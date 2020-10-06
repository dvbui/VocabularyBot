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
import json
import pickle
import role_management
import game_music

from firebase_admin import credentials
from firebase_admin import firestore
sys.setrecursionlimit(10 ** 6)
inflect = inflect.engine()

ADMIN_ID = 361217404296232961

# load new word list
WORD_LIST = ["./words/playable.txt"]
wordDatabase = {}

db = None
message_cache = {}

# music
voice_client = None


async def init_voice_client():
    voice_channel = client.get_channel(709919416984273001)
    global voice_client
    voice_client = await voice_channel.connect()


def create_credential_file():
    dict = {
        "type": os.environ["FIREBASE_TYPE"],
        "project_id": os.environ["FIREBASE_PROJECT_ID"],
        "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
        "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
        "client_id": os.environ["FIREBASE_CLIENT_ID"],
        "auth_uri": os.environ["FIREBASE_AUTH_URI"],
        "token_uri": os.environ["FIREBASE_TOKEN_URI"],
        "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER"],
        "client_x509_cert_url": os.environ["FIREBASE_CLIENT_509"]
    }

    f = open("serviceAccountKey.json", "w")
    f.write(json.dumps(dict))
    f.close()


def initialize_firebase(create_file=True):
    if create_file:
        create_credential_file()
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)

    global db
    db = firestore.client()


def init_word_list():
    global wordDatabase
    for word_list in WORD_LIST:
        new_word_file = open(word_list, "r")
        for line in new_word_file:
            wordDatabase[line.strip()] = {"long": ""}
        new_word_file.close()


# game information
status = 0
keyWord = ""
clues = {}
listOfUsers = {}
oldListOfUsers = {}
answers = {}
wrong_keyWords = ""
winner = ""
acceptingAnswers = False
acceptingKeyword = False
game_finished = 0
max_number_of_games = 1
clock = 0
block_info = {}
# constant
client = discord.Client()


def register_user(user, receive_message=True):
    global listOfUsers
    if not (user in listOfUsers):
        listOfUsers[user] = {
            "answer": "",
            "score": 0,
            "receive_message": receive_message,
            "word_list": {},
            "eliminate": False,
            "subgame_answer": "",
            "subgame_playing": False,
        }
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
            if (not ("word_list" in user_info)) or (user_info["word_list"] == ""):
                listOfUsers[user]["word_list"] = {}
            else:
                listOfUsers[user]["word_list"] = pickle.loads(user_info["word_list"])

    global oldListOfUsers
    for user in listOfUsers:
        oldListOfUsers[user] = listOfUsers[user].copy()


def save_user_data():
    global db
    global oldListOfUsers
    print("Saving user data!\n")
    saved_all = True
    for user in listOfUsers:
        old_info = {"score": 0, "receive_message": False, "word_list": []}
        new_info = {"score": 1, "receive_message": True, "word_list": []}
        if user in oldListOfUsers:
            old_info["score"] = oldListOfUsers[user]["score"]
            new_info["score"] = listOfUsers[user]["score"]
            old_info["receive_message"] = oldListOfUsers[user]["receive_message"]
            new_info["receive_message"] = listOfUsers[user]["receive_message"]
            old_info["word_list"] = oldListOfUsers[user]["word_list"]
            new_info["word_list"] = listOfUsers[user]["word_list"]
        print(str(user)+"\n"+str(old_info)+"\n"+str(new_info))
        if (not (user in oldListOfUsers)) or old_info != new_info:
            try:
                doc_ref = db.collection(u'users').document(str(user.id))
                doc_ref.set({
                    u'score': listOfUsers[user]["score"],
                    u'receive_message': listOfUsers[user]["receive_message"],
                    u'word_list': pickle.dumps(listOfUsers[user]["word_list"])
                })
            except:
                saved_all = False
                print("Can't save user {} data".format(str(user)))

    if saved_all:
        for user in listOfUsers:
            oldListOfUsers[user] = listOfUsers[user].copy()
    else:
        global game_finished
        game_finished = min(game_finished, max_number_of_games-1)


def save_block():
    global listOfUsers
    global db
    global game_finished
    try:
        doc_ref = db.collection(u'blocks').document(str(game_finished))
        doc_ref.set({u'content': pickle.dumps(clues)})
        block_info[game_finished] = clues
    except:
        print("Can't save block data!")


