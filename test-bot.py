import discord
import json
import vocs

client = discord.Client()

# load word database
wordFile = open("wordDatabase.json","r")
wordDatabase = json.load(wordFile)
wordFile.close()


@client.event
async def on_message(message):
	if (message.author == client.user):
		return
	message.content = message.content.lower()
	args = message.content.split(' ')
	if (args[0]!="olym"):
	 	return
	
	mess = ""
	if (len(args)>=2 and args[1] == "hello"):
		mess = "Hello, I am a test bot."
	
	if (len(args)>=3 and args[1] == "def"):
	 	for i in range(2,len(args)):
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
	
	if (len(args)>=2 and args[1] == "help"):
	 	mess = "olym hello\nolym def <word>"
	
	
	await message.channel.send(mess)

f = open("secret.txt","r")
token = f.read()
client.run(token)

