# make sure your downloaded the model with "python -m spacy download en"

import spacy
from langdetect import detect_langs

AVAILABLE_MODELS = 'en', 'fr', 'de'

lang = 'en'
langs = detect_langs(str(doc))
for lang in langs:
    lang = lang.split(':')[0]
    if lang in AVAILABLE_MODELS:
        break

nlp = spacy.load(lang)
doc = nlp("La répétition : lecture et enjeux dans la pensée kierkegaardienne, constitution de la subjectivité")

for token in doc:
    print(token, token.lemma, token.lemma_)