def load_block():
    global db
    for i in range(1, 11):
        if not (i in block_info):
            try:
                doc_ref = db.collection(u'blocks').document(str(i))
                doc = doc_ref.get()
                if doc.exists:
                    doc = doc.to_dict()
                    block_info[i] = pickle.loads(doc["content"])
                    pass
                else:
                    print("Cannot load block")
            except:
                print("Cannot load block")

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
    global wordDatabase
    if len(wordDatabase) == 0:
        init_word_list()

    while len(wordDatabase) > 0:
        word, info = random.choice(list(wordDatabase.items()))
        del wordDatabase[word]
        word, clue_list = wordDef.pick_question(word)
        if word is None:
            continue
        else:
            return word, clue_list

    if len(wordDatabase) == 0:
        init_word_list()
        return pick_keyword()


async def send_message(user, message, special=False):
    if special or ((user in listOfUsers) and listOfUsers[user]["receive_message"]):
        try:
            message = message[0:min(len(message), 2000)]
            print(str(user) + " " + str(message))
            await user.send(message)
        except:
            print("Can't send message")


async def play_music(file_name, retry=3):
    global voice_client
    music = discord.FFmpegPCMAudio(file_name)
    while retry > 0:
        try:
            voice_client.play(music)
            break
        except discord.ClientException:
            if voice_client.is_playing():
                voice_client.stop()
            else:
                await voice_client.disconnect()
                await init_voice_client()
            retry -= 1


async def main_game():
    await client.wait_until_ready()

    global status
    global keyWord
    global clues
    global wrong_keyWords
    global winner
    global acceptingAnswers, acceptingKeyword
    channel = client.get_channel(710081986466676757)
    global voice_client

    if client.is_closed():
        return

    if status == 0:  # Registering phase
        initialize_firebase(False)
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

        # wait_music
        await play_music("./music/30s.mp3")

        await asyncio.sleep(32)

        # rule_music
        m = messenger.rule_message()
        await send_message(channel, m, True)
        for user in listOfUsers:
            await send_message(user, m)
        await play_music("./music/32s.mp3")
        await asyncio.sleep(33)

        # block_buster_opening
        await play_music("./music/opening.mp3")
        await asyncio.sleep(13)

        # open hint
        await send_message(channel, messenger.keyword_message(len(keyWord)), True)
        for user in listOfUsers:
            await send_message(user, messenger.keyword_message(len(keyWord)))
        await play_music("./music/open_hint.mp3")
        await asyncio.sleep(15)

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
        clock = 20
        await play_music('./music/20s.mp3')
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

            user_answers = messenger.show_user_answer(fake_list, answer, question)
            for user in listOfUsers:
                await send_message(user, user_answers)
            await send_message(channel, user_answers, True)
            await play_music("./music/answers.mp3")
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
                        if similarity != 0:
                            listOfUsers[user]["score"] += similarity
                        m += "You get {} points for your answer.".format(similarity)
                        m += " The correct answer is {} ".format(answer)

                    await send_message(user, m)

            if 1 <= status <= 5:
                status += 1
                await asyncio.sleep(1)

    if status == 6:  # Puzzle is solved
        global game_finished
        game_finished += 1
        acceptingKeyword = False
        acceptingAnswers = False
        mess = messenger.block_end_message(keyWord, winner)

        await send_message(channel, mess, True)
        for user in listOfUsers:
            await send_message(user, mess)
            await send_message(user, "```Your current score is " + str(listOfUsers[user]["score"]) + "```")
            await send_message(user, messenger.ranklist_message(listOfUsers))
        await send_message(channel, messenger.ranklist_message(listOfUsers), True)
        status = 0
        save_block()
        save_user_data()
        print("Finished {}".format(game_finished))
        ## await role_management.update_roles(client, db, listOfUsers)
        if game_finished == max_number_of_games:
            os.system("bash ./restart.sh")
            return

    await main_game()


@client.event
async def on_member_join(member):
    print("I'm here")

    server_id = member.guild.id
    purpose = "welcome_message"

    mess = ""

    if (server_id in message_cache) and (purpose in message_cache[server_id]):
        mess = message_cache[server_id][purpose]
    else:
        message_cache[server_id] = {}
        try:
            global db
            doc = db.collection(u'messages').document(str(server_id)).get()
            if doc.exists:
                doc = doc.to_dict()
                if ("welcome_channel" in doc) and (purpose in doc):
                    message_cache[server_id][purpose] = doc[purpose].replace("\\n", "\n")
                    message_cache[server_id]["welcome_channel"] = doc["welcome_channel"]
                    mess = message_cache[server_id][purpose]
        except:
            print("Cannot retrieve welcome message")

    mess = mess.replace("{user}", str(member))

    if mess == "":
        print("Mess is empty")
        return

    print(mess)

    try:
        welcome_channel_id = message_cache[server_id]["welcome_channel"]
        global client
        channel = client.get_channel(int(welcome_channel_id))
        await send_message(channel, mess, True)
    except:
        print("Cannot send message")


