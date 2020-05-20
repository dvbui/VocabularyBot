import requests
import json
import os
from time import sleep

messages = {}


def get_data(url, obj, important=False, retry=10):
    cnt = 0
    while True:
        try:
            x = requests.post(url, data=obj)
        except:
            if important:
                sleep(5)
                continue
            else:
                cnt += 1
                if cnt == retry:
                    return ""

        if x.text[0] == '\n':  # success
            break

    return x.text.strip()


def init_message():
    url = os.environ["SECRET_URL"]
    obj = {"command": "init message"}
    global messages
    messages = json.loads(get_data(url, obj))


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


def fitting(s, length):
    return s + " " * max(0, (length - len(s)))


def print_table(table, deliminator = " | ", max_length_string = 1992):
    n = len(table)
    if n == 0:
        return ""
    m = len(table[0])
    max_length = [0] * m
    for i in range(n):
        for j in range(m):
            max_length[j] = max(max_length[j], len(str(table[i][j])))
    header = ""
    for j in range(m):
        header += fitting(str(table[0][j]), max_length[j])
        if j+1 != m:
            header += deliminator
    barrier = "-"*len(header)
    res = header+"\n"+barrier+"\n"
    for i in range(1, n):
        for j in range(m):
            res += fitting(str(table[i][j]), max_length[j])
            if j+1 != m:
                res += deliminator
        res += "\n"
    return res[0:min(max_length_string, len(res))]


def ranklist_message(user_list):
    mess = "```\n"
    table = [["Name", "Score"]]
    user_list_items = []
    for user in user_list:
        user_list_items.append([user, user_list[user]["score"]])
    user_list_items.sort(key=lambda u: -u[1])
    for user in user_list_items:
        table.append([str(user[0]), "{:.2f}".format(user[1])])
    mess += print_table(table, max_length_string=500)
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
