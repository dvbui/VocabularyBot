def register_message():
    mess = "```\n"
    mess += "Registration Phase\n"
    mess += "Generating a new block in 30 seconds\n"
    mess += "Type \"olym register\" to solve this block\n"
    mess += "Note: You need to register once for each block.\n"
    mess += "```\n"
    return mess


def question_message(question, index="", number_of_character=""):
    mess = "```\n"
    mess += "\n"
    mess += "Clue {} ({} characters):\n".format(index, number_of_character)
    mess += question+"\n"
    mess += "\n"
    mess += "You have 25 seconds to answer this clue.\n"
    mess += "Type your best answer (and only your answer) to answer this clue.\n"
    mess += "To solve this block, type \"olym solve [answer]\"\n"
    mess += "\n"
    mess += "If you haven't registered, type \"olym register\" to register.\n"
    mess += "To stop receiving clues and unregister, type \"olym stop\".\n"
    mess += "```\n"
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


def keyword_message(length):
    mess = "```\n"
    mess += "The keyword has {}".format(length)+" characters.\n"
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
