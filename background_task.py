import discord
import asyncio


class MyClient(discord.Client):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kargs)
		self.listOfUsers = []
		self.bg_task = self.loop.create_task(self.my_background_task())
	
	def registerUser(self,user):
		self.listOfUsers.append(user)
	
	async def my_background_task(self):
		await self.wait_until_ready()
		counter = 0
		for counter in range(0,100):
			if self.is_closed():
				break
			await channel.send(str(counter))
			await asyncio.sleep(15)
