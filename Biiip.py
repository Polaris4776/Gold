import discord
import os
import asyncio
from replit import db
from discord.ext import tasks
import random

"""Commandes spéciales : 
?delete
"""


TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
prefixe = "?"

# reset = input("Voulez-vous reset les scores ? Y/N : ")
# reset = reset.lower()
# if reset == "y" : 
# 	users = db.keys()
# 	for user in users : 
# 		del (db[user])
# 	print("Deleted :)")
# else : 
# 	print("Not deleted :)")



def create_user(UserToCreate) : 
	UserToCreate = str(UserToCreate)
	parcour = [0, 1, 2, 3, 5] # Daily, Hebdo, Gold, Daily, Steal
	users = db.keys()

	for i in parcour : 
		if not prefixes[i] + UserToCreate in users : 
			db[prefixes[i] + UserToCreate] = "0"
			print(f"Created user {prefixes[i] + UserToCreate}")


def timer_edit(user, prefixe_num) : 
	if not (user.startswith(prefixe_num)) :
		return
	var = int(db[user])

	if var == 0 :
		return # On est prêt à faire la commande !
	else : 
		db[user] = var - 1 # On s'approche du moment prêt de 1 heure !


def report_edit(user) : 
	if not (user.startswith(prefixes[4])) :
		return
	var = db[user]
	ls = var.split("|")
	ls[0] = int(ls[0])

	if ls[0] == 0 :
		return # On est prêt à faire la commande !
	else : 
		db[user] = f"{ls[0] - 1}|{ls[1]}" # On s'approche du moment prêt de 1 heure !


async def wait_for_message(channel, author, client) : # En attente d'un message dans le même salon.
	def check(m) : 
		return (m.channel == channel) and (m.content != "") and (m.author == author) and (author != client.user)

	msg = await client.wait_for("message", check=check)

	return msg








num_identity = 0

prefixes = ["←+→", "-@_@-", "°-°", "-_-", "+_+", "X_X"] # ←+→ : daily 	-@_@- : hebdo		°-° : gold		-_- : beg		+_+ : steal ready to report		X_X : steal





second = 1
minute = second * 60
hour = minute * 60
day = hour * 24


white = 16775930





# users = db.keys()
# for user in users : 
# 	if user.startswith("°-°") : 
# 		db[prefixes[3] + user.replace("°-°", "")] = 0







@tasks.loop(seconds=second) # 1 minute d'attente entre chaque execution de def
async def temps():
	users = db.keys()
	for user in users : 
		timer_edit(user, prefixes[0]) # On retire 1 minute au temps restant avant que daily soit dispo
		timer_edit(user, prefixes[1]) # On retire 1 minute au temps restant avant que hebdo soit dispo
		timer_edit(user, prefixes[3]) # On retire 1 minute au temps restant avant que beg soit dispo
		timer_edit(user, prefixes[5]) # On retire 1 minute au temps restant avant que steal soit dispo
		report_edit(user)



@client.event
async def on_ready():
	print("Je me suis connecté en {0.user}".format(client))
	
	temps.start()



