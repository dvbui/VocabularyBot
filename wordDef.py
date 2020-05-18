import random
from nltk.corpus import wordnet


# Input: a string
# Output: a string which is one definition of the word
def get_definition(word):
    synset = wordnet.synsets(word)

    if len(synset) == 0:
        return ""

    id = random.randint(0, len(synset)-1)
    return synset[id].definition()


# Input: a string
# Output: a set with format { "string" : definition }
# Each word / definition only appears once
def get_related(word, typ="hyponyms", definition=""):
    synset = wordnet.synsets(word)
    res = {}
    def_set = {}

    for s in synset:
        hyponym_sets = s.hyponyms()
        if typ == "synonyms":
            if s.definition() == definition:
                continue
            hyponym_sets = [s]
        if typ == "hypernyms":
            hyponym_sets = s.hypernyms()
        for h in hyponym_sets:
            lemma = h.lemmas()
            if len(lemma) == 0:
                continue
            w = lemma[0].name().lower()

            if w == word.lower():
                continue
            if w in res:
                continue

            if w.isalpha():
                definition = h.definition()
                if definition in def_set:
                    continue
                res[w] = definition
                def_set[definition] = ""

    return res


def merge(fi, se):
    def_set = {}
    for w in fi:
        def_set[fi[w]] = ""
    for w in se:
        if w in fi:
            continue
        if se[w] in def_set:
            continue
        fi[w] = se[w]
    return fi


def choose_questions(word, n=4, definition=""):
    s = get_related(word, "hyponyms", definition)
    typ = ["synonyms", "hypernyms"]
    for t in typ:
        if len(s) >= n:
            break
        s = merge(s, get_related(word, t, definition))

    if len(s) < n:
        return None

    best = {}
    not_best = {}
    for w in s:
        if word in w:
            not_best[w] = s[w]
            continue
        if word in s[w]:
            not_best[w] = s[w]
            continue
        best[w] = s[w]

    res = {}
    ke = random.sample(best.keys(), min(n, len(best))) + random.sample(not_best.keys(), n - min(n, len(best)))
    for k in ke:
        res[k] = s[k]

    return res


def get_similarity(first_word, first_definition, second_word):
    first_synset = wordnet.synsets(first_word)
    second_synset = wordnet.synsets(second_word)
    best_similarity = 0
    for first_set in first_synset:
        if not (first_definition == "" or first_definition == first_set.definition()):
            continue
        for second_set in second_synset:
            similarity = first_set.wup_similarity(second_set)
            if not (similarity is None):
                best_similarity = max(best_similarity, similarity)

    return best_similarity

