SAMPLING_RATE = 16000

import torch
torch.set_num_threads(1)
from IPython.display import Audio
from pprint import pprint
import glob
import os
import librosa
import argparse
import csv
 
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils


parser = argparse.ArgumentParser()
parser.add_argument('--path_folder_file_wav', type=str)
parser.add_argument('--save_dir', type=str)
parser.add_argument('--path_file_csv', type=str)

args = parser.parse_args()

def vad():
    with open(args.path_file_csv, 'w', encoding = 'UTF8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['path', 'timestamps'])

        for name in glob.glob(args.path_folder_file_wav + '/*.wav'):
            j = 0
            h = 0
            wav = read_audio(name, sampling_rate = SAMPLING_RATE)
            speech_timestamps = get_speech_timestamps(wav, model, threshold=0.5, sampling_rate=SAMPLING_RATE)

            sum = 0
            k = 0   
            speech_timestamps_mini = []
            mini_audio = []

            while(True):
                sum =  sum + speech_timestamps[k]['end'] - speech_timestamps[k]['start'] 
                speech_timestamps_mini.append(speech_timestamps[k])

                if k < len(speech_timestamps)-1:
                    k = k + 1
                    if sum >= 48000:      
                        mini_audio.append(collect_chunks(speech_timestamps_mini, wav))       
                        timestamps = ', '.join(str(item) for item in speech_timestamps_mini)
                        writer.writerow(args.save_dir + '/' + os.path.splitext(os.path.basename(name))[0] + '/' + str(h), timestamps)
                        speech_timestamps_mini.clear()
                        sum = 0
                        h = h + 1
                        continue
                    else:
                        continue
                else:
                    mini_audio.append(collect_chunks(speech_timestamps_mini, wav))
                    timestamps = ', '.join(str(item) for item in speech_timestamps_mini)
                    print(timestamps)
                    writer.writerow(args.save_dir + '/' + os.path.splitext(os.path.basename(name))[0] + '/' + str(h), timestamps)
                    speech_timestamps_mini.clear()
                    sum = 0
                    break

            if not os.path.exists(args.save_dir + '/' + os.path.splitext(os.path.basename(name))[0]):
                os.mkdir(args.save_dir + '/' + os.path.splitext(os.path.basename(name))[0])              
            for i in mini_audio:
               save_audio(args.save_dir + '/' + os.path.splitext(os.path.basename(name))[0] + '/' + str(j) + '.wav', i, sampling_rate = SAMPLING_RATE)
               j = j + 1 

           
def remove_and_rename():
    for i in glob.glob(args.save_dir + '/*' ):
        k = 0
        for j in glob.glob(i + '/*'):
            if librosa.get_duration(filename = j) < 3 or librosa.get_duration(filename = j) > 15:
                os.remove(j)
            else:
                os.rename(j, i + '/audio_' + str(k) + '.wav')
                k= k+1

vad()
remove_and_rename()
        