@client.event
async def on_ready():
    print("Bot is ready.")
    init_word_list()
    wordDef.init_swear_words_file()
    initialize_firebase()
    load_user_data()
    global db
    messenger.init_message(db)
    ## role_management.init_roles(client, db)
    game_music.load_opus_lib()
    await init_voice_client()
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
        mess = "Blockbusted. Everyone is eliminated!\n"
        mess += "You gain {} points for your keyword answer".format(score)
        status = 6
    else:
        similarity = 0
        if len(key_answer) == len(keyWord):
            similarity = wordDef.get_similarity(key_answer, "", keyWord)
        score = max(1, (5 - status) * 2) * similarity
        if score != 0:
            listOfUsers[user]["score"] += score
        mess = "Failed blockbusting attempt.\n"
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
    question, answer, word = wordDef.generate_custom_antonym(difficulty)
    await send_message(channel, question, True)
    await send_message(channel, "Type olym answer [number] to answer this question", True)
    await send_message(channel, "You have {} seconds.".format(thinking_time), True)
    await asyncio.sleep(thinking_time)

    listOfUsers[author]["subgame_playing"] = False

    if listOfUsers[author]["subgame_answer"] != "":
        await send_message(channel, "Your final answer is {}".format(listOfUsers[author]["subgame_answer"]), True)
    else:
        await send_message(channel, "We did not receive any answer from you. 0 points.", True)
        await send_message(channel, vocs.getLink(word), True)
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
                                                                0:min(len(message.content), len(clues[status - 1][0]))]
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
        if status == 0:
            await send_message(message.author, messenger.register_message())

    if len(args) == 2 and args[1] == "stop":
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

    if len(args) in [2, 3] and (args[1] == "export" or args[1] == "recent"):
        if len(args) == 2:
            load_block()
            for i in block_info:
                for j in range(0, len(block_info[i])):
                    mess += block_info[i][j][0]+" "
                mess += "\n"

        if len(args) == 3:
            load_block()
            for i in block_info:
                for j in range(0, len(block_info[i])):
                    mess += block_info[i][j][0]+"\t"+block_info[i][j][1]+"\n"

        mess = "```\n"+mess+"```"
        mess = mess[0:min(len(mess), 2000)]
        if mess != "":
            await send_message(message.channel, mess, True)
            return

    if len(args) == 2 and args[1] == "help":
        mess = messenger.help_message()
        if mess != "":
            await send_message(message.channel, mess, True)
            return

    if len(args) == 3 and args[1] == "def" and args[2].isalpha():
        mess = vocs.getLink(args[2])
        if mess != "":
            await send_message(message.channel, mess, True)
            return

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
            return

    if len(args) == 2 and args[1] == "restart" and message.author.id == ADMIN_ID:
        os.system("bash ./restart.sh")

    if len(args) == 5 and args[1] == "add_roles":
        server_id = message.guild.id
        author_id = message.author.id

        def to_role_id(s):
            s = s.replace('<', '')
            s = s.replace('&', '')
            s = s.replace('@', '')
            s = s.replace('>', '')
            return int(s)

        role_id = 0
        try:
            role_id = to_role_id(args[2])
        except:
            print(args[2])
            print("Invalid role id")
            return

        try:
            role_management.add_role(db, server_id, author_id, role_id, float(args[3]), float(args[4]))
        except:
            print("Invalid parameters")

    if len(args) >= 3 and args[1] == "suggest":
        not_detected = {}
        detected = {}
        already_in = {}
        user = message.author
        if not (user in listOfUsers):
            register_user(user, False)
        for i in range(2, len(args)):
            words = args[i].lower().replace(',', '').split('\n')
            for word in words:
                word = word.strip()
                cond = word.isalpha() and wordDef.get_definition(word) != ""
                print(word+"\n"+wordDef.get_definition(word))
                cond = cond and not (wordDef.generate_custom_antonym(chosen_word=word)[0] is None)
                if cond:
                    if not (word in listOfUsers[user]["word_list"]):
                        detected[word] = ""
                        listOfUsers[user]["word_list"][word] = {"mastery_level": 0,
                                                                "streak": 0,
                                                                "removed": False,
                                                                "banned": 0}
                    else:
                        already_in[word] = ""
                else:
                    not_detected[word] = ""

        await send_message(message.channel, "Added {} to your dictionary.".format(detected.keys()), True)
        await send_message(message.channel, "{} are already in your dictionary".format(already_in.keys()), True)
        if len(not_detected) > 0:
            mess = "The following words are not supported by the system\n"
            begin = True
            for word in not_detected:
                if not begin:
                    mess += ", "
                begin = False
                mess += word
            await send_message(message.channel, mess, True)
        return

    if mess != "":
        await send_message(message.author, mess, True)


token = os.environ['CLIENT_TOKEN']

print(token)

client.run(token)
