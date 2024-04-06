"""
---ABOUT---
Program that automatically mixes audio using markers saved in json file. Markers values are given in sample count (amount of audio samples from start)

script name:    random_play_with_markers.py
author:         Filip Pawłowski
contact:        filippawlowski2012@gmail.com
"""
import os
import time
import wave
import json
import random
import numpy as np
import sounddevice as sd

# CONSTANTS
__version__ = "00.01.00.00"
WAV_F = "example.wav"  # INPUT NAME OF THE AUDIO FILE HERE
MIX_LENGHT = 44100 * 60  # INPUT TOTAL TIME OF MIX HERE [samples], for 44100Hz sampling rate 1 second = 44100 samples


def find_matching_json(wav_f):
    """Find matching JSON file for the given WAV file."""
    base_name = os.path.splitext(wav_f)[0]
    json_file = base_name + '.json'
    if os.path.isfile(json_file):
        return json_file
    else:
        return None


def play_wav_with_markers(wav_f, json_f, mix_length, crossfade_enabled=True):
    """
    Play the WAV file with markers.

    Args:
        wav_f (str): Path to the WAV file.
        json_f (str): Path to the JSON file containing markers.
        mix_length (int): Length of the randomized mix in samples.
        crossfade_enabled (bool, optional): Enable crossfade between sections. Defaults to True.
    """
    # Load JSON file
    with open(json_f, 'r') as f:
        json_data = json.load(f)

    # Load WAV file
    with wave.open(wav_f, 'rb') as wf:
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        nchannels = wf.getnchannels()

        # Generate crossfade samples
        crossfade_samples = int(10 * framerate)
        crossfade = np.linspace(0, 1, crossfade_samples)

        # Create markers list
        markers = [(marker['sample'], marker['section']) for marker in json_data['markers']]
        markers.sort()

        # Define the sections for infinite mixing (exclude first and last section)
        infinite_mixing_sections = markers[1:-2]

        # Play the first section
        first_section_start_sample, first_section_name = markers[0]
        first_section_end_sample = markers[1][0]
        print(f"Playing first section: {first_section_name}, sample: {first_section_start_sample}")

        total_first_section_samples = first_section_end_sample - first_section_start_sample

        wf.setpos(first_section_start_sample)
        data_chunk = wf.readframes(total_first_section_samples)
        audio_data = np.frombuffer(data_chunk, dtype=np.int16)

        # Play audio for the first section
        sd.play(audio_data.reshape(-1, nchannels), samplerate=framerate)
        time.sleep((len(audio_data) / nchannels) / framerate)

        # Randomly play sections (excluding first and last)
        round = 0
        prev_section_idx = 1  # change to None if using line 88
        current_sample_count = 0

        # update mix lenght by subtracting total_first_section_samples
        mix_length -= total_first_section_samples

        while current_sample_count < mix_length:
            round += 1
            print(f"\n{round=}\
            \n{int(mix_length-current_sample_count)=}, (seconds left: {int((mix_length - current_sample_count) / framerate)})")  # display samples until end

            # Print the current and next sections
            # if prev_section_idx is not None:
            prev_section = infinite_mixing_sections[prev_section_idx]
            prev_start_sample, prev_section_name = prev_section
            print(f"Next section: {prev_section_name}, sample: {prev_start_sample}")

            # Randomly choose the next section for infinite mixing
            next_section_idx = random.choice([i for i in range(len(infinite_mixing_sections)) if i != prev_section_idx])
            next_section = infinite_mixing_sections[next_section_idx]
            next_start_sample, next_section_name = next_section
            print(f"Current section: {next_section_name}, sample: {next_start_sample}")

            # Read audio data for the next section
            wf.setpos(next_start_sample)
            next_end_sample = markers[markers.index(next_section) + 1][0] if next_section != markers[-2] else nframes
            data_chunk = wf.readframes(next_end_sample - next_start_sample)
            audio_data = np.frombuffer(data_chunk, dtype=np.int16)

            # Apply crossfade if enabled and necessary
            if crossfade_enabled and prev_section_idx is not None:
                fade_out_end = min(nframes, next_start_sample + crossfade_samples)

                # Read audio data for the previous section
                prev_start_sample, _ = infinite_mixing_sections[prev_section_idx - 1]
                wf.setpos(prev_start_sample)
                data_chunk = wf.readframes(fade_out_end - prev_start_sample)
                prev_audio_data = np.frombuffer(data_chunk, dtype=np.int16)

                # Apply fade out
                prev_audio_data[-crossfade_samples:] *= (1 - crossfade)

                # Apply fade in
                audio_data[:crossfade_samples] *= crossfade

                # Mix audio data
                audio_data = np.concatenate((prev_audio_data, audio_data[crossfade_samples:]))

            # Calculate the length of the next section and update the current sample count
            section_length = len(audio_data) / nchannels
            current_sample_count += section_length

            # Play audio with correct parameters
            sd.play(audio_data.reshape(-1, nchannels), samplerate=framerate)

            # Wait for the section to finish
            time.sleep(section_length / framerate)

            # Update previous section index
            prev_section_idx = next_section_idx

        # Play the last section
        last_section_start_sample, last_section_name = markers[-1]  # Get the second to last marker
        last_section_end_sample = nframes  # End of the WAV file
        print(f"Playing last section: {last_section_name}, sample: {last_section_start_sample}")

        wf.setpos(last_section_start_sample)
        data_chunk = wf.readframes(last_section_end_sample - last_section_start_sample)
        audio_data = np.frombuffer(data_chunk, dtype=np.int16)

        # Play audio for the last section
        sd.play(audio_data.reshape(-1, nchannels), samplerate=framerate)
        time.sleep((len(audio_data) / nchannels) / framerate)


if __name__ == '__main__':
    if not os.path.isfile(WAV_F):
        input("WAV file not found.\nexit >>>")
        exit(1)

    # Find the matching JSON file
    json_file = find_matching_json(WAV_F)

    # clear terminal window
    os.system('cls')

    # display header
    print(f"Scripts name: {os.path.basename(__file__)}\
    \nVersion: {__version__}\
    \nAUTOPLAY\n\n")

    # Check if JSON file exists
    if json_file:
        # Call the function with the WAV and JSON files
        play_wav_with_markers(WAV_F, json_file, mix_length=MIX_LENGHT, crossfade_enabled=False)
    else:
        input("Matching JSON file not found for the WAV file.\
        \nPlease place json file with markers inside, named _THE_SAME_ as WAV file\
        \nexit >>>")
        exit(1)
