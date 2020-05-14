import vocs
import wordDef
import os
from os import path
import discord
import json
import asyncio
import random
import messenger
import pickle

# load word database
wordFile = open("wordDatabase.json", "r")
wordDatabase = json.load(wordFile)
wordFile.close()

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
    listOfUsers[user]["receive_message"] = True


def load_user_data():
    global listOfUsers
    listOfUsers = {}
    if path.exists("user_data.obj"):
        f = open("user_data.obj", "r")
        for line in f:
            line = line.strip().split(' ')
            if len(line) != 3:
                break
            print(line[0])
            print(line[1])
            print(line[2] == "True")
            user = client.get_user(int(line[0]))
            register_user(user)
            listOfUsers[user]["score"] = float(line[1])
            listOfUsers[user]["receive_message"] = line[2] == "True"
        f.close()


def save_user_data():
    global listOfUsers
    f = open("user_data.obj", "w")
    for user in listOfUsers:
        output = str(user.id)+" "+str(listOfUsers[user]["score"])+" "+str(listOfUsers[user]["receive_message"])+"\n"
        print(output)
        f.write(output)
    f.close()


def free_all_users():
    global listOfUsers
    for user in listOfUsers:
        listOfUsers[user]["eliminate"] = False


def stop_user(user):
    global listOfUsers
    if user in listOfUsers:
        listOfUsers[user]["receive_message"] = False


def is_game_running():
    global status
    return 1 <= status <= 5


def pick_keyword():
    clue_list = []
    while True:
        word, info = random.choice(list(wordDatabase.items()))
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
        await user.send(message)


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
            await asyncio.sleep(30)
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
                        m = "We did not receive any answer. 0 points.\nThe correct answer is " + answer
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
            await channel.send(mess)
            for user in listOfUsers:
                await send_message(user, mess)
                await send_message(user, "```Your current score is "+str(listOfUsers[user]["score"])+"```")
                await send_message(user, messenger.ranklist_message(listOfUsers))
            await channel.send(messenger.ranklist_message(listOfUsers))
            status = 0
            save_user_data()

        if status < 0 or status > 6:
            status = 0
            await channel.send("Something is wrong! Restarting game.")
            for user in listOfUsers:
                await send_message(user, "Something is wrong! Restarting game.")


@client.event
async def on_ready():
    print("Bot is ready.")
    load_user_data()
    client.loop.create_task(main_game())


async def guess_keyword(user, key_answer):
    global status
    if key_answer == keyWord.lower():
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
    if (message.author in listOfUsers) and is_game_running() and (not message.content.startswith("olym ")):
        global acceptingAnswers
        if listOfUsers[message.author]["eliminate"]:
            await message.author.send("You have been eliminated from the game.")
        else:
            if status <= 4:
                if acceptingAnswers:
                    listOfUsers[message.author]["answer"] = message.content
                    await message.author.send("Your current answer is " + message.content + "\n({} letters)".format(len(message.content)))
                else:
                    await message.author.send("Answers for this clue are no longer accepted!")
            else:
                if acceptingKeyword:
                    await guess_keyword(message.author,message.content)
                else:
                    await message.author.send("We are not accepting keyword answers. Please wait a little bit and try again.")

    args = message.content.split(' ')
    if args[0] != "olym":
        return

    mess = ""
    if len(args) >= 2 and args[1] == "hello":
        mess = "Hello, I am a test bot."

    if len(args) >= 3 and args[1] == "def":
        for i in range(2, min(len(args), 5)):
            word = args[i]
            mess = "```\n"
            if word in wordDatabase:
                mess += word + "\n"
                mess += wordDatabase[word]["short"] + "\n"
                mess += wordDatabase[word]["long"] + "\n"
                mess += "\n"
            else:
                page = vocs.getPage(word)
                mess += word + "\n"
                mess += vocs.getShortDefinition(page) + "\n"
                mess += vocs.getLongDefinition(page) + "\n"
            mess += "```"

    if len(args) >= 2 and args[1] == "register":
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

    if len(args) >= 2 and args[1] == "help":
        mess = "olym hello\nolym def <word>"

    if len(args) >= 2 and args[1] == "stop":
        mess = "You have been unregistered."
        stop_user(message.author)

    if len(args) == 3 and args[1] == "solve" and 1 <= status <= 5 and message.author in listOfUsers:
        if acceptingKeyword:
            if listOfUsers[message.author]["eliminate"]:
                mess = "You have been eliminated from this game."
            else:
                key_answer = args[2]
                await guess_keyword(message.author, key_answer)
        else:
            mess = "We are not accepting keyword answers. Please wait a little bit and try again."

    if mess != "":
        await message.author.send(mess)


token = os.environ['CLIENT_TOKEN']

client.run(token)
