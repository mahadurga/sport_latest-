import os
import logging
import ffmpeg

logger = logging.getLogger(__name__)

def align_media(video_path, audio_path, output_path):
    """
    Align video with commentary audio and merge them.
    """
    try:
        # Input video
        video = ffmpeg.input(video_path)

        # Input audio 
        audio = ffmpeg.input(audio_path)

        # Merge video with new audio
        stream = ffmpeg.output(
            video,
            audio,
            output_path,
            vcodec='copy',       # Copy video codec
            acodec='aac',        # Use AAC for audio
            strict='experimental',
            shortest=None,       # End when shortest input ends
            async=1,            # Audio sync method
            vsync=1,            # Video sync method
            avoid_negative_ts='make_zero'
        )

        # Run the ffmpeg command
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return True

    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error occurred: {e.stderr.decode()}")
        return False
    except Exception as e:
        logger.error(f"Error in align_media: {str(e)}")
        return False