import os
from phonemizer.backend import EspeakBackend
backend = EspeakBackend(language='fr-fr')
preprocessed_path = './'
filename = 'french-samples.txt'
def process_meta(filename):
    franch_text = []
    with open(
        os.path.join(preprocessed_path, filename), "r", encoding="utf-8"
    ) as f:
        for line in f.readlines():  
            franch_text.append(line.strip("\n"))
    return franch_text
franch_text = process_meta(filename)
phonemized = backend.phonemize(franch_text)
print(franch_text)
print(phonemized)