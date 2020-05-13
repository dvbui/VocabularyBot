import discord
import json
import vocs
import asyncio
import random

# load word database
wordFile = open("wordDatabase.json","r")
wordDatabase = json.load(wordFile)
wordFile.close()

# game information
status = 0
keyWord = ""
clues = []
listOfUsers = {}
answers = {}

# constant
client = discord.Client()
bot_channel = client.get_channel(710081986466676757)

def registerUser(user):
	listOfUsers[user] = {"answer" : "", "score" : 0 }

def stopUser(user):
	listOfUsers.pop(user)
def gameIsRunning():
	return (1<=status and status<=5)

def pickKeyWord():
	word = ""
	clues = []
	while True:
		word, info = random.choice(list(wordDatabase.items()))
		if (wordDatabase[word]["short"]==""):
			continue
		
		suitable = []
		for clue in info["synonym"]:
			page = vocs.getPage(clue)
			if (vocs.getShortDefinition(page)!=""):
				suitable.append(clue)
		
		if (len(suitable)>=4):
			random.shuffle(suitable)
			clues = suitable[0:4]
			break
	return word, clues

async def main_game():
	await client.wait_until_ready()
	
	global status
	while True:
		channel = client.get_channel(710081986466676757)
		if (status==0): # Registering phase
			keyWord, clues = pickKeyWord()
			print(keyWord)
			print(clues)
			await channel.send("Registering phase")
			await asyncio.sleep(5)
			status+=1
		
		if (1<=status and status<=5): # During the game
			if (status<=4):
				answer = clues[status-1]
			else:
				answer = keyWord
			
			print(answer)
			question = ""
			if (answer in wordDatabase):
				question = wordDatabase[answer]["short"].lower()
			else:
				page = vocs.getPage(answer)
				question = vocs.getShortDefinition(page).lower()
			
			question = question.replace(answer,"."*len(answer))
			
			await channel.send(question)
			for user in listOfUsers:
				listOfUsers[user]["answer"] = ""
				await user.send(question)
			
			await asyncio.sleep(15)
			
			if (1<=status and status<=5):
				for user in listOfUsers:
					if (listOfUsers[user]["answer"] == answer):
						await user.send("Accepted")
						listOfUsers[user]["score"]+=1
					else:
						await user.send("Wrong Answer")

			status+=1
			
		if (status==6): # Puzzle is solved
			mess = "Puzzle solved - "
			mess += keyWord+"\n"
			mess += wordDatabase[keyWord]["long"]
			await channel.send(mess)
			status = 0

@client.event
async def on_ready():
	print("Bot is ready.")

@client.event
async def on_message(message):
	global status
	if (message.author == client.user):
		return
	if (message.author.bot):
		return;
	
	if (message.author in listOfUsers) and gameIsRunning():
		listOfUsers[message.author]["answer"] = message.content
		await message.author.send("Your current answer is "+message.content)

	message.content = message.content.lower()
	args = message.content.split(' ')
	if (args[0]!="olym"):
	 	return

	mess = "Placeholder"
	if (len(args)>=2 and args[1] == "hello"):
		mess = "Hello, I am a test bot."
	
	if (len(args)>=3 and args[1] == "def"):
		for i in range(2,min(len(args),5)):
			word = args[i]
			if (word in wordDatabase):
				mess+=word+"\n"
				mess+=wordDatabase[word]["short"]+"\n"
				mess+=wordDatabase[word]["long"]+"\n"
				mess+="\n"
			else:
				page=vocs.getPage(word)
				mess+=word+"\n"
				mess+=vocs.getShortDefinition(page)+"\n"
				mess+=vocs.getLongDefinition(page)+"\n"
	
	if (len(args)>=2 and args[1] == "register"):
		mess = "You have been registered."
		registerUser(message.author)
	
	if (len(args)>=2 and args[1] == "help"):
		mess = "olym hello\nolym def <word>"
	
	if (len(args)>=2 and args[1] == "stop"):
		mess = "You have been unregistered."
		stopUser(message.author)
	
	if (len(args)>=3 and args[1] == "solve" and 1<=status and status<=5 and message.author in listOfUsers):
		keyAnswer = ""
		for i in range(2,len(args)):
			keyAnswer+=args[i]+" "
		keyAnswer = keyAnswer[:-1]
		if (keyAnswer==keyWord.lower()):
			status = 0
			await bot_channel.send(str(message.author)+" "+"solved the puzzle")
			listOfUsers[message.author]["score"]+=8
			mess = "Puzzle solved"
		else:
		 	mess = "Puzzle is not solved\n"+keyAnswer+" "+keyWord.lower()
	
	await message.author.send(mess)


f = open("secret.txt","r")
token = f.read()
f.close()

client.loop.create_task(main_game())
client.run(token)

