import nltk
nltk.download('wordnet', quiet=True)
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

"""TODO: translation + Wordnet to remove semantic duplicates"""

def translate(s):
    # TODO
    return s

def lemmatizer(s):
    wnl = WordNetLemmatizer()
    lemma = []
    for tags in s:
        lemma.append([wnl.lemmatize(t) for t in tags])
    return lemma

def wordnet(s):
    # TODO
    return s

def vectorizer(s):
    s = translate(s)
    s = lemmatizer(s)
    s = wordnet(s)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([" ".join(doc) for doc in s])
    return X

if __name__ == "__main__":
    tags = ["landscape", "paris", "xyz", "studying", "cats", "bonjour"]
    X = vectorizer([tags])
    assert X.shape[0] == 1
