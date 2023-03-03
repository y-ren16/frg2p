import os
from tqdm import tqdm
from phonemizer.backend import EspeakBackend
import re
import requests
from phonemizer import phonemize
from phonemizer.separator import Separator

in_dir = '../All_Data/Data/BC2023'
# speaker = 'NEB'
speaker = 'AD'
out_dir = '../G2pData'
os.makedirs(out_dir, exist_ok=True)


def main():
    all_text = []
    all_name_new = []
    with open(os.path.join(in_dir, speaker + '_train.csv'), encoding="utf-8") as f:
        line_num = 0
        for line in tqdm(f):
            line_num = line_num + 1
            always_raw = (line_num > 88058) & (speaker == "NEB")
            if (line_num % 2 == 1) | always_raw:
                parts = line.strip().split("|")
                base_name = parts[0]
                start_time_ms = parts[1]
                end_time_ms = parts[2]
                text = parts[3].replace('§', '')
                text = text.replace('#', '')
                if len(parts) > 4:
                    phone1b1 = re.split(r" ", parts[4].strip("\n"))
                    if len(parts[3]) != len(phone1b1):
                        continue
                base_name_new = base_name + "_" + start_time_ms + "_" + end_time_ms
                all_text.append(text)
                all_name_new.append(base_name_new)
            else:
                continue

    assert len(all_text) == len(all_name_new)
    sum_num = len(all_text)
    print(sum_num)

    language_type = ['fr-fr', 'mb-fr1', 'mb-fr2', 'mb-fr3', 'mb-fr4', 'mb-fr5', 'mb-fr6', 'mb-fr7']
    backend_type = ['espeak', 'espeak-mbrola', 'espeak-mbrola', 'espeak-mbrola', 'espeak-mbrola',
                    'espeak-mbrola', 'espeak-mbrola', 'espeak-mbrola']
    english = []
    for i in range(len(language_type)):
        # backend = EspeakBackend(language=BT)
        # phonemized = backend.phonemize(all_text)
        phonemized = phonemize(
            all_text,
            language=language_type[i],
            backend=backend_type[i],
            separator=Separator(phone=None, word=' ', syllable='|'),
            strip=True,
            preserve_punctuation=True,
            njobs=4)
        en_line = []
        with open(
                os.path.join(out_dir, speaker + '_' + language_type[i] + '.txt'), "w",
        ) as f1:
            for j in tqdm(range(sum_num)):
                en2fr = re.compile(r'\(en\)(.*?)\(fr\)')
                match_en = re.search(en2fr, phonemized[j], flags=0)
                if match_en is not None:
                    # print(phonemized[j])
                    en_line.append(str(j) + '|' + all_text[j] + '|' + phonemized[j])
                f1.write(all_text[j] + '|' + phonemized[j] + '\n')
        english.append(en_line)
    with open(
            os.path.join(out_dir, speaker + '_english.txt'), "w",
    ) as f1:
        for i in range(len(language_type)):
            f1.write('**********' + language_type[i] + '**********\n')
            for j in range(len(english[i])):
                f1.write(english[i][j] + '\n')


if __name__ == "__main__":
    main()
