import os
import re
import math
import scrapetube
from pytube import YouTube
import moviepy.editor as mpy
from moviepy.video.fx.all import crop
from multiprocessing import Pool

STOCK_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'StockVideo')
TMP_PATH = os.path.join(os.path.dirname(__file__), '.tmp')
FINAL_VIDEO_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'FinalOutput')

def download_youtube_video(video_id):
    return YouTube(f'http://youtube.com/watch?v={video_id}')

def crop_video(input_path, duration):
    clip = mpy.VideoFileClip(input_path)
    (w, h) = clip.size
    num_loops = math.ceil(duration / clip.duration)
    looped_clip = mpy.concatenate_videoclips([clip] * num_loops)
    cropped_clip = crop(looped_clip, width=h * 0.5, height=h, x_center=w / 2, y_center=h / 2)
    return cropped_clip

def composite_video(clip1, clip2_path, length):
    clip2 = mpy.VideoFileClip(clip2_path)
    clip1_width = clip1.size[0]
    clip1_height = clip1.size[1]
    clip = clip1.subclip(0, length)
    clip2_resized = clip2.resize((clip1_width, clip1_width*0.5)).set_position((0,clip1_height/5))
    return mpy.CompositeVideoClip([clip, clip2_resized])

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def split_video_into_parts(final_clip, duration_limit, video_title, output_dir):
    num_parts = math.ceil(final_clip.duration / duration_limit)
    for i in range(num_parts):
        start_time = i * duration_limit
        end_time = min((i + 1) * duration_limit, final_clip.duration)
        part_clip = final_clip.subclip(start_time, end_time)
        filename = f"{video_title}_{i+1}.mp4"
        filename = sanitize_filename(filename)
        output_path = os.path.join(output_dir, filename)
        temp_video_path = os.path.join(TMP_PATH, f"{filename}_TEMP.m4a")
        part_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", remove_temp=True, temp_audiofile=temp_video_path)

def process_video(video, stock_video):
    #for video, stock_video in zip(video, stock_video):
        stock_video_path = os.path.join(STOCK_VIDEO_PATH, stock_video)
        yt_video = download_youtube_video(video['videoId'])
        clip1 = crop_video(stock_video_path, yt_video.length)
        highest_res_url = yt_video.streams.get_highest_resolution().url
        final_clip = composite_video(clip1, highest_res_url, yt_video.length)
        video_title = sanitize_filename(yt_video.title.replace(' ', '_'))
        split_video_into_parts(final_clip, 30, video_title, FINAL_VIDEO_OUTPUT_PATH)

def main():
    videos = scrapetube.get_channel("UC2Z8pGdkGK4Xgbx1yaK5ndA", limit=2, sort_by='newest')
    stock_videos = [file for file in os.listdir(STOCK_VIDEO_PATH) if file.endswith('.mp4')]
    #process_video(videos, stock_videos)

    with Pool() as p:
        p.starmap(process_video, zip(videos, stock_videos))

if __name__ == "__main__":
    main()
