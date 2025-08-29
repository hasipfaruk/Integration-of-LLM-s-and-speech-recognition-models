import os
import subprocess
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from jiwer import wer, compute_measures
from pydub import AudioSegment
from tqdm import tqdm

# Set UTF-8 encoding for subprocess
os.environ["PYTHONIOENCODING"] = "utf-8"

# Dynamic paths based on user's home directory
HOME_DIR = os.path.expanduser("~")
PROJECT_DIR = os.path.join(HOME_DIR, "Desktop", "client1122")
RUSSIAN_TSV = os.path.join(PROJECT_DIR, "CommonVoice", "russian", "validated.tsv")
MONGOLIAN_TSV = os.path.join(PROJECT_DIR, "CommonVoice", "mongolian", "validated.tsv")
RUSSIAN_AUDIO_DIR = os.path.join(PROJECT_DIR, "CommonVoice", "russian", "clips")
MONGOLIAN_AUDIO_DIR = os.path.join(PROJECT_DIR, "CommonVoice", "mongolian", "clips")
WAV_OUTPUT_DIR = os.path.join(PROJECT_DIR, "output_wav")
WHISPER_EXE = os.path.join(PROJECT_DIR, "whisper.cpp", "build", "bin", "Release", "whisper-cli.exe")
MODEL_PATH = os.path.join(PROJECT_DIR, "whisper.cpp", "models", "ggml-base.bin")

# Step 1: Install dependencies
print("Installing Python dependencies...")
subprocess.run("pip install jiwer pydub numpy pandas matplotlib tqdm", shell=True, check=True)

# Step 2: Install Whisper.cpp
print("Installing Whisper.cpp...")
if not os.path.exists(os.path.join(PROJECT_DIR, "whisper.cpp")):
    print("Cloning whisper.cpp repo...")
    os.chdir(PROJECT_DIR)
    subprocess.run("git clone https://github.com/ggerganov/whisper.cpp.git", shell=True, check=True)
else:
    print("whisper.cpp already exists, skipping clone.")

os.chdir(os.path.join(PROJECT_DIR, "whisper.cpp"))
if not os.path.exists("build"):
    os.mkdir("build")
os.chdir("build")

if not os.path.exists(os.path.join("bin", "Release", "whisper-cli.exe")):
    print("Running cmake...")
    subprocess.run("cmake ..", shell=True, check=True)
    print("Building whisper.cpp...")
    subprocess.run("cmake --build . --config Release", shell=True, check=True)
else:
    print("Whisper.cpp already built, skipping.")

os.chdir(PROJECT_DIR)

if not os.path.exists(MODEL_PATH):
    print(f"Model not found at {MODEL_PATH}.")
    print("Please download the multilingual model from:")
    print("https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin")
    print(f"And place it in: {os.path.dirname(MODEL_PATH)}")
    exit(1)
else:
    print("Multilingual model found, proceeding.")

# Step 3: Verify paths
def check_path(path, description):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{description} not found at {path}")
check_path(RUSSIAN_TSV, "Russian TSV")
check_path(MONGOLIAN_TSV, "Mongolian TSV")
check_path(RUSSIAN_AUDIO_DIR, "Russian audio directory")
check_path(MONGOLIAN_AUDIO_DIR, "Mongolian audio directory")

# Step 4: Convert audio to WAV
def convert_to_wav(input_path, output_path):
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_path, format="wav")
    except Exception as e:
        print(f"Failed to convert {input_path}: {e}")

print("Converting audio files to WAV...")
os.makedirs(WAV_OUTPUT_DIR, exist_ok=True)
supported_formats = [".mp3", ".wav", ".ogg"]

for file in os.listdir(RUSSIAN_AUDIO_DIR):
    if any(file.endswith(fmt) for fmt in supported_formats):
        input_path = os.path.join(RUSSIAN_AUDIO_DIR, file)
        output_path = os.path.join(WAV_OUTPUT_DIR, os.path.splitext(file)[0] + ".wav")
        if not os.path.exists(output_path):
            convert_to_wav(input_path, output_path)
        else:
            print(f"Skipped (already exists): {output_path}")

