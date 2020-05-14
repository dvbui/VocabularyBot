import wordDef
import os
import discord
import json
import asyncio
import random
import messenger

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
bot_channel = client.get_channel(710081986466676757)


def register_user(user):
    global listOfUsers
    listOfUsers[user] = {"answer": "", "score": 0}


def stop_user(user):
    global listOfUsers
    listOfUsers.pop(user)


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
    global bot_channel
    while True:
        channel = client.get_channel(710081986466676757)
        if status == 0:  # Registering phase
            await channel.send(messenger.register_message())
            keyWord, clues = pick_keyword()
            await asyncio.sleep(5)
            status += 1

        if 1 <= status <= 5:  # During the game
            if status <= 4:
                answer = clues[status - 1][0]
            else:
                answer = keyWord

            print(answer)
            question = clues[status - 1][1]
            message_to_send = messenger.question_message(question, status, len(answer))
            await channel.send(message_to_send)
            for user in listOfUsers:
                listOfUsers[user]["answer"] = ""
                await user.send(message_to_send)

            await asyncio.sleep(15)

            if 1 <= status <= 5:
                for user in listOfUsers:
                    if listOfUsers[user]["answer"] == answer:
                        await user.send("Accepted")
                        listOfUsers[user]["score"] += 1
                    else:
                        await user.send("Wrong Answer")
                if status != 0:
                    status += 1
                await asyncio.sleep(5)

        if status == 6:  # Puzzle is solved
            mess = "Puzzle solved - "
            mess += keyWord + "\n"
            mess += wordDatabase[keyWord]["long"]
            await channel.send(mess)
            status = 0


@client.event
async def on_ready():
    print("Bot is ready.")


@client.event
async def on_message(message):
    global status
    global keyWord
    global clues
    if message.author == client.user:
        return
    if message.author.bot:
        return;

    if (message.author in listOfUsers) and is_game_running():
        listOfUsers[message.author]["answer"] = message.content
        await message.author.send("Your current answer is " + message.content)

    try:
        message.content = message.content.lower()
        args = message.content.split(' ')
        if args[0] != "olym":
            return

        mess = "Placeholder"
        if len(args) >= 2 and args[1] == "hello":
            mess = "Hello, I am a test bot."

        if len(args) >= 3 and args[1] == "def":
            for i in range(2, min(len(args), 5)):
                word = args[i]
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

        if len(args) >= 2 and args[1] == "register":
            mess = "You have been registered."
            register_user(message.author)

        if len(args) >= 2 and args[1] == "help":
            mess = "olym hello\nolym def <word>"

        if len(args) >= 2 and args[1] == "stop":
            mess = "You have been unregistered."
            stop_user(message.author)

        if len(args) >= 3 and args[1] == "solve" and 1 <= status <= 5 and message.author in listOfUsers:
            key_answer = ""
            for i in range(2, len(args)):
                key_answer += args[i] + " "
            key_answer = key_answer[:-1]
            if key_answer == keyWord.lower():
                status = 0
                listOfUsers[message.author]["score"] += 8
                mess = "Puzzle solved"
            else:
                mess = "Puzzle is not solved\n" + key_answer + " " + keyWord.lower()

        await message.author.send(mess)
    except:
        print("Error")


token = os.environ['CLIENT_TOKEN']

client.loop.create_task(main_game())
client.run(token)
