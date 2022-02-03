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
SHOP = [[
    "Pendentif de sagesse de Leonard de Vinci :medal:",
    "Avec ce pendentif, vous serez un peu moins bête (c'est déjà un bon début).",
    3000, 1
],
        [
            "Baton de Merlin :magic_wand:",
            "Par la barbe de l'enchanteur, le voilà retrouvé !", 10000, 2
        ],
        [
            "Bottes de sept lieues :boot:",
            "Vous ne serez plus jamais en retard !", 2000, 3
        ],
        [
            "Couronne de la reine d'Angleterre :crown:",
            "Gardé jalousement dans son château, la voilà !", 3000, 4
        ],
        [
            "Excalibur :dagger:",
            "Débrouillez vous pour la retirer de ce maudit rocher !", 15000, 5
        ],
        [
            "Arc de Robin des Bois :bow_and_arrow:",
            "Ne rate jamais sa cible !", 8000, 6
        ], ["Eclair de Zeus :zap:", "Foudroyez vos ennemis !", 10000, 7],
        [
            "Exploitation pétrolière :construction_site:",
            "Investissez dans le pétrole et gagnez automatiquement de l'argent !",
            5000, 8
        ],
        [
            "Sablier temporel :hourglass:",
            "Réinitialisez vos temps d'attente !!!", 3000, 9
        ],
        [
            "Bouclier Divin :shield:",
            "Empêchez les gens de vous voler pendant une semaine !!!", 2000
        ], ["Crotte :poop:", "Offrez la à vos amis !", 10],
        [
            "Justice corrompue :scales:",
            "Faite la preuve de votre richesse est corrompez le monde entier !",
            1000000000, 11
        ],
        [
            "Richesse exquise :reminder_ribbon:",
            "Montrez une preuve de votre raffinement extrême !", 1000000000000,
            12
        ],
        [
            "Richesse suprême :rosette: ",
            "L'objet qui ferait mourir de jalousie un milliardaire !",
            99000000000000000, 13
        ]]
# ":boomerang:""  boomerang

TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT = discord.Client()
PREFIXE = "?"


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
        item_in_shop = SHOP[(int(ls[group_item][0])) - 1]
        # 0 : Name		1 : Comment		2 : Prix		3 : Number
        name = item_in_shop[0]

        lst_of_items.append(name)
        lst_of_items_num.append(ls[group_item][1])

    return lst_of_items, lst_of_items_num


def extract_data_encoded_NT1(cible):  # NT1 Nolann's Technic 1 (spécifique)
    items_dans_db_for_author = PREFIXES[6] + f"{cible}"
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
        if not PREFIXES[i] + UserToCreate in users:
            db[PREFIXES[i] + UserToCreate] = "0"

    if not PREFIXES[6] + UserToCreate in users:  # Items
        db[PREFIXES[6] + UserToCreate] = "11-1"


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
    if not (user.startswith(PREFIXES[4])):
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
        CLIENT):  # En attente d'un message dans le même salon.

    def check(m):
        return (m.channel == channel) and (m.content != "") and (
            m.author == author) and (author != CLIENT.user)

    msg = await CLIENT.wait_for("message", check=check)

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
    xp_in_db = PREFIXES[9] + author
    lvl_in_db = PREFIXES[10] + author

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

    if PREFIXES[11] in user:
        cible = str(user).replace(PREFIXES[11], "")

        retour = get_items_of_user(cible)

        lst_of_items = retour[0]
        lst_of_items_num = retour[1]

        exploitation_name = SHOP[7][0]

        have_an_exploitation = False
        for i in range(len(lst_of_items)):
            if str(lst_of_items[i]) == str(exploitation_name):
                number = i
                have_an_exploitation = True
                break

        if have_an_exploitation:
            number_of_exploitations = int(lst_of_items_num[number])

            rapport_dans_db = PREFIXES[11] + cible
            rapport = db[rapport_dans_db]

            db[rapport_dans_db] = int(
                rapport) + exploitation_rent * number_of_exploitations

            gold_dans_db = PREFIXES[2] + cible
            db[gold_dans_db] = int(
                db[gold_dans_db]) + exploitation_rent * number_of_exploitations