for file in os.listdir(MONGOLIAN_AUDIO_DIR):
    if any(file.endswith(fmt) for fmt in supported_formats):
        input_path = os.path.join(MONGOLIAN_AUDIO_DIR, file)
        output_path = os.path.join(WAV_OUTPUT_DIR, os.path.splitext(file)[0] + ".wav")
        if not os.path.exists(output_path):
            convert_to_wav(input_path, output_path)
        else:
            print(f"Skipped (already exists): {output_path}")

# Step 5: Load metadata
print("Loading metadata...")
russian_tsv = pd.read_csv(RUSSIAN_TSV, sep="\t")
mongolian_tsv = pd.read_csv(MONGOLIAN_TSV, sep="\t")
SAMPLE_SIZE = 10  # Set to the number of files to transcribe (or a large number to process all)
russian_data = russian_tsv[["path", "sentence"]].dropna()
mongolian_data = mongolian_tsv[["path", "sentence"]].dropna()
russian_valid_count = len(russian_data)
mongolian_valid_count = len(mongolian_data)
print(f"Russian valid samples available: {russian_valid_count}")
print(f"Mongolian valid samples available: {mongolian_valid_count}")
if russian_valid_count < SAMPLE_SIZE or mongolian_valid_count < SAMPLE_SIZE:
    print(f"Warning: Requested {SAMPLE_SIZE} samples, but only {russian_valid_count} Russian and {mongolian_valid_count} Mongolian samples are valid.")
russian_data = russian_data.head(SAMPLE_SIZE)
mongolian_data = mongolian_data.head(SAMPLE_SIZE)
print(f"Russian samples to process: {len(russian_data)}")
print(f"Mongolian samples to process: {len(mongolian_data)}")
if mongolian_valid_count < SAMPLE_SIZE:
    print("To process more Mongolian files, add entries to CommonVoice/mongolian/validated.tsv and corresponding audio files to CommonVoice/mongolian/clips.")

# Step 6: Transcribe audio with Whisper.cpp
def transcribe_audio(audio_path, language="en"):
    output_txt = audio_path + ".txt"  # whisper-cli.exe appends .txt to input path
    cmd = f'"{WHISPER_EXE}" -m "{MODEL_PATH}" -f "{audio_path}" -otxt -l {language}'
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, encoding="utf-8")
        if not os.path.exists(output_txt):
            print(f"Output file {output_txt} not created. Command output: {result.stderr}")
            return ""
        with open(output_txt, "r", encoding="utf-8") as f:
            transcription = f.read().strip()
        print(f"Transcription for {audio_path}: {transcription}")
        os.remove(output_txt)  # Clean up temporary file
        return transcription
    except subprocess.CalledProcessError as e:
        print(f"Transcription failed for {audio_path}: {e}")
        print(f"Command output: {e.stderr}")
        return ""
    except FileNotFoundError:
        print(f"Executable {WHISPER_EXE} not found.")
        return ""

print("Transcribing audio files...")
russian_transcriptions = []
mongolian_transcriptions = []
failed_transcriptions = []

for idx, row in tqdm(russian_data.iterrows(), total=len(russian_data), desc="Transcribing Russian"):
    audio_path = os.path.join(WAV_OUTPUT_DIR, os.path.splitext(row["path"])[0] + ".wav")
    if os.path.exists(audio_path):
        transcription = transcribe_audio(audio_path, language="ru")
        russian_transcriptions.append({"audio": row["path"], "reference": row["sentence"], "transcribed": transcription})
    else:
        print(f"Audio file not found: {audio_path}")
        failed_transcriptions.append(row["path"])

for idx, row in tqdm(mongolian_data.iterrows(), total=len(mongolian_data), desc="Transcribing Mongolian"):
    audio_path = os.path.join(WAV_OUTPUT_DIR, os.path.splitext(row["path"])[0] + ".wav")
    if os.path.exists(audio_path):
        transcription = transcribe_audio(audio_path, language="mn")
        mongolian_transcriptions.append({"audio": row["path"], "reference": row["sentence"], "transcribed": transcription})
    else:
        print(f"Audio file not found: {audio_path}")
        failed_transcriptions.append(row["path"])

