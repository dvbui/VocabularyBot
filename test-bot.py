import discord
import json
import vocs
import asyncio

client = discord.Client()

# load word database
wordFile = open("wordDatabase.json","r")
wordDatabase = json.load(wordFile)
wordFile.close()

listOfUsers = []
async def main_game():
	await client.wait_until_ready()
	print("I'm here")
	counter = 0
	while True:
		print("I'm here")
		counter+=1
		print(counter)
		await client.change_presence(game=discord.Game(name=str(counter)))
		for user in listOfUsers:
			await user.send(str(counter))
		await asyncio.sleep(1)

@client.event
async def on_ready():
	print("Bot is ready.")

@client.event
async def on_message(message):
	if (message.author == client.user):
		return
	if (message.author.bot):
		return;

	message.content = message.content.lower()
	args = message.content.split(' ')
	if (args[0]!="olym"):
	 	return
	
	mess = " "
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
		listOfUsers.append(message.author)
	
	if (len(args)>=2 and args[1] == "help"):
		mess = "olym hello\nolym def <word>"
	
	await message.author.send(mess)


f = open("secret.txt","r")
token = f.read()
f.close()

client.loop.create_task(main_game())
client.run(token)

