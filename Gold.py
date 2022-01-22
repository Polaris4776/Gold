import discord
import os
from replit import db
from discord.ext import tasks
import random
from datetime import datetime
import pytz
import classic_commands
import admin_commands
"""Commandes spéciales :
?delete
?resetdata
?removemydata
?blockgold
?unblockgold
"""

# 0 : Name		1 : Comment		2 : Prix		3 : Number
shop = [
    [
        "Pendentif de sagesse de Leonard de Vinci :medal:",
        "Avec ce pendentif, vous serez un peu moins bête (c'est déjà un bon début).",
        3000
    ],
    [
        "Baton de Merlin :magic_wand:",
        "Par la barbe de l'enchanteur, le voilà retrouvé !", 10000
    ],
    [
        "Bottes de sept lieues :boot:",
        "Vous ne serez plus jamais en retard !", 2000
    ],
    [
        "Couronne de la reine d'Angleterre :crown:",
        "Gardé jalousement dans son château, la voilà !", 3000
    ],
    [
        "Excalibur :dagger:",
        "Débrouillez vous pour la retirer de ce maudit rocher !", 15000
    ],
    [
        "Arc de Robin des Bois :bow_and_arrow:", "Ne rate jamais sa cible !",
        8000
    ],
    ["Eclair de Zeus :zap:", "Foudroyez vos ennemis !", 10000],
    [
        "Exploitation pétrolière :construction_site:",
        "Investissez dans le pétrole et gagnez automatiquement de l'argent !",
        5000
    ],
    [
        "Sablier temporel :hourglass:",
        "Réinitialisez vos temps d'attente !!!", 3000
    ],
    [
        "Bouclier Divin :shield:",
        "Empêchez les gens de vous voler pendant une semaine !!!", 2000
    ],
    ["Crotte :poop:", "Offrez la à vos amis !", 10],
    ["Justice corrompue :scales:",
        "Faite la preuve de votre richesse est corrompez le monde entier !", 1000000000],
    ["Richesse exquise :reminder_ribbon:",
        "Montrez une preuve de votre raffinement extrême !", 1000000000000],
    ["Richesse suprême :rosette: ",
        "L'objet qui ferait mourir de jalousie un milliardaire !", 99000000000000000]
]
# ":boomerang:""  boomerang

number = 1
for group_item in shop:
    group_item.append(number)
    number += 1

TOKEN = os.getenv("DISCORD_TOKEN")
print("\n\n\n\n\n")
print(TOKEN)
print("\n\n\n\n")
client = discord.Client()
prefixe = "?"


def is_x_in_items(x, items):  # items = liste dans liste
    x = str(x)
    for group_item in items:
        if str(group_item[0]) == x:
            print("Yes")
            return True

    return False


def get_items_of_user(cible):
    ls = extract_data_encoded_NT1(cible)

    lst_of_items = []
    lst_of_items_num = []

    for group_item in range(len(ls)):
        item_in_shop = shop[(int(ls[group_item][0])) -
                            1]  # 0 : Name		1 : Comment		2 : Prix		3 : Number
        name = item_in_shop[0]
        number = item_in_shop[3]

        lst_of_items.append(name)
        lst_of_items_num.append(ls[group_item][1])

    return lst_of_items, lst_of_items_num


def extract_data_encoded_NT1(cible):  # NT1 Nolann's Technic 1 (spécifique)
    items_dans_db_for_author = prefixes[6] + f"{cible}"
    try:
        value = db[items_dans_db_for_author]

        if list(value) == []:
            raise ValueError
    except ValueError:  # Il ne possède pas encore d'objets
        create_user(cible)
        value = db[items_dans_db_for_author]
    finally:
        ls = value.split("|")
        i = 0
        for item in ls:
            ls[i] = item.split("-")
            i += 1

        return ls


def get_datetime():
    tz_London = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_London)
    time = now.strftime("%d:%m:%Y:%H:%M:%S")
    listime = time.split(":")  # Jour, Mois, Année, Heure, Minute, Seconde
    return listime


def get_mention(
    message, args
):  # Retourne la première mention ou le premier nom d'utilisateur dans le message (pas forcément correct)
    if len(message.mentions) == 0:  # Il n'y a pas de @mention
        if len(args) > 0:
            for arg in args:
                if "#" in str(arg):
                    ls_arg = list(arg)
                    if ls_arg[-5] == "#":
                        return arg
        return None

    else:
        return message.mentions[0]