# Save failed transcriptions
with open(os.path.join(PROJECT_DIR, "failed_transcriptions.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(failed_transcriptions))

# Step 7: Save transcriptions
russian_df = pd.DataFrame(russian_transcriptions)
mongolian_df = pd.DataFrame(mongolian_transcriptions)
russian_df.to_csv(os.path.join(PROJECT_DIR, "russian_transcriptions.csv"), index=False, encoding="utf-8")
mongolian_df.to_csv(os.path.join(PROJECT_DIR, "mongolian_transcriptions.csv"), index=False, encoding="utf-8")

# Step 8: Evaluate WER
print("Evaluating WER...")
russian_df["wer_transcribed"] = russian_df.apply(
    lambda row: wer(row["reference"], row["transcribed"]) if row["transcribed"] else np.nan, axis=1
)
mongolian_df["wer_transcribed"] = mongolian_df.apply(
    lambda row: wer(row["reference"], row["transcribed"]) if row["transcribed"] else np.nan, axis=1
)
print("Russian - Avg WER (Transcribed):", russian_df["wer_transcribed"].mean())
print("Mongolian - Avg WER (Transcribed):", mongolian_df["wer_transcribed"].mean())

# Step 9: Analyze error patterns
def get_error_details(reference, hypothesis):
    if not hypothesis:
        return {"substitutions": 0, "deletions": 0, "insertions": 0}
    measures = compute_measures(reference, hypothesis)
    return {
        "substitutions": measures["substitutions"],
        "deletions": measures["deletions"],
        "insertions": measures["insertions"]
    }

russian_df["error_details"] = russian_df.apply(
    lambda row: get_error_details(row["reference"], row["transcribed"]), axis=1
)
mongolian_df["error_details"] = mongolian_df.apply(
    lambda row: get_error_details(row["reference"], row["transcribed"]), axis=1
)

russian_errors = {
    "substitutions": sum(d["substitutions"] for d in russian_df["error_details"]),
    "deletions": sum(d["deletions"] for d in russian_df["error_details"]),
    "insertions": sum(d["insertions"] for d in russian_df["error_details"])
}
mongolian_errors = {
    "substitutions": sum(d["substitutions"] for d in mongolian_df["error_details"]),
    "deletions": sum(d["deletions"] for d in mongolian_df["error_details"]),
    "insertions": sum(d["insertions"] for d in mongolian_df["error_details"])
}
print("Russian Error Stats:", russian_errors)
print("Mongolian Error Stats:", mongolian_errors)

# Step 10: Visualize results
plt.figure(figsize=(10, 5))
plt.bar(
    ["Russian (Trans)", "Mongolian (Trans)"],
    [russian_df["wer_transcribed"].mean(), mongolian_df["wer_transcribed"].mean()]
)
plt.ylabel("WER")
plt.title("WER Comparison")
plt.savefig(os.path.join(PROJECT_DIR, "wer_comparison.png"))
plt.close()

error_types = ["substitutions", "deletions", "insertions"]
russian_counts = [russian_errors[t] for t in error_types]
mongolian_counts = [mongolian_errors[t] for t in error_types]
plt.figure(figsize=(10, 5))
x = range(len(error_types))
plt.bar(x, russian_counts, width=0.4, label="Russian")
plt.bar([i + 0.4 for i in x], mongolian_counts, width=0.4, label="Mongolian")
plt.xticks([i + 0.2 for i in x], error_types)
plt.ylabel("Count")
plt.title("Error Type Comparison")
plt.legend()
plt.savefig(os.path.join(PROJECT_DIR, "error_type_comparison.png"))
plt.close()

print("Analysis complete. Check 'russian_transcriptions.csv', 'mongolian_transcriptions.csv', 'wer_comparison.png', 'error_type_comparison.png', and 'failed_transcriptions.txt' for results.")
