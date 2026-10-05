import re
from collections import Counter

from utils.preprocessing import clean_text, normalize_arabic

STOP_WORDS = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "is", "are", "with", "as",
    "by", "at", "from", "that", "this", "it", "be", "was", "were", "has", "have", "said",
    "says", "after", "over", "new", "will", "not", "his", "her", "its", "but", "about",
    "من", "في", "علي", "الي", "عن", "و", "ان", "او", "هذا", "هذه", "التي", "الذي", "الذين",
    "بعد", "قبل", "مع", "ما", "لا", "كان", "كانت", "قال", "قالت", "يوم", "كل", "بين", "حتي",
    "ذلك", "تلك", "هو", "هي", "له", "لها", "به", "بها", "عند", "منذ", "خلال", "نحو", "ضد",
}


def tokenize(text):
    text = normalize_arabic(clean_text(text)).lower()
    tokens = []
    for w in text.split():
        if re.match(r"^ال.{3,}", w):
            w = w[2:]
        if len(w) > 2 and w not in STOP_WORDS and not w.isdigit():
            tokens.append(w)
    return tokens


def top_terms(texts, n=15):
    uni, bi = Counter(), Counter()
    for t in texts:
        toks = tokenize(t)
        uni.update(toks)
        bi.update(" ".join(p) for p in zip(toks, toks[1:]))

    unigrams = uni.most_common(n)
    bigrams = [(k, v) for k, v in bi.most_common(n) if v >= 2]
    return unigrams, bigrams
