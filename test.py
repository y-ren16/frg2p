import os
from phonemizer.backend import EspeakBackend
# from torch.utils.data import DataLoader
import re

preprocessed_path = './'
filename = 'AD_train.csv'


def process_meta(filename):
    with open(
            os.path.join(preprocessed_path, filename), "r", encoding="utf-8"
    ) as f:
        name = []
        start_ms = []
        end_ms = []
        raw_text = []
        text_0 = []
        text = []
        text_2 = []
        durations = []
        durations_2 = []
        flag = 0
        for line in f.readlines():
            if flag % 2 == 0:
                n, s, e, r, t, d = line.strip("\n").split("|")
                name.append(n)
                start_ms.append(s)
                end_ms.append(e)
                raw_text.append(r)
                text.append(t)
                durations.append(d)
                assert len(t.split(" ")) == len(d[1:].split(" "))
            else:
                n, s, e, t_0, t_2, d_2 = line.strip("\n").split("|")
                text_0.append(t_0)
                text_2.append(t_2)
                durations_2.append(d_2)
                assert n == name[-1]
                assert s == start_ms[-1]
                assert e == end_ms[-1]
                assert len(t_2.split(" ")) == len(d_2[1:].split(" "))
            flag = flag + 1
    return name, start_ms, end_ms, raw_text, text_0, text, text_2, durations, durations_2


class Dataset:
    def __init__(
            self, filename
    ):
        self.name, self.start_ms, self.end_ms, self.raw_text, self.text_0, self.text, \
        self.text_2, self.durations, self.durations_2 = process_meta(filename)


def read_ISC(ISC_path):
    I2C = {}
    C2I = {}
    with open(ISC_path) as f:
        for line in f:
            temp = re.split(r"\s+", line.strip("\n"))
            IPA = temp[0]
            SAMPA = temp[1]
            CPA = temp[2]
            I2C[IPA] = CPA
            C2I[CPA] = IPA
    return I2C, C2I


_whitespace_re = re.compile(r'\s+')


def collapse_whitespace(text):
    return re.sub(_whitespace_re, ' ', text)


