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


async def main_game():
    await client.wait_until_ready()

    global status
    global keyWord
    global clues
    while True:
        channel = client.get_channel(710081986466676757)
        if status == 0:  # Registering phase
            load_user_data()
            free_all_users()
            m = messenger.register_message()
            await channel.send(messenger.register_message())
            for user in listOfUsers:
                if listOfUsers[user]["receive_message"]:
                    await user.send(m)
            keyWord, clues = pick_keyword()
            await asyncio.sleep(30)
            await channel.send(messenger.keyword_message(len(keyWord)))
            for user in listOfUsers:
                if listOfUsers[user]["receive_message"]:
                    await user.send(messenger.keyword_message(len(keyWord)))
            status += 1

        if 1 <= status <= 5:  # During the game
            if status <= 4:
                answer = clues[status - 1][0]
            else:
                answer = keyWord

            print(answer)
            question = clues[status - 1][1]
            message_to_send = messenger.question_message(question, status, len(answer))
            message_to_send += messenger.keyword_message(len(keyWord))
            await channel.send(message_to_send)
            for user in listOfUsers:
                listOfUsers[user]["answer"] = ""
                if not listOfUsers[user]["receive_message"]:
                    continue
                await user.send(message_to_send)

            await asyncio.sleep(15)

            if 1 <= status <= 5:
                for user in listOfUsers:
                    if not listOfUsers[user]["receive_message"]:
                        continue
                    if listOfUsers[user]["eliminate"]:
                        await user.send("The correct answer is "+answer+".")
                        continue
                    user_answer = listOfUsers[user]["answer"]
                    if user_answer == "":
                        m = "We did not receive any answer. 0 points.\nThe correct answer is " + answer
                        await user.send(m)
                    else:
                        await user.send("Your final answer is {}.".format(user_answer))
                        if listOfUsers[user]["answer"] == answer:
                            await user.send("And that is the correct answer. You get 1 point.")
                            listOfUsers[user]["score"] += 1
                        else:
                            similarity = 0
                            if len(listOfUsers[user]["answer"]) == len(answer):
                                similarity = wordDef.get_similarity(answer, question, listOfUsers[user]["answer"])

                            listOfUsers[user]["score"] += similarity
                            m = "You only get {} points for your answer. The correct answer is {} ".format(similarity, answer)
                            await user.send(m)
                if status != 0:
                    status += 1
                await asyncio.sleep(5)

        if status == 6:  # Puzzle is solved
            mess = messenger.block_end_message(keyWord, wordDatabase[keyWord]["long"])
            await channel.send(mess)
            for user in listOfUsers:
                if not listOfUsers[user]["receive_message"]:
                    continue
                await user.send(mess)
                await user.send("```Your current score is "+str(listOfUsers[user]["score"])+"```")
                await user.send(messenger.ranklist_message(listOfUsers))
            save_user_data()
            await channel.send(messenger.ranklist_message(listOfUsers))
            status = 0

        if status < 0 or status > 6:
            status = 0
            await channel.send("Something is wrong! Restarting game.")
            for user in listOfUsers:
                if listOfUsers[user]["receive_message"]:
                    await user.send("Something is wrong! Restarting game.")


@client.event
async def on_ready():
    print("Bot is ready.")
    load_user_data()
    client.loop.create_task(main_game())


@client.event
async def on_message(message):
    global status
    global keyWord
    global clues
    if message.author == client.user:
        return
    if message.author.bot:
        return

    try:
        message.content = message.content.lower()
        if (message.author in listOfUsers) and is_game_running() and (not message.content.startswith("olym ")):
            if listOfUsers[message.author]["eliminate"]:
                await message.author.send("You have been eliminated from the game.")
            else:
                listOfUsers[message.author]["answer"] = message.content
                await message.author.send("Your current answer is " + message.content)

        args = message.content.split(' ')
        if args[0] != "olym":
            return

        mess = "Placeholder"
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

        if len(args) >= 3 and args[1] == "solve" and 1 <= status <= 5 and message.author in listOfUsers:
            if listOfUsers[message.author]["eliminate"]:
                mess = "You have been eliminated from this game."
            else:
                key_answer = ""
                for i in range(2, len(args)):
                    key_answer += args[i] + " "
                key_answer = key_answer[:-1]
                if key_answer == keyWord.lower():
                    listOfUsers[message.author]["score"] += 8
                    mess = "Puzzle solved. Everyone is eliminated!\n"
                    mess += "You gained 8 points for your keyword answer"
                    status = 6
                else:
                    similarity = 0
                    if len(key_answer) == len(keyWord):
                        similarity = wordDef.get_similarity(key_answer, "", keyWord)
                    score = 8*similarity
                    listOfUsers[message.author]["score"] += score
                    mess = "Puzzle is not solved.\n"
                    mess += "You get {} points for your answer.".format(score)+"\n"
                    mess += "You have been eliminated from the game."
                listOfUsers[message.author]["eliminate"] = True

        await message.author.send(mess)
    except:
        print("Error")


token = os.environ['CLIENT_TOKEN']

client.run(token)
