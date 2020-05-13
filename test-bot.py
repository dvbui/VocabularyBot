import discord


client = discord.Client()

@client.event
async def on_message(message):
	if (message.author == client.user):
		return
	message.content = message.content.lower()
	if (message.content.startswith("hello")):
		await message.channel.send("Hello, I am a test bot.")

f = open("secret.txt","r")
token = f.read()
client.run(token)

