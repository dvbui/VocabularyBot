import requests
import vocs
import wordDef
import os
from os import path
import discord
import json
import asyncio
import random
import messenger


# load new word list
wordDatabase = {}


def init_word_list():
    global wordDatabase
    new_word_file = open("list7000.txt", "r")
    for line in new_word_file:
        wordDatabase[line.strip()] = {"long": ""}
    new_word_file.close()


init_word_list()

# game information
status = 0
keyWord = ""
clues = {}
listOfUsers = {}
answers = {}
wrong_keyWords = ""
winner = ""
acceptingAnswers = False
acceptingKeyword = False
# constant
client = discord.Client()


def register_user(user):
    global listOfUsers
    if not (user in listOfUsers):
        listOfUsers[user] = {"answer": "", "score": 0, "receive_message": True, "eliminate": False}
        listOfUsers[user]["activate"] = False
    listOfUsers[user]["receive_message"] = True


def load_user_data():
    global listOfUsers
    listOfUsers = {}
    link = os.environ["SECRET_URL"]
    post_obj = {"command": "print user"}
    while True:
        x = requests.post(link, post_obj)
        if x.text[0] == '\n':
            break

    f = x.text.strip().split('\n')
    for line in f:
        line = line.strip().split(' ')
        if len(line) != 3:
            break
        print(line[0])
        print(line[1])
        print(line[2] == "1")
        user = client.get_user(int(line[0]))
        if not (user is None):
            register_user(user)
            listOfUsers[user]["score"] = float(line[1])
            listOfUsers[user]["receive_message"] = line[2] == "1"


def save_user_data():
    global listOfUsers
    link = os.environ["SECRET_URL"]

    for user in listOfUsers:
        post_obj = {"user": str(user.id), "score": listOfUsers[user]["score"]}
        if listOfUsers[user]["receive_message"]:
            post_obj["receive_message"] = "1"
        else:
            post_obj["receive_message"] = "0"
        while True:
            x = requests.post(link, post_obj)
            if x.text[0] == '\n':
                break


def save_block():
    global listOfUsers
    link = os.environ["SECRET_URL"]
    post_obj = {"user": 0, "block": ""}
    for i in range(0, len(clues)):
        post_obj["block"] += " "+clues[i][0]
    post_obj["block"] = post_obj["block"].strip()
    while True:
        x = requests.post(link, post_obj)
        if x.text[0] == '\n':
            break


def free_all_users():
    global listOfUsers
    for user in listOfUsers:
        listOfUsers[user]["eliminate"] = False
        listOfUsers[user]["activate"] = False


def stop_user(user):
    global listOfUsers
    if user in listOfUsers:
        listOfUsers[user]["receive_message"] = False


def is_game_running():
    global status
    return 1 <= status <= 5


def pick_keyword():
    clue_list = []
    global wordDatabase
    if len(wordDatabase) == 0:
        init_word_list()

    while True:
        word, info = random.choice(list(wordDatabase.items()))

        if wordDef.get_definition(word) == "":
            del wordDatabase[word]
            continue

        if info["long"] == "":
            info["long"] = vocs.getShortDefinitionWithWord(word)
            if info["long"] == "":
                del wordDatabase[word]
                continue

        details = wordDef.choose_questions(word)
        print(word)
        print(details)

        if details is None:
            continue
        else:
            break
    for k in details:
        clue_list.append((k, details[k]))
    clue_list.append((word, wordDef.get_definition(word)))

    return word, clue_list


async def send_message(user, message):
    if (user in listOfUsers) and listOfUsers[user]["receive_message"]:
        try:
            await user.send(message)
        except:
            print("Can't send message")


async def main_game():
    await client.wait_until_ready()

    global status
    global keyWord
    global clues
    global wrong_keyWords
    global winner
    global acceptingAnswers, acceptingKeyword
    while True:
        channel = client.get_channel(710081986466676757)
        if status == 0:  # Registering phase
            load_user_data()
            free_all_users()
            wrong_keyWords = ""
            winner = ""
            acceptingAnswers = False
            acceptingKeyword = False
            m = messenger.register_message()
            await channel.send(messenger.register_message())
            for user in listOfUsers:
                await send_message(user, m)
            keyWord, clues = pick_keyword()
            await asyncio.sleep(5)
            m = messenger.rule_message()
            await channel.send(m)
            for user in listOfUsers:
                await send_message(user, m)
            await asyncio.sleep(25)
            await channel.send(messenger.keyword_message(len(keyWord)))
            for user in listOfUsers:
                await send_message(user, messenger.keyword_message(len(keyWord)))
            status += 1

        if 1 <= status <= 5:  # During the game
            acceptingAnswers = True
            acceptingKeyword = True
            if status <= 4:
                answer = clues[status - 1][0]
            else:
                answer = keyWord

            print(answer)
            question = clues[status - 1][1]
            message_to_send = messenger.question_message(question, status, len(answer), status == 5)
            message_to_send += messenger.keyword_message(len(keyWord), wrong_keyWords)
            await channel.send(message_to_send)
            for user in listOfUsers:
                listOfUsers[user]["answer"] = ""
                await send_message(user, message_to_send)

            #  time to answer clue
            await asyncio.sleep(25)

            acceptingAnswers = False
            acceptingKeyword = False
            if 1 <= status <= 5:
                fake_list = {}
                for user in listOfUsers:
                    fake_list[user] = {}
                    fake_list[user]["answer"] = listOfUsers[user]["answer"]

                user_answers = messenger.show_user_answer(fake_list)
                for user in listOfUsers:
                    await send_message(user, user_answers)
                await channel.send(user_answers)
                await asyncio.sleep(5)

                for user in listOfUsers:
                    if listOfUsers[user]["eliminate"]:
                        await send_message(user, "The correct answer is "+answer+".")
                        continue
                    user_answer = fake_list[user]["answer"]
                    if user_answer == "":
                        m = "We did not receive any answer from you. 0 points.\nThe correct answer is " + answer
                        await send_message(user, m)
                    else:
                        m = "Your final answer is {}.".format(user_answer)+"\n"
                        if user_answer == answer:
                            m += "And that is the correct answer. You get 1 point."
                            listOfUsers[user]["score"] += 1
                        else:
                            similarity = 0
                            if len(user_answer) == len(answer):
                                similarity = wordDef.get_similarity(answer, question, listOfUsers[user]["answer"])

                            listOfUsers[user]["score"] += similarity
                            m += "You get {} points for your answer.".format(similarity)
                            m += " The correct answer is {} ".format(answer)

                        await send_message(user, m)

                if 1 <= status <= 5:
                    status += 1
                await asyncio.sleep(5)

        if status == 6:  # Puzzle is solved
            acceptingKeyword = False
            acceptingAnswers = False
            mess = messenger.block_end_message(keyWord, wordDatabase[keyWord]["long"], winner)
            del wordDatabase[keyWord]
            await channel.send(mess)
            for user in listOfUsers:
                await send_message(user, mess)
                await send_message(user, "```Your current score is "+str(listOfUsers[user]["score"])+"```")
                await send_message(user, messenger.ranklist_message(listOfUsers))
            await channel.send(messenger.ranklist_message(listOfUsers))
            status = 0
            save_user_data()
            save_block()

        await asyncio.sleep(1)


