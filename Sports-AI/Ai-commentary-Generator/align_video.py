
from utils.align_media import align_media
import os

def main():
    # Example paths
    video_path = os.path.join('static', 'uploads', 'input_video.mp4')
    audio_path = os.path.join('static', 'results', 'commentary.mp3')
    output_path = os.path.join('static', 'results', 'aligned_output.mp4')
    
    # Align the media
    success = align_media(video_path, audio_path, output_path)
    if success:
        print("Video and audio aligned successfully!")
    else:
        print("Error during alignment")

if __name__ == "__main__":
    main()
