from flask import Flask, request, render_template, send_from_directory
import os
from ml_code import process_video  # This imports the process_video function

app = Flask(__name__, static_folder='static', template_folder='templates')

# Define paths for video and audio files
VIDEO_DIR = '/Users/abhishekdhaka/final_year_project_code/user_videos/'
AUDIO_DIR = '/Users/abhishekdhaka/final_year_project_code/'
VIDEO_FILENAME = 'uploaded_video.webm'
AUDIO_FILENAME = 'output.mp3'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return "No file uploaded", 400
    video = request.files['video']
    if video.filename == '':
        return "No file selected", 400
    if video:
        # Define file paths
        video_path = os.path.join(VIDEO_DIR, VIDEO_FILENAME)
        audio_path = os.path.join(AUDIO_DIR, AUDIO_FILENAME)
        
        # Delete existing files if they exist
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Deleted old video: {video_path}")
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"Deleted old audio: {audio_path}")
        
        # Save the new video file
        video.save(video_path)
        print(f"New video saved: {video_path}")
        
        # Process the video to extract or generate audio
        process_video(video_path)  # Assume this generates the audio file at `audio_path`
        
        # Return the audio file URL to the client
        audio_url = f'/audio/{AUDIO_FILENAME}'
        return {"audioUrl": audio_url}

@app.route('/audio/<filename>')
def send_audio(filename):
    audio_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(audio_path):
        return send_from_directory(AUDIO_DIR, filename, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=8000)
