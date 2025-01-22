import sys
#import warnings
#warnings.filterwarnings("ignore")

# Store the original sys.path
# original_sys_path = sys.path.copy()

# # Append your YOLOv5 path
# sys.path.append('/Users/abhishekdhaka/final_year_project_code/yolov5')

# # Do your imports and other operations
# import torch
# from models.yolo import Model

# # Restore the original sys.path
# sys.path = original_sys_path

import cv2
import torch
from pydub import AudioSegment
import speech_recognition as sr
import subprocess
from transformers import pipeline
from moviepy.editor import VideoFileClip
import json
import re
from openai import OpenAI
import os

from gtts import gTTS
from IPython.display import Audio

# Constants and Configuration
# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)



whisper = pipeline("automatic-speech-recognition", model="openai/whisper-small")


API_KEY = os.getenv("SAMBANOVA_API_KEY")
BASE_URL = "https://fast-api.snova.ai/v1"
MODEL = "llama3-70b"

# OpenAI client setup
client = OpenAI(base_url=BASE_URL, api_key='remove_for_privacy')
def video_to_frames(video_path):
    # Capture video
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + fps)  # Skip fps frames
    cap.release()
    return frames

def detect_objects(frames):
    primary_objects = set()
    for frame in frames:
                # Perform inference
        results = model(frame)

        # If no objects were detected, append None or a placeholder
        if results.xyxy[0].shape[0] == 0:
            primary_objects.add(None)
            continue

        # Find the object with the highest confidence
        # results.xyxy[0] - [xmin, ymin, xmax, ymax, confidence, class]
        highest_confidence_idx = results.xyxy[0][:, 4].argmax()
        primary_class_id = int(results.xyxy[0][highest_confidence_idx, 5])
        primary_object_name = model.names[primary_class_id]

        # Append the name of the object with the highest confidence
        primary_objects.add(primary_object_name)
    return primary_objects

def extract_audio_from_video(video_path, output_audio_path):
    # Command should be a list of arguments
    command = ["ffmpeg", "-y","-i", video_path, "-ab", "160k", "-ac", "2", "-ar", "44100", "-vn", output_audio_path]
    try:
        subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Audio extraction completed successfully.")
    except subprocess.CalledProcessError as e:
        # This catches errors from FFmpeg if the command fails
        print("FFmpeg error:", e.stderr)
    except FileNotFoundError:
        # This catches errors if FFmpeg is not installed
        print("FFmpeg is not installed or not found in the system path.")
    except Exception as ex:
        print("Failed to process audio:", str(ex))

def audio_to_text(audio_path):
    transcription = whisper(audio_path)
    return transcription["text"]



video_path = "/Users/abhishekdhaka/final_year_project_code/IMG_7605 2.mp4"



def process_video(video_path):
    # Your processing logic here

    output_audio_path = '/Users/abhishekdhaka/final_year_project_code/output_audio.wav'  # Path for the output WAV audio file
    frames = video_to_frames(video_path)

    detections = detect_objects(frames)

    extract_audio_from_video(video_path, output_audio_path)

    transcript = audio_to_text(output_audio_path)


    print(detections)  # This will print the object detection results
    if 'person' in detections:
        detections.remove('person')


    print(transcript)  # This will print the audio transcript
    detected_objects = list(detections)
    print(detected_objects)

    # Transcribed text from audio
    user_query = transcript
    # Construct a context-rich system message
    if len(detected_objects) != 0:
        detected_objects_list = ', '.join(detected_objects)
        system_message = (
        f"The user is in a room with multiple detected objects: {detected_objects_list}. "
        f"Analyze the user's query to determine if it relates to one or more of these objects. "
        f"If the query is related to a detected object, focus the response specifically on that object, providing detailed and relevant information. "
        f"If the query is unrelated to any detected object, respond appropriately based on the query's content."
    )
    else:
        system_message = (
        "Hello! I'm your AI Assistant, here to help you with any questions or tasks you have. "
        "Since no objects were detected, focus solely on addressing the user's query to the best of your ability."
    )

    # User message from transcribed text
    user_message = {"role": "user", "content": user_query}

    # System initialization message (if not already included)
    init_message = {"role": "system", "content": system_message}

    # Calling the API with the constructed messages
    response = client.chat.completions.create(
        model='Meta-Llama-3.1-8B-Instruct', 
        messages=[init_message, user_message],
        temperature=0.1,
        top_p=0.1
    )

    llm_output=response.choices[0].message.content
    print(llm_output)

    tts = gTTS(llm_output)
    tts.save('output.mp3')
    Audio('output.mp3')
    return output_audio_path