import requests
import vocs
import wordDef
import os
import discord
import inflect
import asyncio
import random
import messenger
import sys
import tracemalloc
tracemalloc.start()
from time import sleep

sys.setrecursionlimit(10 ** 6)
inflect = inflect.engine()

ADMIN_ID = 361217404296232961
# load new word list
wordDatabase = {}


def requests_post(s):
    return requests.post(s["url"], data=s["obj"])


async def get_data(url, obj, important=False, retry=10):
    cnt = 0
    while True:
        try:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, requests_post, {"url": url, "obj": obj})
            x = await future
            if x.text[0] == '\n':  # success
                return x.text.strip()
        except:
            if important:
                await asyncio.sleep(5)
                continue
            else:
                cnt += 1
                if cnt == retry:
                    return ""
    return ""


async def init_word_list():
    global wordDatabase
    new_word_file = open("list8000.txt", "r")
    for line in new_word_file:
        wordDatabase[line.strip()] = {"long": ""}
    new_word_file.close()
    url = os.environ["SECRET_URL"]
    obj = {"command": "print picked words"}
    f = (await get_data(url, obj, True)).split('\n')
    for line in f:
        line = line.strip()
        if line in wordDatabase:
            del wordDatabase[line]
    if len(wordDatabase) == 0:
        await get_data(os.environ["SECRET_URL"], {"command": "reset word"}, False)
        await init_word_list()


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
game_finished = 0
clock = 0
# constant
client = discord.Client()


def register_user(user):
    global listOfUsers
    if not (user in listOfUsers):
        listOfUsers[user] = {"answer": "", "score": 0, "receive_message": True, "eliminate": False}
        listOfUsers[user]["activate"] = False
    listOfUsers[user]["receive_message"] = True


async def load_user_data():
    global listOfUsers
    listOfUsers = {}
    link = os.environ["SECRET_URL"]
    post_obj = {"command": "print user"}

    f = (await get_data(link, post_obj, True)).split('\n')
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


async def save_user_data():
    global listOfUsers
    link = os.environ["SECRET_URL"]

    for user in listOfUsers:
        post_obj = {"user": str(user.id), "score": listOfUsers[user]["score"]}
        if listOfUsers[user]["receive_message"]:
            post_obj["receive_message"] = "1"
        else:
            post_obj["receive_message"] = "0"
        await get_data(link, post_obj, False)


async def save_block():
    global listOfUsers
    link = os.environ["SECRET_URL"]
    post_obj = {"user": 0, "block": ""}
    for i in range(0, len(clues)):
        post_obj["block"] += " " + clues[i][0]
    post_obj["block"] = post_obj["block"].strip()
    await get_data(link, post_obj, False)


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


async def pick_keyword():
    clue_list = []
    global wordDatabase
    if len(wordDatabase) == 0:
        await init_word_list()

    word_definition = ""
    while len(wordDatabase) > 0:
        word, info = random.choice(list(wordDatabase.items()))
        print(word+"\n"+info+"\n"+str(len(wordDatabase))+"\n")

        if inflect.singular_noun(word):
            url = os.environ["SECRET_URL"]
            obj = {"word": word, "picked": 1}
            await get_data(url, obj, False)
            del wordDatabase[word]
            continue

        if wordDef.get_definition(word) == "":
            url = os.environ["SECRET_URL"]
            obj = {"word": word, "picked": 1}
            await get_data(url, obj, False)
            del wordDatabase[word]
            continue

        if info["long"] == "" or info["long"].count("\t") >= 6:
            info["long"] = await vocs.getShortDefinitionWithWord(word)
            if info["long"] == "":
                url = os.environ["SECRET_URL"]
                obj = {"word": word, "picked": 1}
                await get_data(url, obj, False)
                del wordDatabase[word]
                continue

        word_definition = wordDef.get_definition(word)
        details = wordDef.choose_questions(word, definition=word_definition)
        print(word)
        print(details)

        if details is None:
            continue
        else:
            break

    if len(wordDatabase) == 0:
        await init_word_list()
        return await pick_keyword()

    for k in details:
        clue_list.append((k, details[k]))
    clue_list.append((word, word_definition))

    return word, clue_list


