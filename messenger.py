def register_message():
    mess = "```\n"
    mess += "Registration Phase\n"
    mess += "Generating a new block in 30 seconds\n"
    mess += "Type \"olym register\" to solve this block\n"
    mess += "To stop receiving clues and unregister, type \"olym stop\".\n"
    mess += "```\n"
    return mess


def question_message(question, index="", number_of_character="",final_clue=False):
    mess = "```\n"
    mess += "\n"
    mess += "Clue {} ({} characters):\n".format(index, number_of_character)
    mess += question+"\n"
    mess += "\n"
    mess += "You have 25 seconds to answer this clue.\n"
    if not final_clue:
        mess += "Type your best answer (and only your answer) to answer this clue.\n"
        mess += "To guess the keyword, type \"olym solve [keyword]\"\n"
    else:
        mess += "The answer for this clue is the keyword.\n"
        mess += "Type your best guess (and only your guess) for the keyword.\n"
    mess += "```"
    return mess


def block_end_message(word, long_definition, winner):
    mess = "```\n"
    if winner != "":
        mess += "{} solved this block!".format(winner)+"\n\n"
    mess += "The keyword is "+word+"\n"
    mess += "\n"
    mess += "From Vocabulary.com:\n"
    mess += long_definition + "\n"
    mess += "```\n"
    return mess


def keyword_message(length, not_keywords=""):
    mess = "```\n"
    mess += "The keyword has {}".format(length)+" characters.\n"
    if not_keywords != "":
        mess += "The keyword is not:{}".format(not_keywords)+"\n"
    mess += "```\n"
    return mess


def ranklist_message(user_list):
    mess = "```\n"
    mess += "Name \t\t Score\n"
    for user in user_list:
        mess += str(user)+" \t\t "+str(user_list[user]["score"])+"\n"
    mess += "```\n"
    return mess


def show_user_answer(user_list):
    mess = "```\n"
    mess += "Name \t\t Answer\n"
    for user in user_list:
        if user_list[user]["answer"] != "":
            mess += str(user)+" \t\t "+str(user_list[user]["answer"])+"\n"
    mess += "```\n"
    return mess
