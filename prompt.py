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

#define cospair function

def cos_pair(a,b):
  return dot(a,b.T)/linalg.norm(a)/linalg.norm(b)

# Process the input audio
def process_input_audio(input_audio_path):
    frequency, signal = wavfile.read(input_audio_path)
    slice_length = 1.2  # in seconds
    overlap = 0.2  # in seconds
    slices = np.arange(0, len(signal) / frequency, slice_length - overlap, dtype=np.int)
    input_audio_slices = []

    for start, end in zip(slices[:-1], slices[1:]):
        start_audio = start * frequency
        end_audio = (end + overlap) * frequency
        audio_slice = signal[int(start_audio): int(end_audio)]
        audio_slice = audio_slice.reshape(1, -1)
        audio_slice = torch.tensor(audio_slice).to('cuda')
        audio_slice = classifier.encode_batch(audio_slice)
        audio_slice = audio_slice.detach().cpu().squeeze()
        input_audio_slices.append(audio_slice)

    return input_audio_slices

# Process input audio
input_audio_path = str(args.audio_dir)  # Replace with the path to your input audio
input_audio_slices = process_input_audio(input_audio_path)

# Calculate cosine similarity between the input audio and all audio files in wav_dir
min_mat = []
min_path = []

for le in range(len(list_folder)):
    x = glob.glob(str(list_folder[le]) + '*.wav')

    for _ in range(len(x)):
        try:
            frequency, signal = wavfile.read(x[_])
            audio_slices = process_input_audio(x[_])
            
            matrix_audio = [[0] * len(audio_slices) for i in range(len(input_audio_slices))]
            for i in range(len(input_audio_slices)):
                for j in range(len(audio_slices)):
                    matrix_audio[i][j] = (cos_pair(input_audio_slices[i], audio_slices[j]))
            
            mymin = min([min(r) for r in matrix_audio])
            min_mat.append(mymin)
            min_path.append(x[_])
        except Exception as e:
            print(f"Error processing {x[_]}: {str(e)}")
            os.remove(x[_])
    print(le)

data = []
for i in range(len(min_mat)):
    data.append([min_mat[i], min_path[i]])

data = pd.DataFrame(data)
data.columns = ['MinCos', 'Path']

print("Save csv to " + str(args.file_csv))
my_file = Path(args.file_csv)
try:
    data.to_csv(args.file_csv, index=False)
except Exception as e:
    print(f"Error saving CSV: {str(e)}")