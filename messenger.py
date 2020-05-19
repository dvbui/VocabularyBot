import requests
import json
import os

messages = {}


def init_message():
    while True:
        try:
            url = os.environ["SECRET_URL"]
            obj = {"command": "init message"}
            x = requests.post(url, data=obj)
        except:
            continue

        if x.text[0] != '\n':
            continue

        print(x.text)
        global messages
        messages = json.loads(x.text.strip())
        break


def register_message():
    global messages
    mess = "```\n"
    mess += messages["register_message"]
    mess += "```\n"
    return mess


def rule_message():
    mess = "```\n"
    mess += messages["rule_message"]
    mess += "```\n"
    return mess


def help_message():
    mess = "```\n"
    mess += messages["help_message"]
    mess += "```\n"
    return mess


def question_message(question, index="", number_of_character="", final_clue=False):
    mess = "```\n"
    mess += "\n"
    mess += "Clue {} ({} characters):\n".format(index, number_of_character)
    mess += question+"\n"
    mess += "\n"
    mess += "You have 25 seconds to answer this clue.\n"
    if not final_clue:
        mess += "Type your best answer (and only your answer) for this clue.\n"
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
    mess += long_definition + "\n\n"
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
