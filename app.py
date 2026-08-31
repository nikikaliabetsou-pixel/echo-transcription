from flask import Flask, request, jsonify
from basic_pitch.inference import predict

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
        return jsonify({"error": "No file selected"}), 400

    file_path = "/tmp/input_audio"
    audio_file.save(file_path)

    try:
        model_output, midi_data, note_events = predict(file_path)

        midi_path = "/tmp/output.mid"
        midi_data.write(midi_path)

        return jsonify({
            "message": "Transcription successful",
            "midi_file": midi_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