def create_user(UserToCreate):
    try:
        if UserToCreate.bot:
            return
    except AttributeError:  # Ce n'est pas une variable Discord.Member
        pass

    UserToCreate = str(UserToCreate)
    parcour = [
        0, 1, 2, 3, 5, 9, 10, 11, 12, 13
    ]  # Daily, Hebdo, Gold, Daily, Steal, [...], Argent rapportée en exploit. pétrol., Durée d'inactivité...
    users = db.keys()

    for i in parcour:
        if not prefixes[i] + UserToCreate in users:
            db[prefixes[i] + UserToCreate] = "0"

    if not prefixes[6] + UserToCreate in users:  # Items
        db[prefixes[6] + UserToCreate] = "11-1"


def timer_edit_less(user, prefixe_num):
    if not (user.startswith(prefixe_num)):
        return
    var = int(db[user])

    if var == 0:
        return  # On est prêt à faire la commande !
    else:
        db[user] = var - 1  # On s'approche du moment prêt de 1 min !


def timer_edit_more(user, prefixe_num):
    if not (user.startswith(prefixe_num)):
        return
    var = int(db[user])

    db[user] = var + 1  # On augmente la valeur d'une minute.


def report_edit(user):
    if not (user.startswith(prefixes[4])):
        return
    var = db[user]
    ls = var.split("|")
    ls[0] = int(ls[0])

    if ls[0] == 0:
        return  # On est prêt à faire la commande !
    else:
        # On s'approche du moment prêt de 1 min !
        db[user] = f"{ls[0] - 1}|{ls[1]}"


async def wait_for_message(
        channel, author,
        client):  # En attente d'un message dans le même salon.
    def check(m):
        return (m.channel == channel) and (m.content != "") and (
            m.author == author) and (author != client.user)

    msg = await client.wait_for("message", check=check)

    return msg


def get_args(content, command):
    var = str(content)
    var = var.strip()
    var = var.split(" ")

    list_to_del = []
    correction = 0
    for i in range(len(var)):
        var[i] = str(var[i]).strip()
        if var[i] == "":
            list_to_del.append(i)

    for i in list_to_del:
        del (var[i - correction])
        correction += 1

    for i in range(len(var)):
        try:
            var[i] = int(var[i])
        except ValueError:
            continue

    del (var[0])  # Nom de la commande = inutile

    return var


def add_xp(author, value):
    author = str(author)
    xp_in_db = prefixes[9] + author
    lvl_in_db = prefixes[10] + author

    try:
        xp = int(db[xp_in_db])
    except KeyError:
        xp = 0

    try:
        lvl = int(db[lvl_in_db])
    except KeyError:
        lvl = 0

    xp += value
    if xp >= 500 * lvl:
        xp -= 500 * lvl
        lvl += 1

    db[xp_in_db] = str(xp)
    db[lvl_in_db] = str(lvl)


def exploitation(user):
    exploitation_rent = 1

    if prefixes[11] in user:
        cible = str(user).replace(prefixes[11], "")

        retour = get_items_of_user(cible)

        lst_of_items = retour[0]
        lst_of_items_num = retour[1]

        exploitation_name = shop[7][0]

        have_an_exploitation = False
        for i in range(len(lst_of_items)):
            if str(lst_of_items[i]) == str(exploitation_name):
                number = i
                have_an_exploitation = True
                break

        if have_an_exploitation:
            number_of_exploitations = int(lst_of_items_num[number])

            rapport_dans_db = prefixes[11] + cible
            rapport = db[rapport_dans_db]

            db[rapport_dans_db] = int(
                rapport) + exploitation_rent * number_of_exploitations

            gold_dans_db = prefixes[2] + cible
            db[gold_dans_db] = int(
                db[gold_dans_db]) + exploitation_rent * number_of_exploitations


prefixes = [
    "←+→", "-@_@-", "°-°", "-_-", "+_+", "X_X", "¤_¤", "*_*", "→0←", "↔xp↔",
    "↔lvl↔", "_*-*_", "♀_♀", "O_O"
]  # ←+→ : daily 	-@_@- : hebdo		°-° : gold		-_- : beg		+_+ : steal ready to report		X_X : steal		¤_¤ : items		*_* : bannis		→0← : shield		↔xp↔ : xp		↔lvl↔ : level		_*-*_ : argent déjà rapportée par les exploitations pétrolières		♀_♀ : sablier temporel		O_O :  durée d'inactivité

