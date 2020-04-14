import nltk
nltk.download("wordnet", quiet=True)
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from googletrans import Translator
from sklearn.feature_extraction.text import TfidfVectorizer


class TagVectorizer():
    """Handle translation, lemmatization, synset reduction and vectorization of tags"""
    def __init__(self, translations=False):
        self.wnl = WordNetLemmatizer()
        self.tsl = Translator()
        self.tsl_cache = {}
        self.translations = translations

    def translate(self, s):
        translations = []
        for tags in s:
            translation = []
            for t in tags:
                t_ = self.tsl_cache.get(t.lower(), None)
                if t_ is None:
                    try:
                        t_ = self.tsl.translate(t, dest="en").text
                    except Exception:
                        t_ = t
                    finally:
                        self.tsl_cache[t.lower()] = t_
                translation.append(t_)
            translations.append(translation)
        return translations

    def lemmatizer(self, s):
        lemma = []
        for tags in s:
            lemma.append([self.wnl.lemmatize(t.lower()) for t in tags])
        return lemma

    def synsets(self, s):
        synsets = []
        for tags in s:
            synset = []
            for t in tags:
                synons = wordnet.synsets(t)
                if len(synons) > 0:
                    hypernyms = synons[0].hypernyms()
                    if len(hypernyms) > 0:
                        synset.append(hypernyms[0].name())
                    else:
                        synset.append(synons[0].name())
                else:
                    synset.append(t)
            synsets.append(synset)
        return synsets

    def distinct(self, s):
        return [list(set(tags)) for tags in s]

    def vectorizer(self, s):
        s = self.translate(s) if self.translations else s
        s = self.lemmatizer(s)
        s = self.synsets(s)
        s = self.distinct(s)
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform([" ".join(doc) for doc in s])
        return X


if __name__ == "__main__":
    s = [["landscape", "Paris", "paris", "arcdetriomphe",
            "XYZ", "studying", "cats", "bonjour", 
            "Arc de Triomphe", "Atlanta", "bonjour"]]
    tv = TagVectorizer(translations=True)
    s_ = tv.synsets(tv.lemmatizer(tv.translate(s)))
    print(tv.distinct(s_))
    X = tv.vectorizer(s)
    assert X.shape[0] == 1
