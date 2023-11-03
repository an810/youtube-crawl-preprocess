
# YouTube data pipeline for crawling and pre-processing

## Dependencies

Requirements:
```
pip install -r requirements.txt
```

## Data Crawling

Crawl MP4 video from Youtube and convert to WAV:
```
python crawl.py --url_playlist=<URL to YouTube playlist> --save_dir=<Directory folder to save WAV>
```

## Data Pre-processing

First we split the audio files into smaller files using Silero Voice Activity Detection (VAD):
```
python silero-VAD.py --folder_file_wav=<Path to WAV folder> --save_dir=<Directory folder to save new WAV>
```
After performing VAD, compute the cosine similarity of audio pairs:
```
python cosine_pair.py --wav_dir=<Path to VAD-ed WAV folder> --file_csv=<CSV to save results>
```
After getting the similarity scores, irrelevant / noisy audio files have to be removed. For each language, we have to listen to some audio files to define a threshold.
All audio files having the threshold value below the pre-defined threshold will be removed: 
```
python remove.py --file_csv=<CSV path> --thresh_hold=<Threshold value from 0.2 to 0.5>
```
After running the above command, the irrelevant audio files in the VAD-ed wav folder will be removed.
