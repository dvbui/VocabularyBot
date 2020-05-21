import wordDef


def test_easy_list():
    wordDef.init_word_list(0)
    g = open("realEasyWordList.txt","w")
    for word in wordDef.master_word_data[0]:
        result = wordDef.generate_custom_question(1, word)
        if not (result is None):
            print(word)
            g.write(word+"\n")
    g.close()
