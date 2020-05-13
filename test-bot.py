import discord
import json

client = discord.Client()

wordFile = open("wordDatabase.json","r")
wordDatabase = json.load(wordFile)

print(wordDatabase)

@client.event
async def on_message(message):
	if (message.author == client.user):
		return
	message.content = message.content.lower()
	args = message.content.split(' ')
	if (args[0]!="olym"):
	 	return
	if (len(args)>=2 and args[1] == "hello"):
		await message.channel.send("Hello, I am a test bot.")
	if (len(args)>=2 and args[1] == "help"):
	 	await message.channel.send("olym hello\nolym def <word>")

f = open("secret.txt","r")
token = f.read()
client.run(token)

