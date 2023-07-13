import os
import math
import scrapetube
from pytube import YouTube
import moviepy.editor as mpy
from moviepy.video.fx.all import crop

def download_youtube_video(video_id, output_dir):
    yt_video = YouTube(f'http://youtube.com/watch?v={video_id}')
    return yt_video.streams.get_highest_resolution().download(output_dir), yt_video

def crop_video(input_path, output_path):
    clip = mpy.VideoFileClip(input_path)
    (w, h) = clip.size
    cropped_clip = crop(clip, width=h*0.5, height=h, x_center=w/2, y_center=h/2)
    cropped_clip.write_videofile(output_path)
    return mpy.VideoFileClip(output_path)

def composite_video(clip1, clip2_path, length):
    clip2 = mpy.VideoFileClip(clip2_path)
    clip1_width = clip1.size[0]
    clip1_height = clip1.size[1]
    clip = clip1.subclip(0, length)
    clip2_resized = clip2.resize((clip1_width, clip1_width*0.5)).set_position((0,clip1_height/5))
    return mpy.CompositeVideoClip([clip, clip2_resized])

def split_video_into_parts(final_clip, duration_limit, video_title, output_dir):
    num_parts = math.ceil(final_clip.duration / duration_limit)
    for i in range(num_parts):
        start_time = i * duration_limit
        end_time = min((i + 1) * duration_limit, final_clip.duration)
        part_clip = final_clip.subclip(start_time, end_time)
        filename = f"{video_title}_{i+1}.mp4"
        output_path = os.path.join(output_dir, filename)
        part_clip.write_videofile(output_path)

def main():
    videos = scrapetube.get_channel("UC2Z8pGdkGK4Xgbx1yaK5ndA", limit=2, sort_by='newest')
    clip1 = crop_video("C:\\Users\\Patryk\\Downloads\\stockvideos\\stock.mp4", "new_clip.mp4")
    output_dir = "C:\\Users\\Patryk\\Downloads\\finalOutput"

    for video in videos:
        vid = video['videoId']
        clip2_path, yt_video = download_youtube_video(vid, r'C:\Users\Patryk\Downloads\VideoOutput')
        final_clip = composite_video(clip1, clip2_path, yt_video.length)
        video_title = yt_video.title.replace(' ', '_').replace('/', '_')
        split_video_into_parts(final_clip, 30, video_title, output_dir)

if __name__ == "__main__":
    main()
