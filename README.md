video-transcriber
==================

Small utility that extracts audio from a video using FFmpeg and runs transcription with whisper-ctranslate2.

Requirements
- Python 3.10+
- FFmpeg must be installed and available on PATH
- Python packages: platformdirs, whisper-ctranslate2

Installation (uv)
1. Ensure you have uv installed (https://astral.sh/uv).
2. From the project root run: `uv install` to create a project environment and install dependencies from pyproject.toml.

Usage
- Edit src/main.py and set MODEL_PATH to your local whisper model directory.
- Run the console script using uv: `uv run transcribe`.
  Alternatively run the module directly with uv: `uv run python src/main.py` or `uv run python -m src.main`.
- The script accepts a --language / -l flag to specify the transcription language (default: he). Example:

  - `uv run transcribe -- --language en`  (run transcribe with language en)

- A file dialog will open to select a video. The script extracts audio to output_audio.m4a, runs whisper-ctranslate2 (CPU), and writes transcripts into a `transcriptions` user data directory. The temporary audio file is removed after completion.

Notes
- The pyproject defines a console script `transcribe` that maps to main:main.
- If FFmpeg is not found on PATH the script will exit with an informative message.
- Adjust MODEL_PATH before running to point to your downloaded whisper model.