async def send_message(user, message, special=False):
    if special or ((user in listOfUsers) and listOfUsers[user]["receive_message"]):
        try:
            print(str(user) + " " + str(message))
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
    channel = client.get_channel(710081986466676757)

    if client.is_closed():
        return

    if status == 0:  # Registering phase
        #  load_user_data()
        free_all_users()
        wrong_keyWords = ""
        winner = ""
        acceptingAnswers = False
        acceptingKeyword = False
        m = messenger.register_message()
        await send_message(channel, messenger.register_message(), True)
        for user in listOfUsers:
            await send_message(user, m)
        keyWord, clues = await pick_keyword()
        await asyncio.sleep(5)
        m = messenger.rule_message()
        await send_message(channel, m, True)
        for user in listOfUsers:
            await send_message(user, m)
        await asyncio.sleep(25)
        await send_message(channel, messenger.keyword_message(len(keyWord)), True)
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
        message_to_send = messenger.question_message(question, clues, status, len(answer), status == 5)
        message_to_send += messenger.keyword_message(len(keyWord), wrong_keyWords)
        await send_message(channel, message_to_send, True)
        for user in listOfUsers:
            listOfUsers[user]["answer"] = ""
            await send_message(user, message_to_send)

        #  time to answer clue
        global clock
        clock = 25
        while clock > 0:
            clock -= 1
            print(clock)
            await asyncio.sleep(1)

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
            await send_message(channel, user_answers, True)
            await asyncio.sleep(5)

            for user in fake_list:
                if listOfUsers[user]["eliminate"]:
                    await send_message(user, "The correct answer is " + answer + ".")
                    continue
                user_answer = fake_list[user]["answer"]
                if user_answer == "":
                    m = "We did not receive any answer from you. 0 points.\nThe correct answer is " + answer
                    await send_message(user, m)
                else:
                    m = "Your final answer is {}.".format(user_answer) + "\n"
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

    if status == 6:  # Puzzle is solved
        global game_finished
        game_finished += 1
        acceptingKeyword = False
        acceptingAnswers = False
        mess = messenger.block_end_message(keyWord, wordDatabase[keyWord]["long"], winner)
        del wordDatabase[keyWord]
        url = os.environ["SECRET_URL"]
        obj = {"word": keyWord, "picked": 1}
        await get_data(url, obj, False)
        await send_message(channel, mess, True)
        for user in listOfUsers:
            await send_message(user, mess)
            await send_message(user, "```Your current score is " + str(listOfUsers[user]["score"]) + "```")
            await send_message(user, messenger.ranklist_message(listOfUsers))
        await send_message(channel, messenger.ranklist_message(listOfUsers), True)
        status = 0
        await save_user_data()
        await save_block()
        if game_finished == 10:
            os.system("bash ./restart.sh")
            return

    await main_game()


@client.event
async def on_member_join(member):
    print("I'm here")
    obj = {"server": str(member.guild.id), "purpose": "welcome_message"}
    link = os.environ["SECRET_URL"]
    welcome_message = await get_data(link, obj)

    if welcome_message == "":
        return

    welcome_message = welcome_message.replace("{user}", str(member))
    obj["purpose"] = "welcome_channel"
    try:
        welcome_channel_id = int(await get_data(link, obj))
        global client
        channel = client.get_channel(welcome_channel_id)
        await send_message(channel, welcome_message, True)
    except:
        print("Can't send message")
        return


@client.event
async def on_ready():
    print("Bot is ready.")
    await load_user_data()
    await init_word_list()
    messenger.init_message()
    print("I'm here")
    await main_game()


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
    await send_message(user, mess)


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
        if listOfUsers[message.author]["receive_message"]:
            global acceptingAnswers
            if listOfUsers[message.author]["eliminate"]:
                await send_message(message.author, "You have been eliminated from the game.")
            else:
                if status <= 4:
                    if acceptingAnswers:
                        listOfUsers[message.author]["answer"] = message.content[
                                                                0:min(len(message.content), len(clues[status - 1][1]))]
                        mess = "Your current answer is " + message.content + "\n({} characters)".format(
                            len(message.content))
                        global clock
                        mess += "\nYou have {} seconds left.".format(clock)
                        await send_message(message.author, mess)
                    else:
                        await send_message(message.author, "Answers for this clue are no longer accepted!")
                else:
                    if acceptingKeyword:
                        await guess_keyword(message.author, message.content)
                    else:
                        await send_message(message.author,
                                           "We are not accepting keyword answers. Please wait a little bit and try again.")

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
            question = clues[status - 1][1]
            if status == 5:
                answer = keyWord
            else:
                answer = clues[status - 1][0]
            await message.author.send(messenger.question_message(question, clues, status, len(answer), status == 5))

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
        post_obj = {"user": "", "command": "print block"}
        mess = await get_data(link, post_obj, False)
        if mess:
            mess = "```\n" + mess + "```"
        else:
            mess = "Exporting words failed. Please try again later."

    if len(args) == 2 and args[1] == "help":
        mess = messenger.help_message()

    if len(args) == 2 and args[1] == "recent":
        obj = {"command": "print recent block"}
        url = os.environ["SECRET_URL"]
        mess = "```\n" + await get_data(url, obj, False) + "```\n"

    if len(args) == 3 and args[1] == "def" and args[2].isalpha():
        mess = "```\n"
        definition = vocs.getShortDefinitionWithWord(args[2])
        if definition != "":
            mess += "\n"
            mess += definition + "\n"
            mess += "This text is from Vocabulary.com (https://www.vocabulary.com). Copyright ©1998-2020 Thinkmap, Inc. All rights reserved.\n"
            mess += "\n"
        else:
            mess += "{} is not in the database.".format(args[2])
        mess += "```\n"

    if len(args) == 2 and args[1] == "restart" and message.author.id == ADMIN_ID:
        os.system("bash ./restart.sh")

    if mess != "":
        await send_message(message.author, mess, True)


token = os.environ['CLIENT_TOKEN']

client.run(token)
