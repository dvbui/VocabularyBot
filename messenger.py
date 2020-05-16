def register_message():
    mess = "```\n"
    mess += "Registration Phase\n"
    mess += "Generating a new block in 30 seconds\n"
    mess += "Type \"olym register\" to solve this block\n"
    mess += "To stop receiving clues and unregister, type \"olym stop\".\n"
    mess += "```\n"
    return mess


def rule_message():
    mess = "```\n"
    mess += "Blockbuster\n"
    mess += "In this game, contestants answer four questions together.\n"
    mess += "The content and the answer of these questions are clues for a keyword.\n"
    mess += "Contestants answer these questions by typing only their answers (the prefix olym is not needed)\n"
    mess += "The time to answer each question is 25 seconds.\n"
    mess += "Each correct answer is 1 point.\n"
    mess += "Contestants can answer the keyword anytime.\n"
    mess += "(except when waiting for the next clue and when grading the answers)\n"
    mess += "If a contestant get the keyword on clue 1, they will be awarded 8 points, "
    mess += "clue 2 - 6 points, clue 3 - 4 points, clue 4 - 2 points.\n"
    mess += "Once all four clues are exhausted, the definition of the keyword "
    mess += "will appear. If a contestant get the keyword using the definition, they will be awarded 1 point.\n"
    mess += "Whenever a contestant gives the correct keyword, the game will stop immediately.\n"
    mess += "Note: If a contestant answers the keyword incorrectly, they will be eliminated from this game.\n"
    mess += "(The answer is considered correct if it has the required number of characters and is a synonym for the answer.)\n"
    mess += "(If the answer for the keyword is not matched with the keyword but has the required number of characters, "
    mess += "the answerer might receive partial points. The game will still continue.)\n"
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
    mess += long_definition + "\n"
    mess += "This text is from Vocabulary.com (https://www.vocabulary.com). Copyright ©1998-2020 Thinkmap, Inc. All rights reserved.\n"
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
