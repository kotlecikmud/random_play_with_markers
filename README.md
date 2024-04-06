# random_play_with_markers.py

## ABOUT

Program that automatically mixes audio using markers saved in a JSON file. Marker values are given in sample count (
amount of audio samples from start).

- **Script Name:** main.py
- **Author:** Filip Pawłowski
- **Contact:** filippawlowski2012@gmail.com

## Usage

1. Provide the input WAV file.
2. Set the total time of mix in samples.
3. Ensure the WAV file has a corresponding JSON file with markers.

## Dependencies

- `numpy`
- `sounddevice`
- `wave`
- `json`
- `random`
- `os`
- `time`

## Installation

1. Install dependencies using pip:
   ```bash
   pip install numpy sounddevice

## Constants

- `version`: Version of the script.
- `WAV_F`: Name of the input audio file (change as per your file name).
- `MIX_LENGHT`: Total time of mix in samples (change as per your requirement).

#### Parameters:

- `wav_f` (str): Path to the WAV file.
- `json_f` (str): Path to the JSON file containing markers.
- `mix_length` (int): Length of the randomized mix in samples.
- `crossfade_enabled` (bool, optional): Enable crossfade between sections. Defaults to True.
