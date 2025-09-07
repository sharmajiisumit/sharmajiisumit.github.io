from flask import Flask, render_template, request, send_file, redirect, url_for, session
import os
import yt_dlp
import uuid

app = Flask(__name__)
app.secret_key = "supersecret"  # needed for session storage

# absolute path for downloads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "files")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_youtube_audio(url, output_path=DOWNLOAD_FOLDER):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'cookiefile': 'cookies.txt',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        audio_file_name = ydl.prepare_filename(info_dict).replace('.webm', '.mp3')
        return audio_file_name


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        yt_url = request.form.get("yturl")
        if not yt_url:
            return "No YouTube URL provided", 400

        file_path = download_youtube_audio(yt_url)

        # store in session
        session["file_path"] = file_path

        # redirect to download route
        return redirect(url_for("download_file"))

    return render_template("index.html")


@app.route('/download')
def download_file():
    file_path = session.get("file_path")
    if not file_path or not os.path.exists(file_path):
        return "No file available. Please download again.", 400
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
