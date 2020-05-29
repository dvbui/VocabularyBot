import random
import vocs
from nltk.corpus import wordnet

# question data
WORD_LIST = ["./words/VocabularyWorkshopEasy.txt", "./words/VocabularyWorkshopMedium.txt", "./words/VocabularyWorkshopHard.txt"]
SWEAR_WORDS_FILE = "./words/swearWords.txt"
swear_words = {}
master_word_data = [{}, {}, {}]


def init_swear_words_file():
    f = open(SWEAR_WORDS_FILE, "r")
    lines = f.read().split('\n')
    for line in lines:
        swear_words[line.strip().lower()] = ""
    f.close()


def has_swear_words(s):
    for word in swear_words:
        if word in s:
            return True
    return False


# Input: a string
# Output: a string which is one definition of the word
def get_definition(word):
    synset = wordnet.synsets(word)

    if len(synset) == 0:
        return ""

    random_id = random.randint(0, len(synset)-1)
    return synset[random_id].definition()


def get_good_synsets(word):
    synsets = wordnet.synsets(word)
    result = []
    for synset in synsets:
        definition = synset.definition()
        if (not (word in definition)) and (not (has_swear_words(definition))):
            result.append(synset)
    return result


# Input: a string
# Output: a set with format { "string" : definition }
# Each word / definition only appears once
def get_related(word, typ="hyponyms", word_definition=""):
    synset = wordnet.synsets(word)
    res = {}
    def_set = {}

    for s in synset:
        hyponym_sets = s.hyponyms()
        if typ == "synonyms":
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
                if (definition in def_set) or (definition == word_definition):
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


def is_derivative(word):
    return word[-1:] == "s" or word[-2:] == "ed"


def pick_question(word, n=5):
    word = word.lower()
    if has_swear_words(word):
        return None, None
    if is_derivative(word):
        return None, None

    synset = get_good_synsets(word)
    if len(synset) == 0:
        return None, None
    key_def = synset[0].definition()
    res = {word: key_def}
    def_set = {key_def: ""}
    for s in synset:
        set_of_related_synsets = [s.hyponyms(), s.hypernyms(), [s]]
        for related_synsets in set_of_related_synsets:
            for h in related_synsets:
                lemma = h.lemmas()
                definition = h.definition()
                if definition in def_set:
                    continue
                if has_swear_words(definition):
                    continue
                if word in definition:
                    continue

                for w in lemma:
                    related_word = w.name().lower()

                    if word in related_word:
                        continue
                    if related_word in res:
                        continue
                    if is_derivative(related_word):
                        continue
                    if has_swear_words(related_word):
                        continue
                    if not related_word.isalpha():
                        continue
                    if related_word in definition:
                        continue

                    res[related_word] = definition
                    def_set[definition] = ""
                    break

    if len(res) >= n:
        clue_list = [(word, key_def)]
        del res[word]
        for w in res:
            clue_list.append((w, res[w]))
        clue_list = clue_list[0:n]
        clue_list.reverse()
        return word, clue_list
    return None, None


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


def get_antonyms(word):
    antonyms = {}
    for syn in wordnet.synsets(word):
        for lem in syn.lemmas():
            for i in range(len(lem.antonyms())):
                antonyms[lem.antonyms()[i].name()] = ""
    return list(antonyms.keys())


def init_word_list(word_list_index=0):
    new_word_file = open(WORD_LIST[word_list_index], "r")
    for line in new_word_file:
        master_word_data[word_list_index][line.strip()] = {"long": ""}
    new_word_file.close()


def generate_custom_question(difficulty=1, chosen_word=""):
    if len(master_word_data[difficulty-1]) == 0:
        init_word_list(difficulty-1)

    if chosen_word == "":
        word, info = random.choice(list(master_word_data[difficulty-1].items()))
    else:
        word = chosen_word
    info = get_definition(word)
    antonyms = get_antonyms(word)
    chosen_antonym = ""
    if len(antonyms) >= 1:
        chosen_antonym = random.choice(antonyms)

    not_antonyms = {}
    not_antonyms = merge(not_antonyms, get_related(chosen_antonym, "hyponyms"))
    remove = {}
    for key in not_antonyms:
        if key.lower() in word.lower() or word.lower() in key.lower():
            remove[key] = ""

    for key in remove:
        del not_antonyms[key]

    if len(not_antonyms) < 3 or len(antonyms) < 1 or info == "" or info.count("\t") >= 6:
        if chosen_word == "":
            del master_word_data[difficulty-1][word]
            return generate_custom_question(difficulty)
        else:
            return None

    not_antonyms = list(not_antonyms.keys())
    not_antonyms = random.sample(not_antonyms, 3)
    question = "Which of the following words is an antonym for {}?\n".format(word)
    answer = random.randint(1, 4)
    for i in range(0, answer-1):
        question += "{}. {}\n".format(i+1, not_antonyms[i])
    question += "{}. {}\n".format(answer, chosen_antonym)
    for i in range(answer, 4):
        question += "{}. {}\n".format(i+1, not_antonyms[i-1])

    if has_swear_words(question+" "+word):
        if chosen_word == "":
            del master_word_data[difficulty-1][word]
            return generate_custom_question(difficulty)
        else:
            return None

    return question, answer, word

