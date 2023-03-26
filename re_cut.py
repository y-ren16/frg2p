from pydub import AudioSegment
import os
from tqdm import tqdm
import librosa
from scipy.io import wavfile
import numpy as np

data_path = "../Data"
corpus_path = "../Data/AD"
raw_path = "../raw_data"
csv_name = "AD_train.csv"
speaker = "AD"

in_dir = corpus_path
out_dir = raw_path
sampling_rate = 22050
max_wav_value = 32768.0


def main():
    with open(os.path.join(in_dir, csv_name), encoding="utf-8") as f:
        line_num = 0
        for line in tqdm(f):
            line_num = line_num + 1
            if line_num % 2 == 1:
                parts = line.strip().split("|")
                base_name = parts[0]
                start_time_ms = parts[1]
                end_time_ms = parts[2]
                text = parts[3].replace('§', '')
                wav_path_raw = os.path.join(data_path, "{}.wav".format(base_name))
                audio = AudioSegment.from_file(wav_path_raw, "wav")
                audio_clip = audio[int(start_time_ms):int(end_time_ms)]
                base_name_new = base_name + "_" + start_time_ms + "_" + end_time_ms
                wav_path = os.path.join(in_dir, "wavs", "{}.wav".format(base_name_new))
                audio_clip.export(wav_path, format="wav")

                if os.path.exists(wav_path):
                    os.makedirs(os.path.join(out_dir, speaker), exist_ok=True)
                    wav, _ = librosa.load(wav_path, sr=sampling_rate)
                    wav = wav / max(abs(wav)) * max_wav_value
                    wavfile.write(
                        os.path.join(out_dir, speaker, "{}.wav".format(base_name_new)),
                        sampling_rate,
                        wav.astype(np.int16),
                    )
                    with open(
                            os.path.join(out_dir, speaker, "{}.lab".format(base_name_new)),
                            "w",
                    ) as f1:
                        f1.write(text)
            else:
                continue



if __name__ == "__main__":
    main()
