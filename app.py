from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Echo transcription backend is running!"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    return {"message": "Transcription endpoint is ready"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
