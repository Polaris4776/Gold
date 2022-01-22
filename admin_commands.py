import discord
import os
import asyncio
from replit import db
from discord.ext import tasks
import random
from datetime import datetime
import pytz


TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
prefixe = "?"



white = 16775930





def get_mention(message, args) : # Retourne la première mention ou le premier nom d'utilisateur dans le message (pas forcément correct)
	if len(message.mentions) == 0 : # Il n'y a pas de @mention
		if len(args) > 0 : 
			for arg in args : 
				if "#" in str(arg) : 
					ls_arg = list(arg)
					if ls_arg[-5] == "#" : 
						return arg
		return None
	
	else : 
		return message.mentions[0]


def create_user(self, UserToCreate) : 
	try : 
		if UserToCreate.bot : 
			return
	except AttributeError : # Ce n'est pas une variable Discord.Member
		pass

	UserToCreate = str(UserToCreate)
	parcour = [0, 1, 2, 3, 5, 9, 10] # Daily, Hebdo, Gold, Daily, Steal
	users = db.keys()

	for i in parcour : 
		if not self.prefixes[i] + UserToCreate in users : 
			db[self.prefixes[i] + UserToCreate] = "0"
	
	if not self.prefixes[6] + UserToCreate in users : # Items
		db[self.prefixes[6] + UserToCreate] = "11-1"












class commands : 
	def __init__(self, message, prefixes) : 
		self.message = message
		self.content = message.content
		self.author = message.author
		self.channel = message.channel
		self.client = client
		self.user_id = message.author.id
		self.prefixes = prefixes
	

	async def delete(self, notation,  args) : 
		cible = None
		if len(self.message.mentions) == 0 : # IL n'y a pas de @mention
			if len(args) > 0 : 
				for arg in args : 
					if "#" in str(arg) : 
						ls_arg = list(arg)
						if ls_arg[-5] == "#" : 
							cible = arg
		
		else : 
			cible = self.message.mentions[0]
		cible = str(cible)

		create_user(self, cible)
		
		to_delete = cible
		users = db.keys()
		found = False
		for user in users : 
			if to_delete in user : 
				del db[user]
				found = True
		
		if found : 
			embed = discord.Embed(title=f"{to_delete} supprimé avec succès !", description="", color=white)
			await self.channel.send(embed=embed)
		if not(found) : 
			embed = discord.Embed(title=f"{to_delete} n'a pas été trouvé dans la base de données !", description="", color=white)
			await self.channel.send(embed=embed)
	

	async def remove_my_data(self, notation, args) : 	
		cible = str(self.author)

		users = db.keys()

		exist = False
		for user in users : 
			for prefix in self.prefixes :
				if prefix in user : 
					user = user.replace(prefix, "")
					if cible in user : 
						exist = True
		
		if exist : 
			for user in users : 
				if cible in user : 
					del db[user]
			embed = discord.Embed(title="Compte supprimé avec succès !", description="", color=white)
			await self.channel.send(embed=embed)
		else : 
			embed = discord.Embed(title="Vous ne pouvez pas supprimer votre compte car vous n'existez pas encore.", description="", color=white)
			await self.channel.send(embed=embed)
	

	async def reset_data(self, notation, args) : 
		if len(args) == 0 : 
			embed = discord.Embed(title=f"Merci de faire ```{notation}```", description="Entrez le numéro de *prefixes*", color=white)
			await self.channel.send(embed=embed)
			return

		users = db.keys()
		
		for user in users : 
			if user.startswith(self.prefixes[args[0]]) : 
				del db[user]
		embed = discord.Embed(title="Variable supprimée avec succès !", description="", color=white)
		await self.channel.send(embed=embed)
	

	async def blockgold(self, notation, args) : 
		cible = str(get_mention(self.message, args))

		if cible != "None" : 
			create_user(self, cible)

		if cible == "None" :
			embed = discord.Embed(title=f"Merci de faire ```{notation}```", description="Bloquer définitivement l'accès à Gold.", color=white)
			await self.channel.send(embed=embed)
			return

		users = db.keys()

		db[self.prefixes[7] + cible] = "True"

		embed = discord.Embed(title=f"Compte bannis !", description="", color=white)
		await self.channel.send(embed=embed)
	

	async def unblockgold(self, notation, args) : 
		cible = str(get_mention(self.message, args))

		if cible != "None" : 
			create_user(self, cible)

		if cible == "None" :
			embed = discord.Embed(title=f"Merci de faire ```{notation}```", description="Débloquer l'accès à Gold.", color=white)
			await self.channel.send(embed=embed)
			return

		users = db.keys()


		try : 
			del db[self.prefixes[7] + cible]
		except KeyError : 
			embed = discord.Embed(title=f"Ce compte n'étais pas bannis !", description="", color=white)
			await self.channel.send(embed=embed)
		else : 
			embed = discord.Embed(title=f"Compte débannis !", description="", color=white)
			await self.channel.send(embed=embed)