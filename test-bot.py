import discord


client = discord.Client()

@client.event
async def on_message(message):
	if (message.author == client.user):
		return
	message.content = message.content.lower()
	if (message.content.startswith("hello")):
		await message.channel.send("Hello, I am a test bot.")

client.run("NzA5OTE5NTMxODc0Nzc5MTg2.Xrs6aA.uG1a3fdXv4clu3_ry6eYDd6uwaI")

