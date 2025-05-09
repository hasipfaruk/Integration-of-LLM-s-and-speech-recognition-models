

## What This Script Does

This guide helps you run a Python script (`main.py`) that transcribes Russian and Mongolian audio files from the Common Voice dataset into text. The script:
- Converts audio files to a format suitable for transcription.
- Transcribes one audio file each for Russian and Mongolian (you can increase this number if you have more files).
- Compares the transcriptions to the original text to measure accuracy (using Word Error Rate, or WER).
- Saves results to CSV files and creates charts to visualize accuracy.

## What You Need
- **Computer**: Windows 10 or 11 with at least 4GB RAM and 10GB free disk space.
- **Internet**: To download tools and data.
- **Basic Skills**: Ability to run commands in Windows PowerShell and follow file download instructions.

## Step-by-Step Setup

### 1. Install Required Software
You need to install a few tools to run the script. Follow these steps carefully.

#### Install Python
1. Download Python 3.10 or later from [python.org](https://www.python.org/downloads/).
2. Run the installer and check **"Add Python to PATH"** during installation.
3. Open PowerShell (press `Win + S`, type `PowerShell`, and press Enter).
4. Verify Python is installed by typing:
   ```powershell
   python --version
   ```
   You should see something like `Python 3.10.0` or higher.

#### Install Git
1. Download Git from [git-scm.com](https://git-scm.com/download/win).
2. Run the installer and accept the default settings.
3. In PowerShell, verify Git by typing:
   ```powershell
   git --version
   ```
   You should see something like `git version 2.30.0.windows.1`.

#### Install CMake
1. Download CMake from [cmake.org](https://cmake.org/download/) (choose the Windows installer).
2. Run the installer and select **"Add CMake to the system PATH for all users"**.
3. In PowerShell, verify CMake by typing:
   ```powershell
   cmake --version
   ```
   You should see something like `cmake version 3.20.0`.

#### Install Visual Studio Build Tools
1. Download the Visual Studio Build Tools from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. Run the installer and select **"Desktop development with C++"** (this includes tools needed to build Whisper.cpp).
3. Install and restart your computer if prompted.

### 2. Set Up Your Project Folder
1. Create a project folder on your Desktop named `client1122`:
   ```powershell
   mkdir $HOME\Desktop\client1122
   ```
2. Inside `client1122`, you need:
   - A folder named `CommonVoice` with subfolders `russian` and `mongolian`.
   - A script file named `main.py`.
   - A model file (`ggml-base.bin`) that you’ll download later.

### 3. Set Up Common Voice Data
The script needs audio files and metadata (TSV files) for Russian and Mongolian.

#### Option 1: Use Provided Data
If you received a `CommonVoice` folder from your provider:
1. Copy the `CommonVoice` folder to `$HOME\Desktop\client1122`.
2. Ensure it has:
   - `russian\validated.tsv` and `russian\clips` (with audio files like `common_voice_ru_*.mp3`).
   - `mongolian\validated.tsv` and `mongolian\clips` (with at least `common_voice_mn_40158159.mp3`).
3. Verify:
   ```powershell
   dir $HOME\Desktop\client1122\CommonVoice\russian
   dir $HOME\Desktop\client1122\CommonVoice\mongolian
   ```

#### Option 2: Download Data
If you don’t have the data:
1. Visit [Common Voice](https://commonvoice.mozilla.org/en/datasets).
2. Download the Russian and Mongolian datasets.
3. Extract the datasets to:
   - `$HOME\Desktop\client1122\CommonVoice\russian`
   - `$HOME\Desktop\client1122\CommonVoice\mongolian`
4. Ensure each has a `validated.tsv` file and a `clips` folder with audio files.
5. Verify:
   ```powershell
   dir $HOME\Desktop\client1122\CommonVoice\russian\validated.tsv
   dir $HOME\Desktop\client1122\CommonVoice\mongolian\validated.tsv
   ```

### 4. Download the Whisper.cpp Model
1. Download the multilingual model file `ggml-base.bin` from [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin). It’s about 148 MB.
2. Place `ggml-base.bin` in `$HOME\Desktop\client1122\whisper.cpp\models`.
   - If the `whisper.cpp\models` folder doesn’t exist, create it after running the script once (it will create the `whisper.cpp` folder).
   - Or create it manually:
     ```powershell
     mkdir $HOME\Desktop\client1122\whisper.cpp\models
     ```
3. Verify the file is in place:
   ```powershell
   dir $HOME\Desktop\client1122\whisper.cpp\models\ggml-base.bin
   ```

### 5. Save the Script
1. Save the `main.py` script provided by your provider to `$HOME\Desktop\client1122\main.py`.
   - Open Notepad, paste the script, and save as `main.py` (ensure "Save as type" is "All Files").
   - Or download the script file if provided.
2. Verify the script is saved:
   ```powershell
   dir $HOME\Desktop\client1122\main.py
   ```

### 6. Run the Script
1. Open PowerShell:
   - Press `Win + S`, type `PowerShell`, and press Enter.
2. Navigate to your project folder:
   ```powershell
   cd $HOME\Desktop\client1122
   ```
3. Run the script:
   ```powershell
   python main.py
   ```
4. Wait for the script to finish. It will:
   - Install required Python libraries.
   - Download and build Whisper.cpp.
   - Convert audio files to WAV format.
   - Transcribe one Russian and one Mongolian audio file.
   - Save results and create charts.

### 7. Check the Results
After the script finishes, check these files in `$HOME\Desktop\client1122`:
- **russian_transcriptions.csv**: Shows the audio file name, original text, transcribed text, and WER for the Russian sample.
- **mongolian_transcriptions.csv**: Same for the Mongolian sample.
- **wer_comparison.png**: A chart comparing transcription accuracy (WER).
- **error_type_comparison.png**: A chart showing types of errors (substitutions, deletions, insertions).
- **failed_transcriptions.txt**: Lists any audio files that couldn’t be transcribed (should be empty).

To view the CSV files:
1. Open them in Microsoft Excel, or
2. Use PowerShell:
   ```powershell
   type $HOME\Desktop\client1122\russian_transcriptions.csv
   type $HOME\Desktop\client1122\mongolian_transcriptions.csv
   ```

To view the charts:
1. Open `wer_comparison.png` and `error_type_comparison.png` with any image viewer (e.g., Photos app).

### 8. Understanding the Output
- **Console Output**: The script shows:
  - `Russian samples loaded: 1`
  - `Mongolian samples loaded: 1`
  - `Transcription for ...: [transcribed text]`
  - `Russian - Avg WER (Transcribed): [number]`
  - `Mongolian - Avg WER (Transcribed): [number]`
  - WER measures accuracy (lower is better; 0 is perfect, 1 or higher means errors).
- **CSV Files**: Compare `reference` (original text) and `transcribed` (script’s output) columns to check accuracy.
- **Charts**: Show accuracy and error types visually.

## Processing More Audio Files
The script is set to transcribe one audio file per language because your Mongolian dataset has only one file. To process more:
1. Ensure your `CommonVoice\russian\clips` and `CommonVoice\mongolian\clips` folders have additional audio files.
2. Verify `validated.tsv` files list these audio files with corresponding text in the `sentence` column.
3. Edit `main.py` and change:
   ```python
   SAMPLE_SIZE = 10  # Set to the number of files you want to transcribe
   ```
4. Re-run the script.

## Troubleshooting Common Issues

### 1. "Model not found at .../whisper.cpp/models/ggml-base.bin"
- **Problem**: The script can’t find `ggml-base.bin`.
- **Solution**:
  - Download `ggml-base.bin` from [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin).
  - Place it in `$HOME\Desktop\client1122\whisper.cpp\models`.
  - Verify:
    ```powershell
    dir $HOME\Desktop\client1122\whisper.cpp\models\ggml-base.bin
    ```

### 2. "Russian TSV not found" or "Mongolian TSV not found"
- **Problem**: The script can’t find `validated.tsv`.
- **Solution**:
  - Ensure `validated.tsv` exists in:
    - `$HOME\Desktop\client1122\CommonVoice\russian`
    - `$HOME\Desktop\client1122\CommonVoice\mongolian`
  - Verify:
    ```powershell
    dir $HOME\Desktop\client1122\CommonVoice\russian\validated.tsv
    dir $HOME\Desktop\client1122\CommonVoice\mongolian\validated.tsv
    ```
  - If missing, download from [Common Voice](https://commonvoice.mozilla.org/en/datasets).

### 3. "Audio file not found"
- **Problem**: The script can’t find audio files listed in `validated.tsv`.
- **Solution**:
  - Ensure audio files exist in:
    - `$HOME\Desktop\client1122\CommonVoice\russian\clips`
    - `$HOME\Desktop\client1122\CommonVoice\mongolian\clips`
  - Verify:
    ```powershell
    dir $HOME\Desktop\client1122\CommonVoice\mongolian\clips\common_voice_mn_40158159.mp3
    ```
  - If missing, redownload from [Common Voice](https://commonvoice.mozilla.org/en/datasets).

### 4. Poor Transcription Accuracy (High WER)
- **Problem**: WER values are high (e.g., 1.0 or more), meaning transcriptions are inaccurate.
- **Solution**:
  - Check the CSV files to compare `reference` and `transcribed` text.
  - Test a single transcription:
    ```powershell
    cd $HOME\Desktop\client1122
    .\whisper.cpp\build\bin\Release\whisper-cli.exe -m .\whisper.cpp\models\ggml-base.bin -f .\output_wav\common_voice_mn_40158159.wav -otxt -l mn
    type .\output_wav\common_voice_mn_40158159.wav.txt
    ```
  - If accuracy is poor, download `ggml-medium.bin` (1.5 GB) from [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin).
  - Update `main.py`:
    ```python
    MODEL_PATH = os.path.join(PROJECT_DIR, "whisper.cpp", "models", "ggml-medium.bin")
    ```

### 5. "cmake is not recognized"
- **Problem**: CMake is not installed or not in the PATH.
- **Solution**:
  - Reinstall CMake from [cmake.org](https://cmake.org/download/) and select "Add CMake to the system PATH for all users".
  - Verify:
    ```powershell
    cmake --version
    ```

### 6. Script Stops or Shows Errors
- **Problem**: The script crashes or shows unexpected errors.
- **Solution**:
  - Copy the error message from PowerShell.
  - Contact your provider with the error details and console output.
  - Try running the script again after checking all files and paths.

## Support
If you encounter issues:
- Contact your provider with:
  - The full PowerShell output.
  - Contents of `russian_transcriptions.csv` and `mongolian_transcriptions.csv`.
  - A description of the problem.
- Include screenshots of error messages if possible.

## Notes
- The script processes one audio file per language. To process more, update `SAMPLE_SIZE` in `main.py` after adding more data.
- Transcription accuracy depends on audio quality. If results are poor, consider using `ggml-medium.bin`.
- Keep your project folder organized to avoid missing files.