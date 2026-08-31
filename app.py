from flask import Flask, request, jsonify
import os
import tempfile
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

app = Flask(__name__)

@app.route("/")
def home():
    return "Echo transcription backend is running!"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["file"]

    if audio_file.filename == "":
        return jsonify({"error": "No audio file selected"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, audio_file.filename)
        output_dir = os.path.join(temp_dir, "output")

        os.makedirs(output_dir, exist_ok=True)
        audio_file.save(input_path)

        predict_and_save(
            [input_path],
            output_dir,
            True,
            False,
            False,
            False,
            ICASSP_2022_MODEL_PATH
        )

        files = os.listdir(output_dir)

        return jsonify({
            "message": "Transcription complete",
            "files": files
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