second = 1
minute = second * 60
hour = minute * 60
day = hour * 24

white = 16775930


# users = db.keys()
# for user in users :
# 	if user.startswith("+_+") :
# 		# db[prefixes[3] + user.replace("°-°", "")] = 0
# 		del db[user]

# @tasks.loop(seconds=hour) # 1 heure d'attente entre chaque execution de def
# async def midnight():
# 	# Fonction expérimentale
# 	now = get_datetime() # Jour, Mois, Année, Heure, Minute, Seconde
# 	hour = int(now[3])
# 	minute = int(now[4])
# 	second = int(now[5])

# 	print(f"Nous sommes le {now[0]}/{now[1]}/{now[2]} à {hour}:{minute}:{second}")

# 	if hour == 0 :
# 		print(f"Minute == {minute} and Hour == 0 !!!! On a détecté et on peut redémarrer !!!")
# 		with open("tmpinfo.info", "w") as info :
# 			info.write(f"Minute == {minute} and Hour == 0 !!!! On a détecté et on peut redémarrer !!!")

# 		users = db.keys()

# 		for user in users :
# 			if user.startswith(prefixes[0]) : # Préfixe de daily
# 				var = int(db[user])
# 				if var != 0 :
# 					db[user] = 0 # On remet les compteurs à 0 pour minuit !
# 					with open("tmpinfo.info", "w") as info :
# 						info.write(f"{user} remis à 0 !!!")


# 1 minute d'attente entre chaque execution de def
@ tasks.loop(seconds=minute)
async def temps():
    rand = random.randint(1, 2048)  # 1 chance sur 2048 pour l'instant
    if rand == 5:
        rand = True

    users = db.keys()
    for user in users:
        # On retire 1 minute au temps restant avant que daily soit dispo
        timer_edit_less(user, prefixes[0])
        # On retire 1 minute au temps restant avant que hebdo soit dispo
        timer_edit_less(user, prefixes[1])
        # On retire 1 minute au temps restant avant que beg soit dispo
        timer_edit_less(user, prefixes[3])
        # On retire 1 minute au temps restant avant que steal soit dispo
        timer_edit_less(user, prefixes[5])
        # On retire 1 minute au temps restant avant que le sablier temporel soit dispo
        timer_edit_less(user, prefixes[12])
        # On ajoute 1 minute au temps d'inactivité
        timer_edit_more(user, prefixes[13])

        try:
            # On retire 1 minute au temps restant avant que shield soit dispo
            timer_edit_less(user, prefixes[8])
        except ValueError:
            pass
            report_edit(user)
        if rand:
            exploitation(user)  # On ajoute l'argent de l'exploitation

    users = db.keys()
    for user in users:
        if user.startswith("O_O"):
            if int(db[user]) > 10080:  # Inactif depuis 1 semaine.
                list_user = list(user)
                for i in range(3):
                    del list_user[0]
                no_list_user = "".join(list_user)
                if str(db["°-°" + no_list_user]) == "0":
                    print(
                        f"La personne {no_list_user} est pauvre et inactive : supprimons la !")
                    to_delete = no_list_user

                    users = db.keys()
                    found = False
                    for user in users:
                        if to_delete in user:
                            del db[user]
                            found = True
                    if found:
                        print(f"{to_delete} supprimé avec succès !")


@ client.event
async def on_ready():
    print("Je me suis connecté en {0.user}".format(client))

    temps.start()


