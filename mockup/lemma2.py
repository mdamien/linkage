from nltk.stem.wordnet import WordNetLemmatizer

lmtzr = WordNetLemmatizer()

p = 'je suis une ptite souris. I\'m a smallest cats'.split(' ')

for x in p:
    print(x, lmtzr.lemmatize(x))
