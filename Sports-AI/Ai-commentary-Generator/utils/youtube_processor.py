
import yt_dlp
import os
import uuid
from pathlib import Path

def download_youtube_video(url, output_dir, max_duration=30):
    """Download YouTube video and return path and extracted shot type"""
    unique_id = str(uuid.uuid4())
    
    # Extract video title from URL
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', '').lower()
    
    # Define shot types to look for
    shot_types = {
        'pull': 'pull_shot',
        'cover': 'cover_drive',
        'flick': 'flick_shot',
        'sweep': 'sweep_shot',
        'hook': 'hook_shot',
        'cut': 'square_cut',
        'drive': 'straight_drive',
        'defense': 'defensive_shot'
    }
    
    # Find shot type in title
    detected_shot = None
    for key, shot_type in shot_types.items():
        if key in title:
            detected_shot = shot_type
            break
            
    output_path = os.path.join(output_dir, f"youtube_{unique_id}.mp4")
    
    ydl_opts = {
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': output_path,
        'noplaylist': True,
        'restrictfilenames': True,
        'merge_output_format': 'mp4',
        'max_duration': max_duration
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path, detected_shot
    except Exception as e:
        raise Exception(f"Error downloading video: {str(e)}")
