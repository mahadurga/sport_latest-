
import numpy as np
import cv2
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

CRICKET_SHOTS = [
    "cover_drive", "pull_shot", "flick_shot", 
    "sweep_shot", "helicopter_shot"
]

class ShotClassifier:
    def __init__(self):
        self.templates = self._load_templates()
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, frame):
        """Extract features from a frame"""
        try:
            # Convert to grayscale and resize for consistent features
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_resized = cv2.resize(frame_gray, (128, 128))  # Increased resolution
            
            # Extract HOG features with adjusted parameters
            win_size = (128, 128)
            block_size = (16, 16)
            block_stride = (8, 8)
            cell_size = (8, 8)
            nbins = 9
            hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, nbins)
            hog_features = hog.compute(frame_resized)
            
            # Add edge features using Canny with adaptive thresholds
            median = np.median(frame_resized)
            lower = int(max(0, (1.0 - 0.33) * median))
            upper = int(min(255, (1.0 + 0.33) * median))
            edges = cv2.Canny(frame_resized, lower, upper)
            edge_features = edges.flatten() / 255.0
            
            # Add intensity histogram features
            hist_features = cv2.calcHist([frame_resized], [0], None, [32], [0, 256]).flatten()
            hist_features = hist_features / hist_features.sum()  # Normalize
            
            # Combine all features
            features = np.concatenate([
                hog_features.flatten(),
                edge_features,
                hist_features
            ])
            
            return features
        except Exception as e:
            logger.error(f"Error in feature extraction: {str(e)}")
            return None
        
    def train(self, frames_dict):
        """Train classifier on labeled frames"""
        X = []  # Features
        y = []  # Labels
        
        # Process each shot type and its frames
        for shot_type, frames in frames_dict.items():
            frame_count = 0
            for frame in frames:
                try:
                    features = self.extract_features(frame)
                    if features is not None:
                        X.append(features)
                        y.append(shot_type)
                        frame_count += 1
                except Exception as e:
                    logger.error(f"Error extracting features: {str(e)}")
                    continue
            logger.info(f"Processed {frame_count} frames for {shot_type}")
                
        if not X or not y:
            logger.error("No valid training data extracted")
            return False
                
        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        logger.info(f"Shot classifier trained successfully with {len(X)} samples")
        return True
        
    def prepare_training_data(self, video_paths):
        """Prepare training data from labeled videos"""
        training_data = {}
        for shot_type, video_path in video_paths.items():
            frames = []
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            cap.release()
            training_data[shot_type] = frames
            logger.info(f"Extracted {len(frames)} frames for {shot_type}")
        return training_data
            
    def _load_templates(self):
        """Load shot templates from GIF files"""
        template_files = {
            'pull_shot': 'pull.gif',
            'cover_drive': 'cover.gif',
            'flick_shot': 'flick.gif',
            'sweep_shot': 'sweep.gif',
            'helicopter_shot': 'helicopter.gif'
        }
        
        templates = {}
        for shot_type, filename in template_files.items():
            try:
                capture = cv2.VideoCapture(filename)
                ret, frame = capture.read()
                if ret:
                    frame = cv2.resize(frame, (64, 64))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    templates[shot_type] = frame
                capture.release()
            except Exception as e:
                logger.error(f"Error loading template {filename}: {str(e)}")
                
        return templates

    def classify_frame_sequence(self, frames):
        """Classify cricket shot from a sequence of frames"""
        if not frames:
            return "unknown", 0.0
            
        if not self.is_trained:
            logger.warning("Model not trained, falling back to template matching")
            return self._template_matching_classify(frames)
            
        predictions = []
        confidences = []
        
        for frame in frames:
            try:
                # Extract features
                features = self.extract_features(frame)
                features_scaled = self.scaler.transform(features.reshape(1, -1))
                
                # Get prediction and confidence
                prediction = self.model.predict(features_scaled)[0]
                proba = self.model.predict_proba(features_scaled)[0]
                confidence = np.max(proba)
                
                predictions.append(prediction)
                confidences.append(confidence)
                
            except Exception as e:
                logger.error(f"Error in shot classification: {str(e)}")
                continue
                
        if not predictions:
            return "unknown", 0.0
            
        # Get most common prediction with weighted confidence
        prediction_counts = {}
        prediction_confidences = {}
        
        for pred, conf in zip(predictions, confidences):
            if pred not in prediction_counts:
                prediction_counts[pred] = 0
                prediction_confidences[pred] = []
            prediction_counts[pred] += 1
            prediction_confidences[pred].append(conf)
            
        # Weight by both frequency and confidence
        weighted_scores = {}
        for pred in prediction_counts:
            count_weight = prediction_counts[pred] / len(predictions)
            conf_weight = np.mean(prediction_confidences[pred])
            weighted_scores[pred] = count_weight * conf_weight
            
        best_shot = max(weighted_scores.items(), key=lambda x: x[1])[0]
        best_confidence = weighted_scores[best_shot]
        
        return best_shot, float(best_confidence)
        
    def _template_matching_classify(self, frames):
        """Legacy template matching classification as fallback"""
        if not self.templates:
            return "unknown", 0.0
            
        best_shot = None
        best_confidence = 0.0
        
        for frame in frames:
            try:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_resized = cv2.resize(frame_gray, (64, 64))
                
                for shot_type, template in self.templates.items():
                    result = cv2.matchTemplate(frame_resized, template, cv2.TM_CCOEFF_NORMED)
                    similarity = np.max(result)
                    
                    if similarity > best_confidence:
                        best_confidence = similarity
                        best_shot = shot_type
                        
            except Exception as e:
                logger.error(f"Error in template matching: {str(e)}")
                continue
                
        if not best_shot:
            return "unknown", 0.0
            
        return best_shot, float(best_confidence)

def classify_shot(frame_sequence):
    """Wrapper function for shot classification"""
    classifier = ShotClassifier()
    return classifier.classify_frame_sequence(frame_sequence)
