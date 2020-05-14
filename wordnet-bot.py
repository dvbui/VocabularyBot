import discord
import json
import asyncio
import random
import time
import nltk
from nltk.corpus import wordnet
import wordDef
import os

# load word database
wordFile = open("wordDatabase.json","r")
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

def registerUser(user):
	global listOfUsers
	listOfUsers[user] = {"answer" : "", "score" : 0 }

def stopUser(user):
	global listOfUsers
	listOfUsers.pop(user)

def gameIsRunning():
	global status
	return (1<=status and status<=5)



def pickKeyWord():
	word = ""
	clues = []
	while True:
		word, info = random.choice(list(wordDatabase.items()))	
		details = wordDef.chooseQuestions(word)
		print(word)
		print(details)
		if (details == None):
			continue	
		else:
			break
	for k in details:
		clues.append( (k,details[k]) )
	clues.append((word,wordDef.getDefinition(word)))

	return word, clues

async def main_game():
	await client.wait_until_ready()
	
	global status
	global keyWord
	global clues
	global bot_channel
	while True:
		channel = client.get_channel(710081986466676757)
		if (status==0): # Registering phase
			await channel.send("Registering phase")
			keyWord, clues = pickKeyWord()
			await asyncio.sleep(5)
			status+=1
		
		if (1<=status and status<=5): # During the game
			if (status<=4):
				answer = clues[status-1][0]
			else:
				answer = keyWord
			
			print(answer)
			question = clues[status-1][1]
			
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
				if (status!=0):
					status+=1
				await asyncio.sleep(5)
			
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
	global keyWord
	global clues
	if (message.author == client.user):
		return
	if (message.author.bot):
		return;
	
	if (message.author in listOfUsers) and gameIsRunning():
		listOfUsers[message.author]["answer"] = message.content
		await message.author.send("Your current answer is "+message.content)
	
	try:
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
				listOfUsers[message.author]["score"]+=8
				mess = "Puzzle solved"
			else:
				mess = "Puzzle is not solved\n"+keyAnswer+" "+keyWord.lower()
		
		await message.author.send(mess)
	except:
		print("Error")


token = os.environ['CLIENT_TOKEN']


client.loop.create_task(main_game())
client.run(token)