if __name__ == "__main__":

    name, start_ms, end_ms, raw_text, text_0, text, text_2, durations, durations_2 = process_meta(filename)
    backend = EspeakBackend(language='fr-fr')
    dataset = Dataset(
        "AD_train.csv"
    )
    ISC_convert_name = "IPA-SAMPA-CPA.txt"

    I2C, C2I = read_ISC(os.path.join(preprocessed_path, ISC_convert_name))
    # print(I2C)
    xy = True
    shot_line = []
    long_line = []
    error_line = [811, 1245, 1471, 2315, 2325, 2581, 2705, 2857, 3017, 3077, 3459, 3557, 3833, 3935, 4219, 4285, 4353,
                  4387, 4463, 4613, 4849]
    for i in range(len(raw_text)):

        if i*2+1 in error_line:
            continue

        # 是否一对一
        assert len(raw_text[i]) == len(re.split(r" ", text[i].strip("\n")))

        phone1b1 = re.split(r" ", text[i].strip("\n"))
        durations1b1 = re.split(r" ", durations[i][1:].strip("\n"))
        assert len(phone1b1) == len(durations1b1)
        # if len(raw_text[i]) != len(phone1b1):
        #     print(i * 2 + 1)

        for j in range(len(phone1b1)):
            # if durations1b1[j] == '0':
            #     print(phone1b1[j])
            #     print(raw_text[i][j])
            alpha = raw_text[i][j]

            if phone1b1[j] == '_':
                # assert durations1b1[j] == '0'
                # if durations1b1[j] != '0':
                #     print(raw_text[i][j])
                #     print(i * 2 + 1)
                if alpha not in shot_line:
                    shot_line.append(alpha)

            if phone1b1[j] == '__':
                if alpha not in long_line:
                    long_line.append(alpha)

            if (phone1b1[j] == '__') & (alpha == '§'):
                assert durations1b1[j] == '130'

            # if alpha == '(':
            #     print(phone1b1[j])
                # print(durations1b1[j])

            # if (alpha == '¬') | (alpha == '#') | (alpha == '«') | (alpha == '»') | (alpha == '~') | (alpha == '[') \
            #         | (alpha == ']') | (alpha == '(') | (alpha == ')'):
            #     assert durations1b1[j] == '0'

            # if alpha == '§':
            #     if xy:
            #         assert phone1b1[j] == '__'
            #         assert durations1b1[j] == '130'
            #         xy = False
            #     else:
            #         assert phone1b1[j] == '_'
            #         assert durations1b1[j] == '0'
            #         xy = True

            if alpha == '§':
                assert (phone1b1[j] == '__') | (phone1b1[j] == '_')
                # print(phone1b1[j])
                # print(raw_text[i][j])

        raw_text[i] = raw_text[i].replace('§', ' ')
        raw_text[i] = raw_text[i].replace('¬', '')
        raw_text[i] = raw_text[i].replace('#', '')

        raw_text[i] = raw_text[i].replace('«', '')
        raw_text[i] = raw_text[i].replace('»', '')
        raw_text[i] = raw_text[i].replace('~', '')
        raw_text[i] = raw_text[i].replace('[', '')
        raw_text[i] = raw_text[i].replace(']', '')
        raw_text[i] = raw_text[i].replace('(', '')
        raw_text[i] = raw_text[i].replace(')', '')

    phonemized = backend.phonemize(raw_text)
    english = []
    error_in_raw = []
    sum_num1 = 0
    sum_num2 = 0
    for i in range(len(raw_text)):

        if i in error_line:
            continue

        ipa = phonemized[i]

        # raw_twxt单词数应该和text_0一致
        word = re.split(r"\s+|-", raw_text[i].strip("\n"))
        while "" in word:
            word.remove("")

        word_text_match = re.findall(r'{(.*?)}', text_0[i], flags=0)
        if len(word) != len(word_text_match):
            # print(raw_text[i])
            error_in_raw.append(i * 2 + 1)
        # assert len(word)==len(word_text_match)

        # word_pho = re.split(r"\s+", ipa.strip("\n"))
        # while "" in word_pho:
        #     word_pho.remove("")

        # if(len(word_pho)!=len(word)):
        #     print(1)
        # assert len(word_pho)==len(word)

        ipa = ipa.replace(' ', '')
        # ipa = ' '.join([i for i in ipa if  i != ' '])
        enfr = re.compile(r'\(en\)(.*?)\(fr\)')
        matchEn = re.search(enfr, ipa, flags=0)
        if matchEn is not None:
            # print(raw_text[i])
            # print(ipa)
            # print('\n')
            eng = matchEn.group(1)
            english.append(eng)
            stop = backend.phonemize([raw_text[i]])
            ########
            ipa = re.sub(enfr, '', ipa, count=0, flags=0)
            # print(ipa)
        iippaa = []
        # ff = True
        for j in ipa:
            # if ff == False:
            #     continue
            # elif j == '̃':
            if j == '̃':
                iippaa[-1] = iippaa[-1] + j
            elif j == 'ː':
                # iippaa[-1] = iippaa[-1] + j 
                continue
            # elif j == '(':
            #     ff == False
            # elif j == ')':
            #     ff == True   
            else:
                iippaa.append(j)
        ipa = ' '.join([i for i in iippaa])

        cpa = text_2[i]
        # t = t.translate({ ord(i): None for i in '_' })
        cpa = cpa.replace('_', '')
        # t = t.replace(' ','')
        cpa = re.sub(_whitespace_re, ' ', cpa).strip()
        phonesI2C = str()
        # for w in re.split(r"\s+", ipa):
        for w in iippaa:
            if w in I2C:
                phonesI2C += I2C[w]
                phonesI2C += ' '
            else:
                # print(w)
                # if(w == 'oː'):
                #     phonesI2C += I2C['o']
                # elif(w == 'yː'):
                #     phonesI2C += I2C['y']
                # elif(w == 'aː'):
                #     phonesI2C += I2C['a']
                # else:  
                if w == 'ɪ':
                    phonesI2C += I2C['i']
                else:
                    raise NameError("ood")
                    # phonesI2C += '* '

        phonesC2I = str()

        for w in re.split(r"\s+", cpa):
            if w in C2I:
                phonesC2I += C2I[w]
                phonesC2I += ' '
            else:
                raise NameError("ood")
                # phonesC2I += '* '

        # print(cpa)
        # print(ipa)
        # print(phonesI2C)
        # print(phonesC2I)
        # from Bio import AlignIO
        # align = AlignIO.read(cpa,phonesI2C)
        from collections import Counter

        A = re.split(r"\s+", cpa)
        B = re.split(r"\s+", phonesI2C)
        C = Counter(A) & Counter(B)
        num = 0
        for ii in C:
            num = num + C[ii]
        sum_num1 = sum_num1 + num
        sum_num2 = sum_num2 + len(A)
        # print (num/(len(A))*100)

    print(sum_num1)
    print(sum_num2)
    print(sum_num1 / sum_num2 * 100)

    # print(english)
    # print(len(english))
    # print(error_in_raw)
    # print(shot_line)
    # print(long_line)
