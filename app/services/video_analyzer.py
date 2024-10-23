import cv2
import numpy as np
import face_recognition
from fer import FER
import speech_recognition as sr
from textblob import TextBlob
import moviepy.editor as mp
import tempfile
import os
import nltk
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

nltk.download('punkt', quiet=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VideoAnalyzer:
    def __init__(self, known_face_image_path):
        self.known_face_encoding = self.load_known_face(known_face_image_path)
        self.emotion_detector = FER(mtcnn=True)
        self.frame_skip = 20

    def load_known_face(self, image_path):
        try:
            known_image = face_recognition.load_image_file(image_path)
            known_encoding = face_recognition.face_encodings(known_image)[0]
            return known_encoding
        except Exception as e:
            logging.error(f"Error loading known face: {e}")
            return None

    def check_single_person(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error("Error opening video file")
            return False, "Error opening video file", 0

        frame_count = 0
        max_faces = 0
        matched_frames = 0
        total_frames = 0
        total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while cap.isOpened() and frame_count < total_frame_count:
            ret, frame = cap.read()
            if not ret:
                break

            try:
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                max_faces = max(max_faces, len(face_locations))

                for face_encoding in face_encodings:
                    match = face_recognition.compare_faces([self.known_face_encoding], face_encoding)[0]
                    if match:
                        matched_frames += 1
                        break

                total_frames += 1
                logging.info(f'Frame {frame_count}: Detected {len(face_locations)} face(s), Match: {match}')
            except Exception as e:
                logging.error(f"Error processing frame {frame_count}: {e}")

            frame_count += self.frame_skip
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)

        cap.release()
        match_percentage = (matched_frames / total_frames) * 100 if total_frames > 0 else 0

        if max_faces == 0:
            return False, "No person detected in the video.", match_percentage
        elif max_faces > 1:
            return False, f"Multiple people ({max_faces}) detected in the video.", match_percentage
        else:
            return True, "Single person detected in the video.", match_percentage

    def process_frame(self, frame):
        try:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            emotion = None
            eye_contact = False
            match = False

            if face_locations:
                match = face_recognition.compare_faces([self.known_face_encoding], face_encodings[0])[0]

                # Facial expression analysis
                emotions = self.emotion_detector.detect_emotions(frame)
                if emotions:
                    dominant_emotion = max(emotions[0]['emotions'].items(), key=lambda x: x[1])[0]
                    emotion = dominant_emotion
                    logging.info(f'Detected emotion: {dominant_emotion}')

                # Eye contact detection
                top, right, bottom, left = face_locations[0]
                face_image = frame[top:bottom, left:right]
                gray_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

                eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml').detectMultiScale(gray_face)
                if len(eyes) >= 2:
                    eye_contact = True
                    logging.info('Eye contact detected')

            return face_locations, emotion, eye_contact, match
        except Exception as e:
            logging.error(f"Error processing frame: {e}")
            return None, None, False, False

    def analyze_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error("Error opening video file")
            return {}, 0, 0

        facial_expressions = []
        eye_contact_frames = 0
        matched_frames = 0
        total_frames = 0
        frames_to_process = []
        total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while cap.isOpened() and total_frames < total_frame_count:
            ret, frame = cap.read()
            if not ret:
                break

            resized_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            frames_to_process.append(resized_frame)
            total_frames += 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames * self.frame_skip)

        cap.release()

        # Process frames in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_frame = {executor.submit(self.process_frame, frame): frame for frame in frames_to_process}
            for future in as_completed(future_to_frame):
                try:
                    result = future.result()
                    if result[0] is not None:
                        _, emotion, eye_contact, match = result
                        if emotion:
                            facial_expressions.append(emotion)
                        if eye_contact:
                            eye_contact_frames += 1
                        if match:
                            matched_frames += 1
                except Exception as e:
                    logging.error(f"Error processing frame: {e}")

        total_processed = len(frames_to_process)
        expression_counts = {emotion: facial_expressions.count(emotion) for emotion in set(facial_expressions)}
        total_expressions = len(facial_expressions)
        expression_percentages = {k: (v / total_expressions) * 100 for k, v in expression_counts.items()} if total_expressions > 0 else {}
        eye_contact_percentage = (eye_contact_frames / total_processed) * 100 if total_processed > 0 else 0
        match_percentage = (matched_frames / total_processed) * 100 if total_processed > 0 else 0

        return expression_percentages, eye_contact_percentage, match_percentage

    def extract_audio(self, video_path):
        video = mp.VideoFileClip(video_path)

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_path = temp_audio.name
        temp_audio.close()

        video.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')
        return temp_audio_path

    def analyze_speech(self, audio_path, audio_length):
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio)
            blob = TextBlob(text)

            sentiment = blob.sentiment.polarity
            word_count = len(blob.words)
            speaking_rate = word_count / (audio_length / 60)

            logging.info(f'Speech sentiment: {sentiment}, speaking rate: {speaking_rate} wpm, word count: {word_count}')

            return sentiment, speaking_rate, word_count
        except sr.UnknownValueError:
            logging.error("Speech recognition could not understand the audio")
            return None, None, None
        except sr.RequestError as e:
            logging.error(f"Could not request results from speech recognition service; {e}")
            return None, None, None

    def analyze(self, video_path):
        if self.known_face_encoding is None:
            return {"error": "Failed to load known face image"}

        # Check if the video contains a single person and if it matches the known face
        is_single_person, message, initial_match_percentage = self.check_single_person(video_path)
        logging.info(message)
        logging.info(f"Initial match percentage: {initial_match_percentage:.2f}%")

        # Video analysis
        expression_percentages, eye_contact_percentage, match_percentage = self.analyze_video(video_path)

        video = mp.VideoFileClip(video_path)
        audio_length = video.audio.duration

        # Extract audio and analyze speech
        temp_audio_path = self.extract_audio(video_path)
        sentiment, speaking_rate, word_count = self.analyze_speech(temp_audio_path, audio_length)

        os.unlink(temp_audio_path)

        if sentiment is not None and speaking_rate is not None:
            confidence_score = (
                eye_contact_percentage * 0.2 +
                expression_percentages.get('happy', 0) * 0.15 +
                expression_percentages.get('neutral', 0) * 0.1 +
                (sentiment + 1) * 50 * 0.15 +
                min(speaking_rate / 150 * 100, 100) * 0.15 +
                match_percentage * 0.25
            )
        else:
            confidence_score = None

        return {
            "facial_expressions": expression_percentages,
            "eye_contact": eye_contact_percentage,
            "speech_sentiment": sentiment,
            "speaking_rate": speaking_rate,
            "word_count": word_count,
            "confidence_score": confidence_score,
            "face_match_percentage": match_percentage
        }

# # Usage
# try:
    
#     video_path ="/home/dell/Downloads/How to say I don't know in Interviews _ Interview Qs 4.mp4"
#     known_face_image_path = "/home/dell/Desktop/channels4_profile.jpg"  # Replace with your actual image path

#     analyzer = VideoAnalyzer(known_face_image_path)
#     analysis_results = analyzer.analyze(video_path)

#     logging.info("Analysis Results:")
#     logging.info(analysis_results)
# except Exception as e:
#     logging.error(f"An error occurred during analysis: {e}")



