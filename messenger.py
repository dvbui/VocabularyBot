def register_message():
    mess = "```\n"
    mess += "Registration Phase\n"
    mess += "Generating new block\n"
    mess += "Type \"olym register\" to solve this block\n"
    mess += "Note: You need to register once for each block."
    mess += "```\n"
    return mess


def question_message(question, index="", type_of_word="", number_of_character=""):
    mess = "```\n"
    mess += "\n"
    mess += "Clue {} ({},{} characters): {}\n".format(index, type_of_word, number_of_character, question)
    mess += "\n"
    mess += "You have 15 seconds to answer this clue.\n"
    mess += "Type your answer (and only your answer) to answer your question.\n"
    mess += "If you haven't register, type \"olym register\" to register.\n"
    mess += "\n"
    mess += "To solve this block, type \"olym solve [answer]\"\n"
    mess += "\n"
    mess += "```\n"
    return mess
