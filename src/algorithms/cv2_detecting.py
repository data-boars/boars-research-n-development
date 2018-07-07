from imutils import contours
from skimage import measure
import numpy as np
import imutils
import cv2


def detect_animals(image, min_pixels=20):
    thresh = threshold_dilate(image)
    mask = connected_component_analysis(thresh, min_pixels)
    bboxes = find_bboxes(mask)
    return bboxes


def threshold_dilate(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]
    dilate = cv2.dilate(thresh, None, iterations=2)
    erode = cv2.erode(dilate, None, iterations=1)
    return erode


def connected_component_analysis(image, min_pixels=20):
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


def find_bboxes(mask):
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = contours.sort_contours(cnts)[0]

    bboxes = []
    # loop over the contours
    for (i, c) in enumerate(cnts):
        # draw the bright spot on the image
        (x, y, w, h) = cv2.boundingRect(c)
        bboxes.append((x,y,w,h))

    return bboxes


def draw_bboxes(image, bboxes):
    image2 = np.copy(image)
    for bbox in bboxes:
        cv2.rectangle(image2,
                      (bbox[0], bbox[1]),
                      (bbox[0]+bbox[2], bbox[1]+bbox[3]),
                      (0, 255, 0))
    return image2
