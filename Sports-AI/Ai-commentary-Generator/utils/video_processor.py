import os
import logging
import shutil
from pathlib import Path
import random
import time
import cv2
from flask import session, redirect, url_for
import numpy as np

logger = logging.getLogger(__name__)

def process_video(input_path, output_path, sample_rate=3, unique_id=None, language='en'):  # Process every 3rd frame for better performance
    """
    Process a cricket video using CNN classification and generate commentary.

    Args:
        input_path (str): Path to input video
        output_path (str): Path to save processed video
        sample_rate (int): Process every nth frame (for performance)
        unique_id (str): Unique identifier for the processed video.

    Returns:
        list: Detected events with timestamps and descriptions
    """
    logger.info(f"Processing video: {input_path}")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Video file not found: {input_path}")

    # Read video
    cap = cv2.VideoCapture(input_path)
    frames = []
    frame_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create directory for storing frames
    frames_dir = os.path.join('static/frames', os.path.basename(input_path).split('.')[0])
    os.makedirs(frames_dir, exist_ok=True)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    # Extract frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % sample_rate == 0:
            # Save frame with timestamp
            frame_path = os.path.join(frames_dir, f'frame_{frame_count:04d}.jpg')
            cv2.imwrite(frame_path, frame)
            frames.append(frame)
        frame_count += 1

    cap.release()

    try:
        # Process frames for shot classification
        shot_type = None
        confidence = 0

        if len(frames) > 0:
            # Use the shot classifier to detect the shot type
            from utils.shot_classification import ShotClassifier
            classifier = ShotClassifier()
            shot_type, confidence = classifier.classify_frame_sequence(frames)

            # Map shot types to commentary templates
            shot_type_mapping = {
                'cover_drive': 'cover_drive',
                'pull_shot': 'pull_shot',
                'flick_shot': 'flick_shot',
                'sweep_shot': 'sweep_shot',
                'helicopter_shot': 'helicopter_shot'
            }

            # Get the correct template type
            template_type = shot_type_mapping.get(shot_type, 'generic')

            # Save frames with detected shot label
            for i, frame in enumerate(frames):
                frame_path = os.path.join(frames_dir, f'frame_{i:04d}.jpg')
                cv2.putText(frame, template_type, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imwrite(frame_path, frame)

            # Generate events with proper shot type
            events = []

            # Add shot played event with proper labeling
            events.append({
                'type': 'shot_played',
                'subtype': template_type,
                'confidence': confidence,
                'timestamp': duration * 0.4,
                'frame': frame_count // 2
            })

            # For pull shots, count as a boundary (4) only once
            events.append({
                'type': 'boundary',
                'subtype': 'four',
                'confidence': confidence * 0.9,
                'timestamp': duration * 0.5,
                'frame': frame_count // 2 + 15
            })

            # Store boundary in session
            from flask import session, redirect, url_for
            if 'boundaries' not in session:
                session['boundaries'] = {'four': 1, 'six': 0}
            session['boundaries']['four'] = 1  # Set to 1 for pull shot


        # Get video duration and events with timestamps
        # Generate natural flowing commentary for all events together with language support
        commentary = generate_commentary(events, language=language)

        # Setup paths with absolute paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processed_video_path = os.path.join(base_dir, 'static', 'results', f'processed_{unique_id}.mp4')
        commentary_audio_path = os.path.join(base_dir, 'static', 'results', f'commentary_{unique_id}.mp3')
        final_output_path = os.path.join(base_dir, 'static', 'results', f'final_{unique_id}.mp4')

        # Ensure results directory exists
        os.makedirs(os.path.dirname(processed_video_path), exist_ok=True)

        # First copy the video
        shutil.copy2(input_path, processed_video_path)

        # Generate commentary audio and merge with video
        if os.path.exists(commentary_audio_path):
            logger.info("Merging video with commentary audio...")
            from utils.align_media import align_media
            
            # Ensure audio file is complete before merging
            while True:
                try:
                    with open(commentary_audio_path, 'rb') as f:
                        f.seek(-128, 2)  # Check if file is complete
                    break
                except:
                    time.sleep(0.1)  # Wait for audio generation to complete

            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    success = align_media(processed_video_path, commentary_audio_path, final_output_path)
                    if success:
                        logger.info("Successfully merged video and audio")

                        # Verify the output
                        if os.path.exists(final_output_path) and os.path.getsize(final_output_path) > 0:
                            session['processing_results'] = {
                                'processed_video': processed_video_path,
                                'commentary_audio': commentary_audio_path,
                                'merged_video': final_output_path if os.path.exists(final_output_path) else None,
                                'events': events,
                                'commentary': commentary
                            }
                            return events, final_output_path, commentary

                        logger.warning("Output file verification failed, retrying...")
                    else:
                        logger.warning(f"Merge attempt {retry_count + 1} failed")

                except Exception as e:
                    logger.error(f"Error during merge attempt {retry_count + 1}: {str(e)}")

                retry_count += 1

            logger.warning("Failed to merge audio after all retries, returning video without commentary")

        logger.info(f"Video processed and saved to {processed_video_path}")
        session['processing_results'] = {
            'processed_video': processed_video_path,
            'commentary_audio': commentary_audio_path,
            'merged_video': final_output_path if os.path.exists(final_output_path) else None,
            'events': events,
            'commentary': commentary
        }
        return events, processed_video_path, commentary

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise

def generate_simulated_events():
    """
    Generate simulated cricket events for demo purposes.

    Returns:
        list: Simulated events
    """
    events = []

    # Define some common events
    event_types = {
        'boundary': ['four', 'six'],
        'wicket': ['bowled', 'caught', 'lbw', 'run_out'],
        'shot_played': [
            'straight drive', 'cover drive', 'cut shot', 'pull shot', 
            'hook shot', 'sweep shot', 'defensive shot', 'flick shot'
        ]
    }

    # Define standard match length (in seconds)
    match_length = 300  # 5 minutes for demo

    # Generate random events
    for _ in range(random.randint(4, 8)):
        timestamp = random.uniform(10, match_length - 10)
        events.append({
            'type': 'shot_played',
            'subtype': random.choice(event_types['shot_played']),
            'confidence': random.uniform(0.5, 0.95),
            'timestamp': timestamp,
            'frame': int(timestamp * 30)
        })

    # Sort events by timestamp
    events.sort(key=lambda x: x['timestamp'])

    return events

def generate_commentary(events, language='en'):
    """Generates commentary based on events and video duration."""
    from utils.commentary_generator import COMMENTARY_TEMPLATES, TRANSITIONS

    commentary_parts = []
    if len(events) > 0:
        for event in events:
            if event['type'] == 'shot_played':
                shot_desc = random.choice(COMMENTARY_TEMPLATES["shot_played"].get(
                    event.get('subtype', 'generic'), 
                    COMMENTARY_TEMPLATES["shot_played"]["generic"]
                ))
                transition = random.choice(TRANSITIONS.get(language, TRANSITIONS['en']))
                commentary_parts.append(f"{transition}{shot_desc}")
            elif event['type'] == 'boundary':
                boundary_type = event.get('subtype', 'four')
                boundary_desc = random.choice(COMMENTARY_TEMPLATES["boundary"][boundary_type])
                commentary_parts.append(boundary_desc)

    # Return default commentary if no events detected
    if not commentary_parts:
        default_commentary = {
            'en': "The batsman takes guard as the tension builds in the stadium.",
            'hi': "बल्लेबाज गार्ड लेते हैं और स्टेडियम में तनाव बढ़ता है।",
            'ta': "பேட்ஸ்மேன் கார்டு எடுக்கிறார், மைதானத்தில் பதற்றம் அதிகரிக்கிறது।"
        }
        return default_commentary.get(language, default_commentary['en'])

    return ' '.join(commentary_parts)