PREFIXES = [
    "←+→", "-@_@-", "°-°", "-_-", "+_+", "X_X", "¤_¤", "*_*", "→0←", "↔xp↔",
    "↔lvl↔", "_*-*_", "♀_♀", "O_O"
]  # ←+→ : daily 	-@_@- : hebdo		°-° : gold		-_- : beg		+_+ : steal ready to report		X_X : steal		¤_¤ : items		*_* : bannis		→0← : shield		↔xp↔ : xp		↔lvl↔ : level		_*-*_ : argent déjà rapportée par les exploitations pétrolières		♀_♀ : sablier temporel		O_O :  durée d'inactivité

SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24

WHITE = 16775930


# 1 minute d'attente entre chaque execution de def
@tasks.loop(seconds=MINUTE)
async def temps():
    rand = random.randint(1, 2048)  # 1 chance sur 2048 pour l'instant
    if rand == 5:
        rand = True

    users = db.keys()
    for user in users:
        # On retire 1 minute au temps restant avant que daily soit dispo
        timer_edit_less(user, PREFIXES[0])
        # On retire 1 minute au temps restant avant que hebdo soit dispo
        timer_edit_less(user, PREFIXES[1])
        # On retire 1 minute au temps restant avant que beg soit dispo
        timer_edit_less(user, PREFIXES[3])
        # On retire 1 minute au temps restant avant que steal soit dispo
        timer_edit_less(user, PREFIXES[5])
        # On retire 1 minute au temps restant avant que le sablier temporel soit dispo
        timer_edit_less(user, PREFIXES[12])
        # On ajoute 1 minute au temps d'inactivité
        timer_edit_more(user, PREFIXES[13])

        try:
            # On retire 1 minute au temps restant avant que shield soit dispo
            timer_edit_less(user, PREFIXES[8])
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
                try:
                    if str(db["°-°" + no_list_user]) == "0":
                        print(
                            f"La personne {no_list_user} est pauvre et inactive : supprimons la !"
                        )
                        to_delete = no_list_user

                        users = db.keys()
                        found = False
                        for user in users:
                            if to_delete in user:
                                del db[user]
                                found = True
                        if found:
                            print(f"{to_delete} supprimé avec succès !")
                except KeyError as e:
                    print(f"\nKeyError catched. Exception : {e}")


@CLIENT.event
async def on_ready():
    print("Je me suis connecté en {0.user}".format(CLIENT))

    temps.start()


