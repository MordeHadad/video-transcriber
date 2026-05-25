import argparse
import os
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog
from typing import Final, List, Optional
from platformdirs import PlatformDirs

MODEL_PATH: Final[str] = r"D:\Software\ivrit-faster-whisper-v2-d4"
OUTPUT_AUDIO: Final[str] = "output_audio.m4a"
DEFAULT_LANGUAGE: Final[str] = "he"


def get_video_path() -> Optional[str]:
    """Opens a dialog and returns the selected path or None."""
    root = tk.Tk()
    root.withdraw()

    root.update_idletasks()

    print("Opening file dialog...")
    file_path: str = filedialog.askopenfilename(
        parent=root,
        title="Select Video File",
        filetypes=[("Video files", "*.mp4 *.mkv *.mov *.avi"), ("All files", "*.*")],
    )
    root.destroy()
    return file_path if file_path else None


def extract_audio(input_path: str) -> bool:
    """Uses FFmpeg to rip audio. Returns True if successful."""
    print(f"--- Extracting audio from: {os.path.basename(input_path)} ---")

    cmd: List[str] = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vn",
        "-c:a",
        "copy",
        OUTPUT_AUDIO,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error: {e.stderr.decode()}")
        return False


def ffmpeg_available() -> bool:
    """Return True if an ffmpeg executable is available on PATH."""
    return shutil.which("ffmpeg") is not None


def run_whisper(audio_path: str, language: str) -> None:
    """Runs transcription with whisper-ctranslate2 for the specified language on CPU.

    The function ensures transcripts are written into a user data `transcriptions` directory.
    """
    print(f"--- Starting Transcription ({language} / CPU) ---")

    # Ensure the 'transcriptions' subdirectory exists and run whisper from there
    dirs = PlatformDirs("transcriptions")
    base_dir = dirs.user_data_dir
    trans_dir = os.path.dirname(base_dir)
    os.makedirs(trans_dir, exist_ok=True)

    cmd: List[str] = [
        "whisper-ctranslate2",
        audio_path,
        "--model_directory",
        MODEL_PATH,
        "--language",
        language,
        "--device",
        "cpu",
        "--output_dir",
        trans_dir,
    ]

    try:
        # Run whisper with cwd set to the transcriptions subdirectory
        subprocess.run(cmd, check=True, cwd=trans_dir)
        print(f"\n--- Done! Transcripts are in: {trans_dir} ---")
    except subprocess.CalledProcessError as e:
        print(f"Whisper Error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract audio from video and transcribe using whisper-ctranslate2")
    parser.add_argument("--language", "-l", default=DEFAULT_LANGUAGE, help="Language code for transcription (default: he)")
    args = parser.parse_args()

    # Ensure ffmpeg is available before doing any GUI work or processing
    if not ffmpeg_available():
        print("FFmpeg not found in PATH. Please install FFmpeg and ensure it's available in your PATH.")
        return

    video_path: Optional[str] = get_video_path()

    if not video_path:
        print("Selection cancelled.")
        return

    if extract_audio(video_path):
        # Pass an absolute path to whisper so it can access the audio when we cd into the subdirectory
        run_whisper(os.path.abspath(OUTPUT_AUDIO), args.language)

        # Cleanup
        if os.path.exists(OUTPUT_AUDIO):
            os.remove(OUTPUT_AUDIO)
            print("Temp files cleaned.")


if __name__ == "__main__":
    main()
