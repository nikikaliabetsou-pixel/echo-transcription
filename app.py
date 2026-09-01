from flask import Flask, request, jsonify
import os
import requests
import tempfile

app = Flask(__name__)

AUDD_API_URL = "https://api.audd.io/"


@app.route("/")
def home():
    return "Echo transcription backend is running!"


@app.route("/transcribe", methods=["POST"])
def transcribe():

    # Check that a file was uploaded
    if "file" not in request.files:
        return jsonify({
            "error": "No audio file provided"
        }), 400

    audio_file = request.files["file"]

    if audio_file.filename == "":
        return jsonify({
            "error": "No audio file selected"
        }), 400

    # Get AudD API token from Render environment variables
    api_token = os.environ.get("AUDD_API_TOKEN")

    if not api_token:
        return jsonify({
            "error": "AUDD_API_TOKEN is not configured"
        }), 500

    try:
        # Save the recording temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(audio_file.filename)[1]
        ) as temp_file:

            audio_file.save(temp_file.name)
            temp_path = temp_file.name

        # Send recording to AudD
        with open(temp_path, "rb") as audio:

            response = requests.post(
                AUDD_API_URL,
                data={
                    "api_token": api_token,
                    "return": "apple_music,spotify"
                },
                files={
                    "file": audio
                },
                timeout=60
            )

        # Delete temporary recording
        os.remove(temp_path)

        # Check AudD response
        if response.status_code != 200:
            return jsonify({
                "error": "AudD request failed",
                "status_code": response.status_code,
                "details": response.text
            }), 502

        data = response.json()

        # AudD itself returned an error
        if data.get("status") != "success":
            return jsonify({
                "error": "AudD recognition failed",
                "details": data
            }), 502

        result = data.get("result")

        # No song found
        if not result:
            return jsonify({
                "message": "No song identified"
            }), 404

        # Return the useful song information
        return jsonify({
            "message": "Song identified",
            "artist": result.get("artist"),
            "title": result.get("title"),
            "album": result.get("album"),
            "release_date": result.get("release_date"),
            "timecode": result.get("timecode"),
            "song_link": result.get("song_link"),
            "apple_music": result.get("apple_music"),
            "spotify": result.get("spotify")
        })

    except requests.RequestException as e:
        return jsonify({
            "error": "Could not connect to AudD",
            "details": str(e)
        }), 502

    except Exception as e:
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port
    )
