import os
from tqdm import tqdm
import re
from phonemizer.backend import EspeakBackend
backend = EspeakBackend(language='fr-fr', preserve_punctuation=True)
from phonemizer.backend import EspeakMbrolaBackend
backend2 = EspeakMbrolaBackend(language='mb-fr2')
import numpy as np

# raw_dir = "2023-FH1_submission_directory/NEB_test/NEB_test.csv"
# out_dir = "2023-FH1_submission_directory/NEB_test/NEB_test.txt"
# raw_dir = "2023-FH1_submission_directory/NEB_test_homos/NEB_test_homos.csv"
# out_dir = "2023-FH1_submission_directory/NEB_test_homos/NEB_test_homos.txt"
# raw_dir = "2023-FH1_submission_directory/NEB_test_list/NEB_test_list.csv"
# out_dir = "2023-FH1_submission_directory/NEB_test_list/NEB_test_list.txt"
# raw_dir = "2023-FH1_submission_directory/NEB_test_sus/NEB_test_sus.csv"
# out_dir = "2023-FH1_submission_directory/NEB_test_sus/NEB_test_sus.txt"
raw_dir = "2023-FH1_submission_directory/NEB_test_par/NEB_raw_test_par.txt"
out_dir = "2023-FH1_submission_directory/NEB_test_par/NEB_test_par.txt"

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
    name = []
    raw_text = []
    with open(raw_dir, encoding="utf-8") as f:
        for line in tqdm(f):
            parts = line.strip().split("|")
            text = parts[1].replace('§', '').replace('#', '').replace('¬', '').replace('~','').replace('»','').replace('«','')
            text = text.lstrip(",.;?!:")
            name.append(parts[0])
            raw_text.append(text)

    assert len(name) == len(raw_text)
    sum_num = len(name)
    print("sum_num ", sum_num)

    phonemized = backend.phonemize(raw_text)

    error = []

    for i in range(sum_num):
        _en2fr = re.compile(r'\(en\)(.*?)\(fr\)')
        _curly_re = re.compile(r'(.*?)\(en\)(.+?)\(fr\)(.*)')
        match_en = re.search(_en2fr, phonemized[i], flags=0)
        while len(phonemized[i]):
            # match_en = _en2fr.match(phonemized[j])
            match_en = re.search(_en2fr, phonemized[i], flags=0)
            if match_en is not None:
                m = _curly_re.match(phonemized[i])
                aa = m.group(1).strip()
                bb = m.group(2).strip()
                cc = m.group(3).strip()
                words_ = re.split('[ ,-,.,\",!,?]', raw_text[i].strip())
                words_ = list(filter(None, words_))
                aaa = list(filter(None, re.split('[ ,-,.,\",!,?]', aa.strip())))
                ccc = list(filter(None, re.split('[ ,-,.,\",!,?]', cc.strip())))
                bbb = list(filter(None, re.split('[ ,-,.,\",!,?]', bb.strip())))
                if not len(aaa) + len(bbb) + len(ccc) == len(words_):
                    print(raw_text[i])
                    print(phonemized[i])
                    error.append(name[i])
                    phonemized[i] = ""
                    continue
                # print(all_text[j])
                # print(words_)
                # print(bb)
                # print(phonemized[j])
                correct_word = words_[len(aaa)]
                correct_phone = backend2.phonemize([correct_word])[0]
                correct_phone = SAMPA2IPA(correct_phone)
                phonemized[i] = aa + correct_phone + cc
                print(correct_word)
                print(correct_phone)
            else:
                break

    with open(out_dir, "w", encoding="utf-8") as f:
        for i in range(sum_num):
            if name[i] in error:
                f.write(f"{name[i]}|{raw_text[i]}|***" + "\n")
                continue
            f.write(f"{name[i]}|{raw_text[i]}|{phonemized[i]}" + "\n")




if __name__ == "__main__":
    main()