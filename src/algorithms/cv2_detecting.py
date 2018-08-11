from imutils import contours
from skimage import measure
import numpy as np
import imutils
import cv2
from scipy.spatial import distance as dist


class ContourDetector:

    def __init__(self):
        pass

    def detect_animal_contours(self, image, min_pixels=20):
        thresh = self.threshold_dilate(image)
        mask = self.connected_component_analysis(thresh, min_pixels)
        contours = self.find_contours(mask)
        return contours

    def threshold_dilate(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]
        dilate = cv2.dilate(thresh, None, iterations=2)
        erode = cv2.erode(dilate, None, iterations=1)
        return erode

    def connected_component_analysis(self, image, min_pixels=20):
        labels = measure.label(image, neighbors=8, background=0)
        mask = np.zeros(image.shape, dtype="uint8")

        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue

            # otherwise, construct the label mask and count the
            # number of pixels
            labelMask = np.zeros(image.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)

            # if the number of pixels in the component is sufficiently
            # large, then add it to our mask of "large blobs"
            if numPixels >= min_pixels:
                mask = cv2.add(mask, labelMask)

        return mask

    def find_contours(self, mask):
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        if cnts:
            cnts = contours.sort_contours(cnts)[0]

        return cnts


class ContourFilter:

    def __init__(self,
                 hard_threshold=100,
                 soft_threshold=95.0,
                 common_area_threshold=0.25,
                 shape_ratio_threshold=2):

        self.hard_threshold = hard_threshold
        self.soft_threshold = soft_threshold
        self.common_area_threshold = common_area_threshold
        self.shape_ratio_threshold = shape_ratio_threshold

        self.last_frame = np.empty(0)
        self.last_bboxes = []

    @staticmethod
    def common_area(box_1, box_2):  # returns None if rectangles don't intersect
        dx = min(box_1[1] + box_1[3], box_2[1] + box_2[3]) - max(box_1[1], box_2[1])
        dy = min(box_1[0] + box_1[2], box_2[0] + box_2[2]) - max(box_1[0], box_2[0])
        if (dx >= 0) and (dy >= 0):
            return dx * dy
        else:
            return 0

    @staticmethod
    def area(a):  # returns None if rectangles don't intersect
        return a[2] * a[3]

    @staticmethod
    def ellipse(contour):
        i
        focal_point_1, focal_point_2, _ = cv2.fitEllipse(contour)
        return dist.euclidean(focal_point_1, focal_point_2)

    @staticmethod
    def is_shape_ratio_ok(image, contour, threshold):
        if len(contour) < 5:
            return True
        (x,y), (major_axis_length, minor_axis_lenght), angle = cv2.fitEllipse(contour)
        return major_axis_length/minor_axis_lenght < threshold

    def filter_contours(self, image, contours):
        left_contours = []
        left_bboxes = []
        for contour in contours:
            bbox = cv2.boundingRect(contour)
            bbox_content = image[bbox[1]:bbox[1] + bbox[3],
                                 bbox[0]:bbox[0] + bbox[2]]

            if not ContourFilter.is_shape_ratio_ok(image, contour, self.shape_ratio_threshold):
                continue

            if bbox_content.mean() >= self.hard_threshold:
                left_contours.append(contour)
                left_bboxes.append(bbox)
            elif bbox_content.mean() >= self.soft_threshold:
                if not self.last_bboxes:
                    left_contours.append(contour)
                    left_bboxes.append(bbox)
                common_areas = [self.common_area(bbox, bb) for bb in self.last_bboxes]
                area = self.area(bbox)
                if any(comm_area / area >= self.common_area_threshold for comm_area in common_areas):
                    left_contours.append(contour)
                    left_bboxes.append(bbox)

        self.last_bboxes = left_bboxes
        return left_contours


def draw_bboxes(image, contours):
    image2 = np.copy(image)
    for contour in contours:
        bbox = cv2.boundingRect(contour)
        cv2.rectangle(image2,
                      (bbox[0], bbox[1]),
                      (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                      (0, 255, 0))
    return image2