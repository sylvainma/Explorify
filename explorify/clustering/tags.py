from sklearn.feature_extraction.text import TfidfVectorizer

"""TODO: translation + Wordnet to remove semantic duplicates"""

def translate(s):
    # TODO
    return s

def wordnet(s):
    # TODO
    return s

def vectorizer(s):
    s = translate(s)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(s)
    return X

if __name__ == "__main__":
    tags = ["landscape", "paris", "xyz", "studying", "bonjour"]
    X = vectorizer([" ".join(tags)])
    assert X.shape[0] == 1
