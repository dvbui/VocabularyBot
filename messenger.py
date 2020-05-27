import requests
import json
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from time import sleep

import vocs
import wordDef

OLYMPIA_MAIN_SERVER = 709919416456052897

messages = {}


def init_message(db):
    doc_ref = db.collection(u'messages').document(str(OLYMPIA_MAIN_SERVER))
    doc = doc_ref.get()
    if doc.exists:
        info = doc.to_dict()
        messages["register_message"] = info["register_message"].replace("\\n", "\n")
        messages["rule_message"] = info["rule_message"].replace("\\n", "\n")
        messages["help_message"] = info["help_message"].replace("\\n", "\n")
        print(messages["register_message"])
    else:
        print("Cannot find messages")


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


def question_message(question, clues, index=1, number_of_character="", final_clue=False):
    mess = "```\n"
    mess += "\n"
    for i in range(0, index-1):
        mess += "Clue {}: {}".format(i+1, clues[i][0])+"\n"
    mess += "Clue {} ({} characters):\n".format(index, number_of_character)
    mess += question+"\n"
    mess += "\n"
    mess += "You have 20 seconds to answer this clue.\n"
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
    mess += "```\n"
    mess += vocs.getLink(word)
    return mess


def keyword_message(length, not_keywords=""):
    mess = "```\n"
    mess += "The keyword has {}".format(length)+" characters.\n"
    mess += "```\n"
    return mess


def fitting(s, length):
    return s + " " * max(0, (length - len(s)))


def print_table(table, deliminator=" | ", max_length_string=1992):
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


def show_user_answer(user_list, answer, question):
    mess = "```\n"
    table = [["Name", "Answer"]]
    for user in user_list:
        if user_list[user]["answer"] != "":
            similarity = wordDef.get_similarity(answer, question, user_list[user]["answer"])
            if similarity != 0:
                table.append([str(user), str(user_list[user]["answer"])])
    mess += print_table(table, max_length_string=500)
    mess += "```\n"
    return mess