@ client.event
async def on_message(message):
    content = message.content
    author = message.author
    channel = message.channel

    if author == client.user:
        return

    if str(content).startswith(prefixe):
        create_user(str(author))

        users = db.keys()
        for user in users:
            if user.startswith(prefixes[7]):
                if str(author) in user:
                    print(
                        f"{author}, utilisateur bannis, a tenté de faire une commande."
                    )
                    return
        add_xp(author, 49)

    cl_command = classic_commands.commands(message, prefixes, shop)
    adm_command = admin_commands.commands(message, prefixes)

    if content.lower().startswith(prefixe + "help"):
        notation = f"{prefixe}help"
        args = get_args(content, prefixe + "help")

        await cl_command.help(notation, args)

    elif content.lower().startswith(prefixe + "shop"):
        notation = f"{prefixe}shop"

        await cl_command.shop_print(notation)

    elif content.lower().startswith(prefixe + "buy"):
        notation = f"{prefixe}buy [item_number] [count]"
        args = get_args(content, prefixe + "buy")

        await cl_command.buy(notation, args)

    elif content.lower().startswith(prefixe + "sell"):
        notation = f"{prefixe}sell [item_number] [count]"
        args = get_args(content, prefixe + "sell")

        await cl_command.sell(notation, args)

    elif content.lower().startswith(prefixe + "bag"):
        notation = f"{prefixe}bag [user]"
        args = get_args(content, prefixe + "bag")

        await cl_command.bag(notation, args)

    elif content.lower().startswith(prefixe + "use"):
        notation = f"{prefixe}use [item]"
        args = get_args(content, prefixe + "buy")

        await cl_command.use(notation, args)

    elif content.lower().startswith(prefixe + "profile"):
        notation = f"{prefixe}profile [user]"
        args = get_args(content, prefixe + "profile")

        await cl_command.profile(notation, args)

    elif content.lower().startswith(prefixe + "gold"):
        notation = f"{prefixe}gold [user]"
        args = get_args(content, prefixe + "gold")

        await cl_command.gold(notation, args)
    elif content.lower().startswith(prefixe + "balance"):
        notation = f"{prefixe}balance [user]"
        args = get_args(content, prefixe + "balance")

        await cl_command.gold(notation, args)

    if content.lower().startswith(prefixe + "level"):
        notation = f"{prefixe}level [user]"
        args = get_args(content, prefixe + "level")

        await cl_command.level(notation, args)
    if content.lower().startswith(prefixe + "xp"):
        notation = f"{prefixe}xp [user]"
        args = get_args(content, prefixe + "xp")

        await cl_command.level(notation, args)

    elif content.lower().startswith(prefixe + "give"):
        notation = f"{prefixe}give <user> <valeur>"
        args = get_args(content, prefixe + "give")

        await cl_command.give(notation, args)

    elif content.lower().startswith(prefixe + "rank level"):
        notation = f"{prefixe}rank level"

        await cl_command.rank_level(notation)

    elif content.lower().startswith(prefixe + "rank gold"):
        notation = f"{prefixe}rank gold"

        await cl_command.rank_gold(notation)

    elif content.lower().startswith(prefixe + "beg"):
        notation = f"{prefixe}beg"

        await cl_command.beg()

    elif content.lower().startswith(prefixe + "daily"):
        notation = f"{prefixe}daily"

        await cl_command.daily()

    elif content.lower().startswith(prefixe + "hebdo"):
        notation = f"{prefixe}hebdo"

        await cl_command.hebdo()

    elif content.lower().startswith(prefixe + "ping"):
        notation = f"{prefixe}ping"

        await cl_command.ping()

    elif content.lower().startswith(prefixe + "steal"):
        notation = f"{prefixe}steal <user>"
        args = get_args(content, prefixe + "steal")

        await cl_command.steal(notation, args)

    elif content.lower().startswith(prefixe + "report"):
        notation = f"{prefixe}report <user>"
        args = get_args(content, prefixe + "report")

        await cl_command.report(notation, args)

    elif content.lower().startswith(prefixe + "delete"):
        notation = f"{prefixe}delete <user>"
        args = get_args(content, prefixe + "delete")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.delete(notation, args)

    elif content.lower().startswith(prefixe + "removemydata"):
        notation = f"{prefixe}removemydata"
        args = get_args(content, prefixe + "removemydata")

        if not (str(author) == "Alioth#7249"):
            if not (str(author) == "Polaris#4776"):
                return

        await adm_command.remove_my_data(notation, args)

    elif content.lower().startswith(prefixe + "resetdata"):
        notation = f"{prefixe}resetdata <type>"
        args = get_args(content, prefixe + "resetdata <type>")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.reset_data(notation, args)

    elif content.lower().startswith(prefixe + "blockgold"):
        notation = f"{prefixe}blockgold <user>"
        args = get_args(content, prefixe + "blockgold <user>")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.blockgold(notation, args)

    elif content.lower().startswith(prefixe + "unblockgold"):
        notation = f"{prefixe}unblockgold <user>"
        args = get_args(content, prefixe + "unblockgold <user>")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.unblockgold(notation, args)

    elif content.lower().startswith(prefixe + "nothing"):
        notation = f"{prefixe}nothing"

        embed = discord.Embed(title="Rien ne s'est passé !",
                              description="", color=white)
        await channel.send(embed=embed)

    if not author.bot:
        add_xp(author, 1)

        # On remet la durée d'inactivité à 0.
        db[prefixes[13] + str(author)] = 0


client.run(TOKEN)
