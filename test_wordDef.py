import wordDef
import inflect

inflect = inflect.engine()


def test_easy_list():
    wordDef.init_word_list(0)
    g = open("realEasyWordList.txt", "w")
    for word in wordDef.master_word_data[0]:
        print(word)
        result = wordDef.generate_custom_question(1, word)
        if not (result is None):
            print(word+" chosen")
            g.write(word+"\n")
    g.close()


wordDatabase = {}
WORD_LIST = ["./words/VinceGREWordListFormatted.txt", "./words/WordPowerMadeEasyFormatted.txt",
             "./words/VocabularyWorkshopEasy.txt", "./words/VocabularyWorkshopMedium.txt",
             "./words/VocabularyWorkshopHard.txt"]


def init_word_list():
    global wordDatabase
    for word_list in WORD_LIST:
        new_word_file = open(word_list, "r")
        for line in new_word_file:
            wordDatabase[line.strip()] = {"long": ""}
        new_word_file.close()


def pick_keyword(word):
    clue_list = []
    global wordDatabase

    info = wordDatabase[word]
    print(word+"\n"+str(info)+"\n"+str(len(wordDatabase))+"\n")

    if inflect.singular_noun(word):
        return False

    word_definition = wordDef.get_definition(word)
    info["long"] = word_definition
    if word_definition == "":
        return False

    details = wordDef.choose_questions(word, definition=word_definition)
    print(word)
    print(details)

    if details is None:
        return False

    for k in details:
        clue_list.append((k, details[k]))
    clue_list.append((word, word_definition))

    if wordDef.has_swear_words(str(clue_list)+" "+word):
        return False

    return True


def test_pick_keyword():
    init_word_list()
    f = open("./words/playable.txt", "w")
    print(len(wordDatabase))
    cnt = 0
    for word in wordDatabase:
        cnt += 1
        print(cnt)
        if pick_keyword(word):
            f.write(word+"\n")
    f.close()


