from flask import Flask, request, render_template, send_from_directory
import os
from ml_code import process_video  # This imports the process_video function

app = Flask(__name__)

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
        # video_path = os.path.join('/tmp', video.filename)
        # video.save(video_path)
        # output_audio_path = process_video(video_path)  # Call your ML function
        # output_audio_path='/Users/abhishekdhaka/final_year_project_code/output.mp3'
        directory = '/Users/abhishekdhaka/final_year_project_code'
        filename = 'output.mp3'
        #return send_from_directory(directory=os.path.dirname(output_audio_path), filename=os.path.basename(output_audio_path), as_attachment=True)
        if os.path.exists(os.path.join(directory, filename)):
            return send_from_directory(directory, filename, as_attachment=True)
        else:
            return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=8011)
