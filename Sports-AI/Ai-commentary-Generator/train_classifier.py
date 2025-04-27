
from utils.youtube_processor import download_youtube_video  
from utils.shot_classification import ShotClassifier
import logging
import os

logging.basicConfig(level=logging.INFO)

# Video URLs and their labels
training_videos = {
    "https://youtube.com/shorts/Q-W__e0YQuM?si=FbwiaMewbxFnusoF": "cover_drive",
    "https://youtu.be/7ZLy1fWm1Mg?si=hGNFbetXOF5cSulA": "flick_shot", 
    "https://youtube.com/shorts/mFsyGkx2wzA?si=hRkIiPzMh_AZ07vy": "helicopter_shot",
    "https://youtube.com/shorts/MUxI8zOA8Z8?si=p8vFDi1Gv-3ivpc1": "sweep_shot",
    "https://youtube.com/shorts/eZfCVOfsAxE?si=jG49X3-p78hcA56_": "pull_shot"
}

def extract_keywords(title):
    """Extract relevant keywords from video title"""
    keywords = ['cover', 'drive', 'flick', 'helicopter', 'sweep', 'pull', 
               'shot', 'batting', 'cricket']
    found_keywords = []
    title_lower = title.lower()
    
    for keyword in keywords:
        if keyword in title_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def train_classifier():
    classifier = ShotClassifier()
    video_paths = {}
    
    # Create training videos directory if it doesn't exist
    os.makedirs("static/training_videos", exist_ok=True)
    
    # Define valid shot types that match commentary templates
    valid_shot_types = {
        'cover_drive': ['cover', 'drive'],
        'pull_shot': ['pull'],
        'flick_shot': ['flick'],
        'sweep_shot': ['sweep'],
        'helicopter_shot': ['helicopter']
    }
    
    # Download videos and process titles
    for url, initial_label in training_videos.items():
        try:
            output_path, detected_shot = download_youtube_video(url, "static/training_videos")
            
            # Get video info to extract title keywords
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', '').lower()
                keywords = extract_keywords(title)
                
            # Use detected shot type or keywords to verify/enhance labeling
            if detected_shot:
                shot_type = detected_shot
            elif keywords:
                # Use keywords to determine shot type
                if 'cover' in keywords or 'drive' in keywords:
                    shot_type = 'cover_drive'
                elif 'flick' in keywords:
                    shot_type = 'flick_shot'
                elif 'helicopter' in keywords:
                    shot_type = 'helicopter_shot'
                elif 'sweep' in keywords:
                    shot_type = 'sweep_shot'
                elif 'pull' in keywords:
                    shot_type = 'pull_shot'
                else:
                    shot_type = initial_label
            else:
                shot_type = initial_label
                
            video_paths[shot_type] = output_path
            logging.info(f"Downloaded video for {shot_type} from {url}")
            logging.info(f"Extracted keywords: {keywords}")
            
        except Exception as e:
            logging.error(f"Error downloading video {url}: {str(e)}")
            continue
    
    # Prepare training data and train classifier
    if video_paths:
        training_data = classifier.prepare_training_data(video_paths)
        classifier.train(training_data)
        logging.info("Classifier training completed successfully")
        logging.info(f"Trained on {len(video_paths)} shot types: {list(video_paths.keys())}")
    else:
        logging.error("No training videos downloaded successfully")

if __name__ == "__main__":
    train_classifier()
