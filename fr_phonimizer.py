from phonemizer.backend import EspeakBackend
backend = EspeakBackend(language='fr-fr')
from phonemizer.backend import EspeakMbrolaBackend
backend2 = EspeakMbrolaBackend(language='mb-fr2')
import os
from tqdm import tqdm
import re

in_dir = '../All_Data/Data/BC2023'
speaker = 'NEB'
out_dir = '../G2pData'
os.makedirs(os.path.join(out_dir,speaker), exist_ok=True)
ISC_convert_name = 'IPA-SAMPA-CPA.txt'
def read_ISC(ISC_path):
    I2C = {}
    C2I = {}
    S2I = {}
    S2C = {}
    with open(ISC_path) as f:
        for line in f:
            temp = re.split(r"\s+", line.strip("\n"))
            IPA = temp[0]
            SAMPA = temp[1]
            CPA = temp[2]
            I2C[IPA] = CPA
            C2I[CPA] = IPA
            S2I[SAMPA] = IPA
            S2C[SAMPA] = CPA
    return I2C, C2I, S2I, S2C

def SAMPA2IPA(SAMPA_i):
    I2C, C2I, S2I, S2C = read_ISC(os.path.join('./', ISC_convert_name))
    IPA_now = ''
    skip = False
    for j in range(len(SAMPA_i)):
        if skip == True:
            skip = False
            continue
        if j == len(SAMPA_i)-1:
            IPA_now = IPA_now + S2I[SAMPA_i[j]]
        elif SAMPA_i[j+1] == '~':
            if SAMPA_i[j] == 'o':
                IPA_now = IPA_now + S2I['O~']
            elif SAMPA_i[j] == 'e':
                IPA_now = IPA_now + S2I['E~']
            elif SAMPA_i[j] == 'a':
                IPA_now = IPA_now + S2I['A~']
            else:
                IPA_now = IPA_now + S2I[SAMPA_i[j]+'~']
            skip = True
        else:
            IPA_now = IPA_now + S2I[SAMPA_i[j]]
    return f" {IPA_now} "

def main():
    all_text = []
    all_name_new = []
    with open(os.path.join(in_dir, f'{speaker}_train.csv'), encoding="utf-8") as f:
        line_num = 0
        for line in tqdm(f):
            line_num = line_num + 1
            always_raw = line_num > 88058 and speaker == "NEB"
            if line_num % 2 != 1 and not always_raw:
                continue
            parts = line.strip().split("|")
            base_name = parts[0]
            start_time_ms = parts[1]
            end_time_ms = parts[2]
            text = parts[3].replace('§', '')
            text = text.replace('#', '')
            text = text.replace("¬", "")
            text = text.replace('~',"")
            if len(parts) > 4:
                phone1b1 = re.split(r" ", parts[4].strip("\n"))
                if len(parts[3]) != len(phone1b1):
                    continue
            base_name_new = f"{base_name}_{start_time_ms}_{end_time_ms}"
            all_text.append(text)
            all_name_new.append(base_name_new)
    assert len(all_text) == len(all_name_new)
    sum_num = len(all_text)
    print(sum_num)

    phonemized = backend.phonemize(all_text)

    for j in range(len(phonemized)):
        _en2fr = re.compile(r'\(en\)(.*?)\(fr\)')
        _curly_re = re.compile(r'(.*?)\(en\)(.+?)\(fr\)(.*)')

        while len(phonemized[j]):
            # match_en = _en2fr.match(phonemized[j])
            match_en = re.search(_en2fr, phonemized[j], flags=0)
            if match_en is not None:
                m = _curly_re.match(phonemized[j])
                aa = m.group(1).strip()
                bb = m.group(2).strip()
                cc = m.group(3).strip()
                words_ = re.split('[ ,\',-]', all_text[j].strip())
                words_ = list(filter(None, words_))
                if not len(aa.split()) + len(bb.split()) + len(cc.split()) == len(words_):
                    stop = 1
                # print(all_text[j])
                # print(words_)
                # print(bb)
                # print(phonemized[j])
                correct_word = words_[len(aa.split())]
                correct_phone = backend2.phonemize([correct_word])[0]
                correct_phone = SAMPA2IPA(correct_phone)
                phonemized[j] = aa + correct_phone + cc
                # print(correct_word)
                # print(correct_phone)
            else:
                break



    train_resources = 'train.txt'
    valid_resources = 'valid.txt'
    test_resources = 'test.txt'
    ttv = {'AD': [2293, 2443],'NEB': [60000, 63200]}
    with open(
                os.path.join(out_dir, speaker, train_resources), "w",
            ) as f1:
        for i in range(len(all_text)):
            if (i<int(ttv[speaker][0])):
                f1.write(f'{all_name_new[i]}.wav|{all_text[i]}|{phonemized[i]}' + '\n')
    with open(
                os.path.join(out_dir, speaker, test_resources), "w",
            ) as f1:
        for i in range(len(all_text)):
            if (i>=int(ttv[speaker][0]))&(i<int(ttv[speaker][1])):
                f1.write(f'{all_name_new[i]}.wav|{all_text[i]}|{phonemized[i]}' + '\n')
    with open(
                os.path.join(out_dir, speaker, valid_resources), "w",
            ) as f1:
        for i in range(len(all_text)):
            if (i>=int(ttv[speaker][1])):
                f1.write(f'{all_name_new[i]}.wav|{all_text[i]}|{phonemized[i]}' + '\n')

if __name__ == "__main__":
    main()