@CLIENT.event
async def on_message(message):
    content = message.content
    author = message.author
    channel = message.channel

    if author == CLIENT.user:
        return

    if str(content).startswith(PREFIXE):
        create_user(str(author))

        users = db.keys()
        for user in users:
            if user.startswith(PREFIXES[7]):
                if str(author) in user:
                    print(
                        f"{author}, utilisateur bannis, a tenté de faire une commande."
                    )
                    return
        add_xp(author, 49)

    cl_command = classic_commands.commands(message, PREFIXES, SHOP)
    adm_command = admin_commands.commands(message, PREFIXES)

    if content.lower().startswith(PREFIXE + "help"):
        notation = f"{PREFIXE}help"
        args = get_args(content, PREFIXE + "help")

        await cl_command.help(notation, args)

    elif content.lower().startswith(PREFIXE + "shop"):
        notation = f"{PREFIXE}shop"

        await cl_command.shop_print(notation)

    elif content.lower().startswith(PREFIXE + "buy"):
        notation = f"{PREFIXE}buy [item_number] [count]"
        args = get_args(content, PREFIXE + "buy")

        await cl_command.buy(notation, args)

    elif content.lower().startswith(PREFIXE + "sell"):
        notation = f"{PREFIXE}sell [item_number] [count]"
        args = get_args(content, PREFIXE + "sell")

        await cl_command.sell(notation, args)

    elif content.lower().startswith(PREFIXE + "bag"):
        notation = f"{PREFIXE}bag [user]"
        args = get_args(content, PREFIXE + "bag")

        await cl_command.bag(notation, args)

    elif content.lower().startswith(PREFIXE + "use"):
        notation = f"{PREFIXE}use [item]"
        args = get_args(content, PREFIXE + "buy")

        await cl_command.use(notation, args)

    elif content.lower().startswith(PREFIXE + "profile"):
        notation = f"{PREFIXE}profile [user]"
        args = get_args(content, PREFIXE + "profile")

        await cl_command.profile(notation, args)

    elif content.lower().startswith(PREFIXE + "gold"):
        notation = f"{PREFIXE}gold [user]"
        args = get_args(content, PREFIXE + "gold")

        await cl_command.gold(notation, args)
    elif content.lower().startswith(PREFIXE + "balance"):
        notation = f"{PREFIXE}balance [user]"
        args = get_args(content, PREFIXE + "balance")

        await cl_command.gold(notation, args)

    if content.lower().startswith(PREFIXE + "level"):
        notation = f"{PREFIXE}level [user]"
        args = get_args(content, PREFIXE + "level")

        await cl_command.level(notation, args)
    if content.lower().startswith(PREFIXE + "xp"):
        notation = f"{PREFIXE}xp [user]"
        args = get_args(content, PREFIXE + "xp")

        await cl_command.level(notation, args)

    elif content.lower().startswith(PREFIXE + "give"):
        notation = f"{PREFIXE}give <user> <valeur>"
        args = get_args(content, PREFIXE + "give")

        await cl_command.give(notation, args)

    elif content.lower().startswith(PREFIXE + "rank level"):
        notation = f"{PREFIXE}rank level"

        await cl_command.rank_level(notation)

    elif content.lower().startswith(PREFIXE + "rank gold"):
        notation = f"{PREFIXE}rank gold"

        await cl_command.rank_gold(notation)

    elif content.lower().startswith(PREFIXE + "beg"):
        notation = f"{PREFIXE}beg"

        await cl_command.beg()

    elif content.lower().startswith(PREFIXE + "daily"):
        notation = f"{PREFIXE}daily"

        await cl_command.daily()

    elif content.lower().startswith(PREFIXE + "hebdo"):
        notation = f"{PREFIXE}hebdo"

        await cl_command.hebdo()

    elif content.lower().startswith(PREFIXE + "ping"):
        notation = f"{PREFIXE}ping"

        await cl_command.ping()

    elif content.lower().startswith(PREFIXE + "steal"):
        notation = f"{PREFIXE}steal <user>"
        args = get_args(content, PREFIXE + "steal")

        await cl_command.steal(notation, args)

    elif content.lower().startswith(PREFIXE + "report"):
        notation = f"{PREFIXE}report <user>"
        args = get_args(content, PREFIXE + "report")

        await cl_command.report(notation, args)

    elif content.lower().startswith(PREFIXE + "delete"):
        notation = f"{PREFIXE}delete <user>"
        args = get_args(content, PREFIXE + "delete")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.delete(notation, args)

    elif content.lower().startswith(PREFIXE + "removemydata"):
        notation = f"{PREFIXE}removemydata"
        args = get_args(content, PREFIXE + "removemydata")

        if not (str(author) == "Alioth#7249"):
            if not (str(author) == "Polaris#4776"):
                return

        await adm_command.remove_my_data(notation, args)

    elif content.lower().startswith(PREFIXE + "resetdata"):
        notation = f"{PREFIXE}resetdata <type>"
        args = get_args(content, PREFIXE + "resetdata <type>")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.reset_data(notation, args)

    elif content.lower().startswith(PREFIXE + "blockgold"):
        notation = f"{PREFIXE}blockgold <user>"
        args = get_args(content, PREFIXE + "blockgold <user>")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.blockgold(notation, args)

    elif content.lower().startswith(PREFIXE + "unblockgold"):
        notation = f"{PREFIXE}unblockgold <user>"
        args = get_args(content, PREFIXE + "unblockgold <user>")

        if not (str(author) == "Polaris#4776"):
            return

        await adm_command.unblockgold(notation, args)

    elif content.lower().startswith(PREFIXE + "nothing"):
        notation = f"{PREFIXE}nothing"

        embed = discord.Embed(title="Rien ne s'est passé !",
                              description="",
                              color=WHITE)
        await channel.send(embed=embed)

    if not author.bot:
        add_xp(author, 1)

        # On remet la durée d'inactivité à 0.
        db[PREFIXES[13] + str(author)] = 0


CLIENT.run(TOKEN)