@client.event
async def on_ready():
    print("Bot is ready.")
    load_user_data()
    client.loop.create_task(main_game())


async def guess_keyword(user, key_answer):
    global status
    if key_answer.lower() == keyWord.lower():
        score = max(1, (5 - status) * 2)
        listOfUsers[user]["score"] += score
        global winner
        winner = str(user)
        mess = "Puzzle solved. Everyone is eliminated!\n"
        mess += "You gain {} points for your keyword answer".format(score)
        status = 6
    else:
        similarity = 0
        if len(key_answer) == len(keyWord):
            similarity = wordDef.get_similarity(key_answer, "", keyWord)
        score = max(1, (5 - status) * 2) * similarity
        listOfUsers[user]["score"] += score
        mess = "Puzzle is not solved.\n"
        mess += "You get {} points for your answer.".format(score) + "\n"
        mess += "You have been eliminated from the game."
        global wrong_keyWords
        if key_answer.isalpha():
            wrong_keyWords += " {}".format(key_answer)

    listOfUsers[user]["eliminate"] = True
    await user.send(mess)


@client.event
async def on_message(message):
    global status
    global keyWord
    global clues
    if message.author == client.user:
        return
    if message.author.bot:
        return

    message.content = message.content.lower()
    if (message.author in listOfUsers) and is_game_running() and message.content.isalpha():
        global acceptingAnswers
        listOfUsers[message.author]["activate"] = True
        if listOfUsers[message.author]["eliminate"]:
            await message.author.send("You have been eliminated from the game.")
        else:
            if status <= 4:
                if acceptingAnswers:
                    listOfUsers[message.author]["answer"] = message.content
                    await message.author.send("Your current answer is " + message.content + "\n({} characters)".format(len(message.content)))
                else:
                    await message.author.send("Answers for this clue are no longer accepted!")
            else:
                if acceptingKeyword:
                    await guess_keyword(message.author, message.content)
                else:
                    await message.author.send("We are not accepting keyword answers. Please wait a little bit and try again.")

    args = message.content.split(' ')
    if args[0] != "olym":
        return

    mess = ""
    if len(args) == 2 and args[1] == "hello":
        mess = "Hello, I am a test bot."

    if len(args) == 2 and args[1] == "register":
        mess = "You have been registered."
        register_user(message.author)
        if is_game_running():
            await message.author.send(messenger.keyword_message(len(keyWord)))
            question = clues[status-1][1]
            if status == 5:
                answer = keyWord
            else:
                answer = clues[status-1][0]
            await message.author.send(messenger.question_message(question, status, len(answer)))

    if len(args) == 2 and args[1] == "stop":
        mess = "You have been unregistered."
        stop_user(message.author)

    if len(args) == 3 and args[1] == "solve" and 1 <= status <= 5 and message.author in listOfUsers:
        listOfUsers[message.author]["activate"] = True
        if acceptingKeyword:
            if listOfUsers[message.author]["eliminate"]:
                mess = "You have been eliminated from this game."
            else:
                key_answer = args[2]
                await guess_keyword(message.author, key_answer)
        else:
            mess = "We are not accepting keyword answers. Please wait a little bit and try again."

    if len(args) == 2 and args[1] == "export" and message.author in listOfUsers:
        link = os.environ["SECRET_URL"]
        post_obj = {"user": str(message.author.id), "command": "print block"}
        while True:
            x = requests.post(link, post_obj)
            if x.text[0] == '\n':
                break
        mess = "```\n"
        mess += x.text.strip()
        mess += "```\n"

    if mess != "":
        await message.author.send(mess)


token = os.environ['CLIENT_TOKEN']

client.run(token)
