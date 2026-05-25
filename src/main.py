import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from typing import Final, List, Optional
from platformdirs import PlatformDirs

# Configuration as Constants
# ty loves Final for things that shouldn't change
MODEL_PATH: Final[str] = r"D:\Software\ivrit-faster-whisper-v2-d4"
OUTPUT_AUDIO: Final[str] = "output_audio.m4a"


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


def run_whisper(audio_path: str) -> None:
    """Runs the Hebrew transcription on CPU but first cds into a 'transcriptions' subdirectory."""
    print("--- Starting Transcription (Hebrew / CPU) ---")

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
        "he",
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
    video_path: Optional[str] = get_video_path()

    if not video_path:
        print("Selection cancelled.")
        return

    if extract_audio(video_path):
        # Pass an absolute path to whisper so it can access the audio when we cd into the subdirectory
        run_whisper(os.path.abspath(OUTPUT_AUDIO))

        # Cleanup
        if os.path.exists(OUTPUT_AUDIO):
            os.remove(OUTPUT_AUDIO)
            print("Temp files cleaned.")


if __name__ == "__main__":
    main()
