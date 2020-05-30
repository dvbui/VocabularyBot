import random
import vocs
from nltk.corpus import wordnet

# question data
WORD_LIST = ["./words/VocabularyWorkshopEasy.txt",
             "./words/VocabularyWorkshopMedium.txt",
             "./words/VocabularyWorkshopHard.txt"]
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


def generate_custom_antonym(difficulty=1, chosen_word=""):

    if chosen_word != "":
        for i in range(len(WORD_LIST)):
            if len(master_word_data[i]) == 0:
                init_word_list(i)
            if chosen_word in master_word_data[i]:
                difficulty = i
                break

    if len(master_word_data[difficulty-1]) == 0:
        init_word_list(difficulty-1)

    if chosen_word == "":
        word, info = random.choice(list(master_word_data[difficulty-1].items()))
    else:
        word = chosen_word

    antonyms = get_antonyms(word)
    antonyms = {antonyms[i]: "" for i in range(len(antonyms))}
    removed = {}
    for anto in antonyms:
        if (anto.lower() in word.lower()) or (word.lower() in anto.lower()):
            removed[anto] = ""

    for word in removed:
        del antonyms[word]

    antonyms = list(antonyms.keys())

    print(len(antonyms))
    if len(antonyms) == 0:
        if chosen_word == "":
            return generate_custom_antonym(difficulty, chosen_word)
        else:
            return None, None, None

    chosen_antonym = random.choice(antonyms)
    not_antonym = list(master_word_data[difficulty-1].keys())
    random.shuffle(not_antonym)

    real_not_antonym = {}
    for candidate in not_antonym:
        if get_similarity(candidate, "", chosen_antonym) > 10 ** -9:
            continue
        if has_swear_words(candidate):
            continue
        if (candidate.lower() in chosen_antonym.lower()) or (chosen_antonym.lower() in candidate.lower()):
            continue
        if (candidate.lower() in word.lower()) or (word.lower() in candidate.lower()):
            continue
        real_not_antonym[candidate] = ""
        if len(real_not_antonym) == 3:
            break

    not_antonyms = list(real_not_antonym.keys())

    question = "Which of the following words is an antonym for {}?\n".format(word)
    answer = random.randint(1, 4)
    for i in range(0, answer - 1):
        question += "{}. {}\n".format(i + 1, not_antonyms[i])
    question += "{}. {}\n".format(answer, chosen_antonym)
    for i in range(answer, 4):
        question += "{}. {}\n".format(i + 1, not_antonyms[i - 1])

    return question, answer, word


def generate_custom_question(difficulty=1, chosen_word=""):
    return generate_custom_antonym(difficulty, chosen_word)

