import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import tqdm
import pickle as pkl


def load_video_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    frames = []
    ret = True
    while ret:
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames


def find_bboxes_for_video(frames, annotation, misplace_tolerance=0.03, progressbar=lambda iterable, total: iterable):
    length = min(len(frames), len(annotation))
    bboxes = []

    for i, annotation_row in progressbar(enumerate(annotation.itertuples()), total=length):
        if i >= length:
            break

        frame = frames[i].copy()
        bbx = find_bboxes_for_frame(frame, annotation_row.objects, misplace_tolerance)
        bboxes.append(bbx)

    res = annotation.copy()
    res['bounding_boxes'] = bboxes
    return res


def find_bboxes_for_frame(image, boar_points, misplace_tolerance=0.03):
    image_gray = cv2.cvtColor(image.copy(), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(image_gray, 40, 100)
    cont_image, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = [cv2.convexHull(c) for c in contours]

    bboxes = []
    for x, y in boar_points:
        matching_contours = []
        all_contours = []
        for contour in contours:
            dist_from_contour = cv2.pointPolygonTest(contour, (x, y), True)
            if dist_from_contour >= 0:
                matching_contours.append({'contour': contour,
                                          'area': cv2.contourArea(contour),
                                          'distance': dist_from_contour})
            elif abs(dist_from_contour) <= misplace_tolerance * min(image.shape[:2]):
                all_contours.append({'contour': contour,
                                     'area': cv2.contourArea(contour),
                                     'distance': abs(dist_from_contour)})
        if matching_contours:
            contour = min(matching_contours, key=lambda x: x['area'])['contour']
            x, y, w, h = cv2.boundingRect(contour)
            bboxes.append((max(0, x - 1),  # enlarging bbox, with respect to image size
                           max(0, y - 1),
                           min(image.shape[1], x + w + 1),
                           min(image.shape[0], y + h + 1)))
        elif all_contours:
            contour = min(all_contours, key=lambda x: x['distance'])['contour']
            x, y, w, h = cv2.boundingRect(contour)
            bboxes.append((max(0, x - 1),  # enlarging bbox, with respect to image size
                           max(0, y - 1),
                           min(image.shape[1], x + w + 1),
                           min(image.shape[0], y + h + 1)))
        else:
            bboxes.append(None)
    return bboxes


def interpolate_boar_positions(positions: pd.Series):
    assert positions.apply(lambda x: isinstance(x, np.ndarray) or np.isnan(x)).all()
    assert positions.apply(lambda x: x.shape[1] == 2 if isinstance(x, np.ndarray) else True).all()

    temp = positions.copy()
    data = temp._data.interpolate()
    temp._data = data
    return temp.fillna(method='bfill')


def convert_annotation_boar_points_to_np_arrays(annotation_df: pd.DataFrame):
    df = annotation_df.copy()
    df['objects'] = df['objects'].apply(lambda obj: np.asarray([[x, y] for boar_id, x, y in eval(obj)]))
    return df


def prepare_referential_timeseries_df(annotation_df: pd.DataFrame,
                                      datetime_from: datetime,
                                      duration: timedelta,
                                      frame_rate: int):
    referential_steps = []
    for sec in range(duration.seconds + 1):
        dtm = datetime_from + timedelta(seconds=sec)
        for frame_nb in range(frame_rate):
            if (dtm < annotation_df['timestamp'].max()
                    or frame_nb <= annotation_df[annotation_df['timestamp'] == annotation_df['timestamp'].max()]['frame'].max()):
                referential_steps.append((dtm, frame_nb))

        if dtm > annotation_df['timestamp'].max():
            break

    return pd.DataFrame(referential_steps, columns=['timestamp', 'frame'])


def merge_annotation_with_referential_time_df(annotation_df, referential_time_df):
    return referential_time_df.merge(annotation_df, how='left', on=['timestamp', 'frame'])


def prepare_frames_with_drawings(frames, bboxes_annotation, draw_bboxes=True, draw_markers=True,
                                 progressbar=lambda iterable, total: iterable):
    length = min(len(frames), len(bboxes_annotation))
    frames_with_drawings = []

    for i, row in progressbar(enumerate(bboxes_annotation.itertuples()), total=length):
        frame = frames[i].copy()
        if draw_bboxes:
            for bb in row.bounding_boxes:
               if bb:
                    cv2.rectangle(frame, (bb[0], bb[1]), (bb[2], bb[3]), (0, 255, 0))
        if draw_markers:
            for ob in row.objects:
                cv2.drawMarker(frame, (int(ob[0]), int(ob[1])), (0, 0, 255))
        frames_with_drawings.append(frame)
    return frames_with_drawings


def save_video_mp4(frames, filename, frame_rate=20, resolution=(1280, 720)):
    video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, resolution, True)
    for fr in frames:
        video.write(fr)
    video.release()