import os
from tqdm import tqdm
import re
from phonemizer.backend import EspeakBackend
from pydub import AudioSegment
import librosa
from scipy.io import wavfile
import numpy as np

raw_dir = '../All_Data/blizzard_challenge_2023'
in_dir = '../All_Data/Data'
speaker = 'NEB'
# speaker = 'AD'
out_dir = '../G2pData'

os.makedirs(os.path.join(out_dir,speaker), exist_ok=True)
os.makedirs(os.path.join(in_dir,speaker,"wavs"), exist_ok=True)

def main():
    all_text = []
    all_name_new = []
    with open(os.path.join(raw_dir, f'{speaker}_train.csv'), encoding="utf-8") as f:
        line_num = 0
        error_line_num_1 = 0
        error_line_num_2 = 0
        too_long_num = 0
        too_short_num = 0
        for line in tqdm(f):
            line_num = line_num + 1
            always_raw = line_num > 88058 and speaker == "NEB"
            if line_num % 2 != 1 and not always_raw:
                continue
            parts = line.strip().split("|")
            base_name = parts[0]
            start_time_ms = parts[1]
            end_time_ms = parts[2]
            text = parts[3].replace('§', '').replace('#', '').replace('¬', '').replace('~','').replace('»','').replace('«','')
            text = text.lstrip(",.;?!:")
            if len(parts) > 4:
                phone1b1 = re.split(r" ", parts[4].strip("\n"))
                if len(parts[3]) != len(phone1b1):
                    error_line_num_1 += 1
                    continue
            if '{' in text or '}' in text:
                error_line_num_2 += 1
                continue
            ss = int(start_time_ms)
            ee = int(end_time_ms)
            if ee - ss > 10000:
                too_long_num += 1
                continue
            if ee - ss < 100:
                too_short_num += 1
                continue
            base_name_new = f"{base_name}_{start_time_ms}_{end_time_ms}"
            all_text.append(text)
            all_name_new.append(base_name_new)

            wav_path_raw = os.path.join(raw_dir, "{}.wav".format(base_name))
            audio = AudioSegment.from_file(wav_path_raw, "wav")
            audio_clip = audio[ss:ee]
            wav_path = os.path.join(in_dir, speaker, "wavs", "{}.wav".format(base_name_new))
            audio_clip.export(wav_path, format="wav")


    sum_num = len(all_text)
    print("sum_num ", sum_num)
    print("error_line_num_1 ", error_line_num_1)
    print("error_line_num_2 ", error_line_num_2)
    print("too_long_num ", too_long_num)
    print("too_short_num ", too_short_num)
    assert len(all_text) == len(all_name_new)

    backend = EspeakBackend(language='fr-fr', preserve_punctuation=True, language_switch='remove-utterance')

    phonemized = backend.phonemize(all_text)
    print("en-fr num ", sum_num - len(phonemized))

    train_resources = 'train.txt'
    valid_resources = 'valid.txt'
    test_resources = 'test.txt'
    
    with open(os.path.join(out_dir, speaker, train_resources), 'w', encoding='utf-8') as f1:
        for i in range(sum_num):
            if i > 0.8 * sum_num:
                break
            f1.write(f"{all_name_new[i]}.wav|{all_text[i]}|{phonemized[i]}" + "\n")
    with open(os.path.join(out_dir, speaker, valid_resources), 'w', encoding='utf-8') as f2:
        for i in range(sum_num):
            if i < 0.8 * sum_num or i > 0.9 * sum_num:
                continue
            f2.write(f"{all_name_new[i]}.wav|{all_text[i]}|{phonemized[i]}" + "\n")
    with open(os.path.join(out_dir, speaker, test_resources), 'w', encoding='utf-8') as f3:
        for i in range(sum_num):
            if i < 0.9 * sum_num:
                continue
            f3.write(f"{all_name_new[i]}.wav|{all_text[i]}|{phonemized[i]}" + "\n")


if __name__ == "__main__":
    main()