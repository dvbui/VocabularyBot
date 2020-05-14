def register_message():
    mess = "```\n"
    mess += "Registration Phase\n"
    mess += "Generating new block\n"
    mess += "Type \"olym register\" to solve this block\n"
    mess += "Note: You need to register once for each block."
    mess += "```\n"
    return mess


def question_message(question, index="", number_of_character=""):
    mess = "```\n"
    mess += "\n"
    mess += "Clue {} ({} characters): {}\n".format(index, number_of_character, question)
    mess += "\n"
    mess += "You have 15 seconds to answer this clue.\n"
    mess += "Type your best answer (and only your answer) to answer this clue.\n"
    mess += "To solve this block, type \"olym solve [answer]\"\n"
    mess += "\n"
    mess += "If you haven't registered, type \"olym register\" to register.\n"
    mess += "To stop receiving clues and unregister, type \"olym stop\".\n"
    mess += "```\n"
    return mess


def block_end_message(word, long_definition):
    mess = "```\n"
    mess += "This block is "+word+"\n"
    mess += "\n"
    mess += "From Vocabulary.com:\n"
    mess += long_definition + "\n"
    mess += "```\n"
    return mess
