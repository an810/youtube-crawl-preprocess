# -*- coding: utf-8 -*-
"""Tu.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jC2n0ei-cWEfm2CXO2nwzt0qO72H_Fc8
"""

import argparse
import glob
import librosa
import torchaudio
from speechbrain.pretrained import EncoderClassifier
import numpy as np
from scipy.io import wavfile
import numpy as np
from scipy.io.wavfile import write
import torch
import os
from scipy import linalg, mat, dot
import pandas as pd
import seaborn as sns
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--wav_dir', type=str,
                        help='wav_dir')
parser.add_argument('-f', '--file_csv', type=str,   
                        help='file_csv')
parser.add_argument('--audio_dir', type=str, help='audio_dir')
args = parser.parse_args()
print("Load wav from " + str(args.wav_dir))
list_folder = str(args.wav_dir) + "/*/"
print(list_folder)
list_folder = glob.glob(list_folder)

classifier = EncoderClassifier.from_hparams(run_opts={"device":'cuda'}, source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

# Define cospair function
def cos_pair(a, b):
    return dot(a, b.T) / linalg.norm(a) / linalg.norm(b)

# Process the input audio
def process_input_audio(input_audio_path):
    frequency, signal = wavfile.read(input_audio_path)
    audio = signal.reshape(1, -1)
    audio = torch.tensor(audio).to('cuda')
    audio = classifier.encode_batch(audio)
    audio = audio.detach().cpu().squeeze()
    return audio

# Process input audio
input_audio_path = str(args.audio_dir)  # Replace with the path to your input audio
input_audio_embeddings = process_input_audio(input_audio_path)

# Calculate cosine similarity between the input audio and all audio files in wav_dir
cosine_similarities = []

for le in range(len(list_folder)):
    x = glob.glob(str(list_folder[le]) + '*.wav')

    for _ in range(len(x)):
        try:
            frequency, signal = wavfile.read(x[_])
            audio_embeddings = process_input_audio(x[_])
            similarity = cos_pair(input_audio_embeddings, audio_embeddings)
            cosine_similarities.append((x[_], similarity))
        except Exception as e:
            print(f"Error processing {x[_]}: {str(e)}")

data = pd.DataFrame(cosine_similarities, columns=['Path', 'Cosine_Similarity'])

print("Save csv to " + str(args.file_csv))
my_file = Path(args.file_csv)
try:
    data.to_csv(args.file_csv, index=False)
except Exception as e:
    print(f"Error saving CSV: {str(e)}")