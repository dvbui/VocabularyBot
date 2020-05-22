import vocs
import wordDef
import os
import discord
import inflect
import asyncio
import random
import messenger
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
sys.setrecursionlimit(10 ** 6)
inflect = inflect.engine()

ADMIN_ID = 361217404296232961

# load new word list
WORD_LIST = "VinceGREWordListFormatted.txt"
wordDatabase = {}

db = None


def initialize_firebase():
    secret_url = os.environ["SECRET_URL"]
    os.system("curl {} --output serviceAccountKey.json".format(secret_url))
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    global db
    db = firestore.client()


def init_word_list():
    global wordDatabase
    new_word_file = open(WORD_LIST, "r")
    for line in new_word_file:
        wordDatabase[line.strip()] = {"long": ""}
    new_word_file.close()


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


def register_user(user, receive_message=True):
    global listOfUsers
    if not (user in listOfUsers):
        listOfUsers[user] = {
            "answer": "",
            "score": 0,
            "receive_message": True,
            "eliminate": False,
            "subgame_answer": "",
            "subgame_playing": False
        }
        listOfUsers[user]["activate"] = False
    listOfUsers[user]["receive_message"] = receive_message


def load_user_data():
    global listOfUsers
    listOfUsers = {}
    users_ref = db.collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        user = client.get_user(int(doc.id))
        if not (user is None):
            register_user(user)
            user_info = doc.to_dict()
            listOfUsers[user]["score"] = user_info["score"]
            listOfUsers[user]["receive_message"] = user_info["receive_message"]


def save_user_data():
    global db
    for user in listOfUsers:
        doc_ref = db.collection(u'users').document(str(user.id))
        doc_ref.set({
            u'score': listOfUsers[user]["score"],
            u'receive_message': listOfUsers[user]["receive_message"]
        })


def save_block():
    global listOfUsers
    global db
    global game_finished
    doc_ref = db.collection(u'blocks').document(str(game_finished))
    doc_ref.set({u'content': str(clues)})


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

    word_definition = ""
    while len(wordDatabase) > 0:
        word, info = random.choice(list(wordDatabase.items()))
        print(word+"\n"+str(info)+"\n"+str(len(wordDatabase))+"\n")

        if inflect.singular_noun(word):
            del wordDatabase[word]
            continue

        word_definition = wordDef.get_definition(word)
        info["long"] = word_definition
        if word_definition == "":
            del wordDatabase[word]
            continue

        details = wordDef.choose_questions(word, definition=word_definition)
        print(word)
        print(details)

        if details is None:
            continue
        else:
            break

    if len(wordDatabase) == 0:
        init_word_list()
        return pick_keyword()

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
        keyWord, clues = pick_keyword()
        await asyncio.sleep(30)
        m = messenger.rule_message()
        await send_message(channel, m, True)
        for user in listOfUsers:
            await send_message(user, m)
        await asyncio.sleep(60)
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

        global db
        doc_ref = db.collection("words").document(keyWord)
        doc_ref.set({"picked": True})

        await send_message(channel, mess, True)
        for user in listOfUsers:
            await send_message(user, mess)
            await send_message(user, "```Your current score is " + str(listOfUsers[user]["score"]) + "```")
            await send_message(user, messenger.ranklist_message(listOfUsers))
        await send_message(channel, messenger.ranklist_message(listOfUsers), True)
        status = 0
        save_user_data()
        save_block()
        if game_finished == 10:
            os.system("bash ./restart.sh")
            return

    await main_game()


@client.event
async def on_ready():
    print("Bot is ready.")
    initialize_firebase()
    load_user_data()
    init_word_list()
    global db
    messenger.init_message(db)
    await main_game()


async def guess_keyword(user, key_answer):
    global status
    if key_answer.lower() == keyWord.lower():
        score = max(1, (5 - status) * 2)
        listOfUsers[user]["score"] += score
        global winner
        winner = str(user)
        global acceptingKeyword
        acceptingKeyword = False
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


async def sub_game(author, channel, difficulty):
    global listOfUsers
    if not (author in listOfUsers):
        register_user(author, False)

    listOfUsers[author]["subgame_playing"] = True
    thinking_time = 0
    if difficulty == 1:
        thinking_time = 10
    if difficulty == 2:
        thinking_time = 15
    if difficulty == 3:
        thinking_time = 20
    question, answer, word = wordDef.generate_custom_question(difficulty)
    await send_message(channel, question, True)
    await send_message(channel, "Type olym answer [number] to answer this question", True)
    await send_message(channel, "You have {} seconds.".format(thinking_time), True)
    await asyncio.sleep(thinking_time)

    listOfUsers[author]["subgame_playing"] = False

    if listOfUsers[author]["subgame_answer"] != "":
        await send_message(channel, "Your final answer is {}".format(listOfUsers[author]["subgame_answer"]), True)
    else:
        await send_message(channel, "We did not receive any answer from you. 0 points.", True)
        return

    await asyncio.sleep(1)
    if listOfUsers[author]["subgame_answer"] == str(answer):
        listOfUsers[author]["score"] += difficulty
        await send_message(channel, "And that is the correct answer! You are awarded {} points.".format(difficulty), True)
    else:
        await send_message(channel, "That is not the correct answer. The correct answer is {}.".format(answer), True)
    listOfUsers[author]["subgame_answer"] = ""
    await send_message(channel, vocs.getLink(word), True)


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
        mess = "Exporting words failed. Please try again later."

    if len(args) == 2 and args[1] == "help":
        mess = messenger.help_message()

    if len(args) == 2 and args[1] == "recent":
        mess = "Exporting words failed. Please try again later."

    if len(args) == 3 and args[1] == "def" and args[2].isalpha():
        mess = "Exporting words failed. Please try again later."

    if len(args) == 3 and args[1] == "mega" and args[2] in ["1", "2", "3"]:
        if message.author in listOfUsers and listOfUsers[message.author]["subgame_playing"]:
            return
        await sub_game(message.author, message.channel, int(args[2]))
        return

    if len(args) == 3 and args[1] == "answer" and args[2] in ["1", "2", "3", "4"]:
        if message.author in listOfUsers and listOfUsers[message.author]["subgame_playing"]:
            print("I'm here")
            listOfUsers[message.author]["subgame_answer"] = args[2]
            await send_message(message.channel, "Your current answer is {}".format(args[2]), True)

    if len(args) == 2 and args[1] == "restart" and message.author.id == ADMIN_ID:
        os.system("bash ./restart.sh")

    if mess != "":
        await send_message(message.author, mess, True)


token = os.environ['CLIENT_TOKEN']

client.run(token)
