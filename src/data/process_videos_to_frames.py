from moviepy import editor as me
import moviepy.video.fx.all as vfx
import os
from PIL import Image
#import tqdm


FRAMES_PATH = './data/quadracopter_sample/frames/dzik25fps_bw'
if not os.path.exists(FRAMES_PATH):
    os.mkdir(FRAMES_PATH)

target_res = (None, 480)
video = me.VideoFileClip('./data/quadracopter_sample/videos/dzik25fps.mp4',
                         target_resolution=target_res, audio=False)
video = video.cutout('00:00:50.0', '00:01:15.0')
video = video.cutout('00:01:31.0', '00:02:17.0')
video = video.fx(vfx.blackwhite)

video.write_images_sequence(f'{FRAMES_PATH}/frame_%06d.png')
original_fps = video.fps

# i = 0
# frames = []
# for frame in video.iter_frames(dtype='uint8', progress_bar=True):
#     img = Image.fromarray(frame)
#     img.save(f'{FRAMES_PATH}/frame_{i:06d}.png')
#     i += 1
#     #frames.append(frame)