@client.event
async def on_message(message) :
	content = message.content
	author = message.author
	channel = message.channel
	
	create_user(str(author))

	if author == client.user :
		return

	elif content.startswith(prefixe + "help") :
		with open("help.txt", "r") as lg : 
			Lines = lg.readlines()
			commandes = []
			descriptif = []
			line_number = 1
			for line in Lines : 
				if line_number % 2 == 0 : 
					if line.strip() == "" : 
						continue
					descriptif.append(line.strip().replace("{prefixe}", prefixe))
				else : 
					if line.strip() == "" : 
						continue
					
					commandes.append(line.strip().replace("{prefixe}", prefixe))
				line_number += 1

		embed = discord.Embed(title="Commandes possibles : ", description="", color=white)
		for i in range(len(commandes)):
			embed.add_field(name=f"{commandes[i]}", value=f"{descriptif[i]}")
		await channel.send(embed=embed)
	

	elif content.startswith(prefixe + "gold") :
		users = db.keys()
		if len(message.mentions) == 0 :
			gold_dans_db = prefixes[2] + str(author)

			embed = discord.Embed(title="Tu as {} gold.".format(db[gold_dans_db]), description="", color=white)
			await channel.send(embed=embed)
		else : 
			cible_user = message.mentions[0]
			gold_dans_db = prefixes[2] + str(cible_user)

			embed = discord.Embed(title="Cette personne a {} gold.".format(db[gold_dans_db]), description="", color=white)
			await channel.send(embed=embed)
	

	elif content.startswith(prefixe + "give") :
		users = db.keys()

		if len(message.mentions) == 0 :
			embed = discord.Embed(title="Merci de faire {} @user [valeur]".format(prefixe + "give"), description="", color=white)
			await channel.send(embed=embed)
			return
		cible_user = message.mentions[0]
		gold_dans_db_for_author = prefixes[2] + str(author)
		gold_dans_db_for_cible = prefixes[2] + str(cible_user)

		gold_of_author = int(db[gold_dans_db_for_author])
		gold_of_cible = int(db[gold_dans_db_for_cible])

		var = str(message.content)
		var = var.replace(prefixe + "give", "")
		var = var.strip()
		var = var.split(" ")
		print(var)
		embed = discord.Embed(title="Merci de m'envoyer la valeur du transfert : ", description=f"Votre argent : {gold_of_author}", color=white)
		await channel.send(embed=embed)

		msg = await wait_for_message(channel, author, client)
		valeur = msg.content
		valeur = int(str(valeur).strip())

		if not (((gold_of_author - valeur) > 0) or ((gold_of_author - valeur) == 0)) : # Trop pauvre !
			embed = discord.Embed(title=f"Vous ne possédez pas suffisament d'argent pour envoyer {valeur} à {cible_user}", description="", color=white)
			await channel.send(embed=embed)
			return
		else : # Suffisament riche !
			db[gold_dans_db_for_author] = str(gold_of_author - valeur) # On retire l'argent à l'auteur
			db[gold_dans_db_for_cible] = str(gold_of_cible + valeur) # Ajoute l'argent à la cible
			embed = discord.Embed(title="⇄ Transfert effectué : ", description=f"{author} : **{gold_of_author}** - {valeur} = **{gold_of_author - valeur}**\n⇄\n{cible_user} : **{gold_of_cible}** + {valeur} = **{gold_of_cible + valeur}**", color=white)
			await channel.send(embed=embed)


	elif content.startswith(prefixe + "rank gold") : 
		users = db.keys()
		all_users = []
		for user in users : 
			if user.startswith(prefixes[2]) : 
				all_users.append(str(user.replace(prefixes[2], "")))

		value_of_all_users = []
		for user in all_users : 
			value_of_all_users.append(int(db[str(prefixes[2] + user)]))
		dict_all_users = {}

		for i in range(len(all_users)) : 
			dict_all_users[all_users[i]] = value_of_all_users[i]
		
		tri = reversed(sorted(dict_all_users.items(), key=lambda t: t[1])) # Trié dans l'ordre croissant

		to_print = ""
		i = 0
		for user in tri : 
			if i == 0 : 
				to_print += "🥇"
			elif i == 1 :
				to_print += "🥈"
			elif i == 2 :
				to_print += "🥉"
			elif i == 3 : # Fin du top 3
				to_print += "\n" + "▬" * 10 + "\n\n"

			to_print += f"**{user[0]}** : {user[1]}\n"
			i += 1
		
		embed = discord.Embed(title="🏆 Classement : ", description=f"{to_print}", color=white)
		await channel.send(embed=embed)


	elif content.startswith(prefixe + "beg"):
		users = db.keys()
		beg_dans_db = prefixes[3] + str(author)
		gold_dans_db = prefixes[2] + str(author)

		if int(db[beg_dans_db]) == 0 :
			rand = random.randint(1, 2)
			if rand == 1 : 
				rand = 50
			if rand == 2 : 
				rand = 100

			db[gold_dans_db] = int(db[gold_dans_db]) + rand
			db[beg_dans_db] = 5 # minute a attendre
			embed = discord.Embed(title="Tu as mendié un peu d'argent", description=f"+{rand} gold", color=white)
			await channel.send(embed=embed)
			
		elif int(db[beg_dans_db]) > 0:
			minute = db[beg_dans_db]
			embed = discord.Embed(title=f"Tu dois encore attendre {minute} minutes avant de mendier à nouveau.", description="", color=white)
			await channel.send(embed=embed)


	elif content.startswith(prefixe + "daily"):
		users = db.keys()
		daily_dans_db = prefixes[0] + str(author)
		gold_dans_db = prefixes[2] + str(author)
	
		if int(db[daily_dans_db]) == 0 :
			db[gold_dans_db] = int(db[gold_dans_db]) + 700
			db[daily_dans_db] = 1439
			embed = discord.Embed(title="Tu as récupéré ta récompense journalière.", description="+700 gold", color=white)
			await channel.send(embed=embed)
			
		elif int(db[daily_dans_db]) > 0:
			minute = db[daily_dans_db]
			heure = minute // 60
			embed = discord.Embed(title=f"Tu dois encore attendre {heure}h {minute % 60}min.", description="", color=white)
			await channel.send(embed=embed)


	elif content.startswith(prefixe + "hebdo"):
		users = db.keys()
		hebdo_dans_db = prefixes[1] + str(author)
		gold_dans_db = prefixes[2] + str(author)
		
		if int(db[hebdo_dans_db]) == 0:
			db[gold_dans_db] = int(db[gold_dans_db]) + 1100
			db[hebdo_dans_db] = 10079
			embed = discord.Embed(title="Tu as récupéré ta récompense hebdomadaire.", description="+1100 gold", color=white)
			await channel.send(embed=embed)
		elif int(db[hebdo_dans_db]) > 0 :
			minute = db[hebdo_dans_db]
			heure = minute // 60
			jour = heure // 24
			embed = discord.Embed(title=f"Tu dois encore attendre {jour}j {heure % 24}h {minute % 60}min.", description="", color=white)
			await channel.send(embed=embed)


	elif content.startswith(prefixe + "delete") :
		if not(str(author) == "Polaris#4776") : 
			return
		if len(message.mentions) == 0 :
			embed = discord.Embed(title="Merci de faire {} @user".format(prefixe + "delete"), description="", color=white)
			await channel.send(embed=embed)
			return
		
		to_delete = str(message.mentions[0])
		print(to_delete)
		users = db.keys()
		for user in users : 
			if to_delete in user : 
				del db[user]
		
		embed = discord.Embed(title=f"{to_delete} supprimé avec succès !", description="", color=white)
		await channel.send(embed=embed)


	elif content.startswith(prefixe + "steal") :
		if not(str(author) == "Polaris#4776") : 
			return
		
		if len(message.mentions) == 0 :
			embed = discord.Embed(title="Merci de faire {} @user".format(prefixe + "steal"), description="", color=white)
			await channel.send(embed=embed)
			return

		cible = message.mentions[0]
		users = db.keys()

		gold_dans_db_for_author = prefixes[2] + str(author)
		gold_dans_db_for_cible = prefixes[2] + str(cible)
		report_dans_db_for_author = prefixes[4] + "author"
		steal_dans_db = prefixes[5] + str(author)
		
		if int(db[steal_dans_db]) == 0 :
			gold_of_author = int(db[gold_dans_db_for_author])
			gold_of_cible = int(db[gold_dans_db_for_cible])

			valeur = 1000

			if not (((gold_of_cible - valeur) > 0) or ((gold_of_cible - valeur) == 0)) : # Trop pauvre !
				valeur = gold_of_cible

			else : # Suffisament riche !
				db[gold_dans_db_for_author] = str(gold_of_author + valeur) # On vole l'argent !
				db[gold_dans_db_for_cible] = str(gold_of_cible - valeur) # Ajoute l'argent à la cible
				db[report_dans_db_for_author] = f"5|{cible}"
				db[steal_dans_db] = 1439
				embed = discord.Embed(title=f"Vous avez dérobé dans le beau porte-feuille de {cible} +1000 !", description=f"Cet idiot a 5 minutes pour vous rattrapper avant que vous soyez loin !{author} : **{gold_of_author}** + {valeur} = **{gold_of_author + valeur}**\n⇄\n{cible} : **{gold_of_cible}** - {valeur} = **{gold_of_cible - valeur}**", color=white)

				await channel.send(embed=embed)

		elif int(db[steal_dans_db]) > 0 :
			minute = db[steal_dans_db]
			heure = minute // 60
			jour = heure // 24
			embed = discord.Embed(title=f"Tu dois encore attendre {jour}j {heure % 24}h {minute % 60}min.", description="", color=white)
			await channel.send(embed=embed)


	elif content.startswith(prefixe + "nothing") :
		embed = discord.Embed(title="Rien ne s'est passé !", description="", color=white)
		await channel.send(embed=embed)





client.run(TOKEN)