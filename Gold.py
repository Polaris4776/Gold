from this import d
from unicodedata import name
import discord
import os
from replit import db
from discord.ext import tasks
import random
from datetime import datetime
import pytz
import classic_commands
import admin_commands
import json

"""Commandes spéciales :
?delete
?resetdata
?removemydata
?blockgold
?unblockgold
"""

TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT = discord.Client()
PREFIXE = "?"
ALEA_OF_HEAVY_CHANGE = 100

LOCATION_OF_FR_JSON = "language/fr.json"
LANGUAGE = str(os.getenv("LANGUAGE"))

if LANGUAGE == "fr":
    with open(LOCATION_OF_FR_JSON) as json_file:
        data = json.load(json_file)
        SHOP = data["SHOP"]
elif LANGUAGE == "en":
    pass  # Pas encore programmé

with open(LOCATION_OF_FR_JSON) as json_file:
    data = json.load(json_file)
    PREFIXES = data["PREFIXES"]

with open(LOCATION_OF_FR_JSON) as json_file:
    data = json.load(json_file)
    BASE_ACTION = data["ACTIONS_SHOP"]


def is_x_in_items(x: str, items: list) -> bool:  # items = liste dans liste
    for group_item in items:
        if str(group_item[0]) == str(x):
            print("Yes")
            return True
    return False


def get_items_of_user(cible: str) -> list:
    ls = extract_data_encoded_NT1_for_shop(cible)

    lst_of_items = []
    lst_of_items_num = []

    for group_item in range(len(ls)):
        item_in_shop = SHOP[(int(ls[group_item][0])) - 1]
        # 0 : Name		1 : Comment		2 : Prix		3 : Number
        name = item_in_shop["name"]

        lst_of_items.append(name)
        lst_of_items_num.append(ls[group_item][1])

    return lst_of_items, lst_of_items_num


# NT1 Nolann's Technic 1(spécifique)
def extract_data_encoded_NT1_for_shop(cible: str) -> list:
    items_dans_db_for_author = PREFIXES["items"] + f"{cible}"
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


def get_datetime() -> list:
    tz_London = pytz.timezone('Europe/Paris')
    now = datetime.now(tz_London)
    time = now.strftime("%d:%m:%Y:%H:%M:%S")
    listime = time.split(":")  # Jour, Mois, Année, Heure, Minute, Seconde
    return listime


def create_user(UserToCreate):
    try:
        if UserToCreate.bot:
            return
    except AttributeError:  # Ce n'est pas une variable Discord.Member
        pass

    UserToCreate = str(UserToCreate)
    # Daily, Hebdo, Gold, Daily, Steal, [...], Argent rapportée en exploit. pétrol., Durée d'inactivité...
    parcour = [
        "daily", "hebdo", "gold", "beg", "steal", "shield", "xp", "level", "auto_gold_won", "sablier", "inactivity", "excalibur"
    ]
    users = db.keys()

    for key in parcour:
        if not PREFIXES[key] + UserToCreate in users:
            db[PREFIXES[key] + UserToCreate] = "0"

    if not PREFIXES["items"] + UserToCreate in users:  # Items
        db[PREFIXES["items"] + UserToCreate] = "11-1"

    if not PREFIXES["user_action_possessions"] + UserToCreate in users:  # Possessions of actions
        new_value = []
        for i in range(3):
            new_value.append((str(BASE_ACTION[i]["name"])) + "-0")
        new_value = "|".join(new_value)
        db[PREFIXES["user_action_possessions"] +
            UserToCreate] = new_value


def timer_edit_less(user: str, prefixe_num: str):
    if not (user.startswith(prefixe_num)):
        return
    var = int(db[user])

    if var == 0:
        return  # On est prêt à faire la commande !
    else:
        db[user] = var - 1  # On s'approche du moment prêt de 1 min !


def timer_edit_more(user: str, prefixe_num: str):
    if not (user.startswith(prefixe_num)):
        return
    var = int(db[user])

    db[user] = var + 1  # On augmente la valeur d'une minute.


def report_edit(user: str):
    if not (user.startswith(PREFIXES["report"])):
        return
    var = db[user]
    ls = var.split("|")
    ls[0] = int(ls[0])

    if ls[0] == 0:
        return  # On est prêt à faire la commande !
    else:
        # On s'approche du moment prêt de 1 min !
        db[user] = f"{ls[0] - 1}|{ls[1]}"


# En attente d'un message dans le même salon.
async def wait_for_message(channel, author, CLIENT):

    def check(m):
        return (m.channel == channel) and (m.content != "") and (
            m.author == author) and (author != CLIENT.user)

    msg = await CLIENT.wait_for("message", check=check)

    return msg


def get_args(content: str, command: str) -> list:
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


def add_xp(author: str, value: int):
    author = str(author)
    xp_in_db = PREFIXES["xp"] + author
    lvl_in_db = PREFIXES["level"] + author

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


def historic_changing(new_value: int, historic: str) -> str:
    historic = historic.split("|")  # Devient une liste
    del historic[0]
    historic.append(str(new_value))
    historic = "|".join(historic)
    print(f"Red historic now : {historic}")

    return historic


def fluctuation_simulation(value_of_actions: int, historic_of_values: list) -> int:
    historic_of_values = historic_of_values.split("|")  # Devient une liste

    for element in range(len(historic_of_values)):
        historic_of_values[element] = int(historic_of_values[element])

    tmp_sum = 0
    for element in historic_of_values:
        tmp_sum += int(element)
    average = tmp_sum // len(historic_of_values)

    sorted_historic = sorted(historic_of_values)
    etendue = int(sorted_historic[-1]) - int(sorted_historic[0])

    ecart = int(historic_of_values[0]) - int(historic_of_values[-1])

    heavy_change = False

    # Premier lancer pour fort changement
    alea = random.randint(0, ALEA_OF_HEAVY_CHANGE)
    print(f"Ancienne valeur : {value_of_actions}")
    old_value_of_actions = value_of_actions
    if alea == ALEA_OF_HEAVY_CHANGE:  # Forte valorisation ou effondrement
        value_of_actions = average + ecart * random.randint(1, 15)
        heavy_change = True
    else:  # Changement normal
        alea = random.randint(0, 100)
        if alea > 50:
            value_of_actions = value_of_actions + ecart * \
                (alea - 50) // 10 + random.randint(-10, 30)
            etendue // 1000
        if alea < 50:
            value_of_actions = value_of_actions - ecart * \
                alea // 10 - random.randint(-10, 30) - etendue // 1000

    if value_of_actions < 10:  # Minimum value
        value_of_actions = 100

    if heavy_change:
        print("\n\nLa valeur de l'action de l'entreprise à fortement changé !!!")
        print(f"La valeur actuelle est désormais : {value_of_actions}\n\n")
    print(f"Le changement est de : {value_of_actions - old_value_of_actions}")

    return value_of_actions


def first_historic_generator(index_value: int, database_location: str) -> str:
    ls = []
    mini = index_value // 2
    maxi = index_value * 2
    for i in range(5):
        ls.append(str(random.randint(mini, maxi)))
    joined = "|".join(ls)
    print("Joined = " + str(joined) + "\n")
    db[database_location] = joined

    return joined


def edit_actions_RGB():
    print("Modification des actions.")

    Red_in_db = PREFIXES["Red_actions"]
    Green_in_db = PREFIXES["Green_actions"]
    Blue_in_db = PREFIXES["Blue_actions"]

    Red_Historic_in_db = PREFIXES["Red_historic"]
    Green_Historic_in_db = PREFIXES["Green_historic"]
    Blue_Historic_in_db = PREFIXES["Blue_historic"]

    Red = int(db[Red_in_db])
    Green = int(db[Green_in_db])
    Blue = int(db[Blue_in_db])

    try:
        Red_Historic = db[Red_Historic_in_db]
        Green_Historic = db[Green_Historic_in_db]
        Blue_Historic = db[Blue_Historic_in_db]
    except KeyError:
        print("Veuillez entrer la valeur afin de générer les chiffres aléatoires pour les trois entreprises de base : ")
        generate_R = int(input("Valeur de Red : "))
        generate_G = int(input("Valeur de Green : "))
        generate_B = int(input("Valeur de Blue : "))

        Red_Historic = first_historic_generator(generate_R, Red_Historic_in_db)
        Green_Historic = first_historic_generator(
            generate_G, Green_Historic_in_db)
        Blue_Historic = first_historic_generator(
            generate_B, Blue_Historic_in_db)

    new_R_value = fluctuation_simulation(Red, Red_Historic)
    new_G_value = fluctuation_simulation(Green, Green_Historic)
    new_B_value = fluctuation_simulation(Blue, Blue_Historic)

    db[Red_in_db] = new_R_value
    db[Green_in_db] = new_G_value
    db[Blue_in_db] = new_B_value

    db[Red_Historic_in_db] = historic_changing(new_R_value, Red_Historic)
    db[Green_Historic_in_db] = historic_changing(new_G_value, Green_Historic)
    db[Blue_Historic_in_db] = historic_changing(new_B_value, Blue_Historic)


def exploitation(user: str):
    exploitation_rent = 1

    if PREFIXES["auto_gold_won"] in user:
        cible = str(user).replace(PREFIXES["auto_gold_won"], "")

        retour = get_items_of_user(cible)

        lst_of_items = retour[0]
        lst_of_items_num = retour[1]

        exploitation_name = SHOP[7]["name"]

        have_an_exploitation = False
        for i in range(len(lst_of_items)):
            if str(lst_of_items[i]) == str(exploitation_name):
                number = i
                have_an_exploitation = True
                break

        if have_an_exploitation:
            number_of_exploitations = int(lst_of_items_num[number])

            rapport_dans_db = PREFIXES["auto_gold_won"] + cible
            rapport = db[rapport_dans_db]

            db[rapport_dans_db] = int(
                rapport) + exploitation_rent * number_of_exploitations

            gold_dans_db = PREFIXES["gold"] + cible
            db[gold_dans_db] = int(
                db[gold_dans_db]) + exploitation_rent * number_of_exploitations


# PREFIXES = [
#     "←+→", "-@_@-", "°-°", "-_-", "+_+", "X_X", "¤_¤", "*_*", "→0←", "↔xp↔", "↔lvl↔",
#     "_*-*_", "♀_♀", "O_O", "T_T",  "U_U|user_actions|", "U_U|base_action|Red", "U_U|base_action|Green", "U_U|base_action|Blue", "U_U|base_action|Red|history", "U_U|base_action|Green|history", "U_U|base_action|Blue|history"
# ]
# # ←+→ : daily 	-@_@- : hebdo		°-° : gold		-_- : beg		+_+ : steal ready to report		X_X : steal		¤_¤ : items		*_* : bannis		→0← : shield		↔xp↔ : xp
# # ↔lvl↔ : level		_*-*_ : argent déjà rapportée par les exploitations pétrolières		♀_♀ : sablier temporel
# # O_O :  durée d'inactivité       T_T : Excalibur     U_U|user_actions| : Possessions de chaque utilisateur
# # |base_action| : Actions de bases (Red Green Blue)
# # |base_action|history| : Historique des valeurs des actions

SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24

WHITE = 16775930


# 1 minute d'attente entre chaque execution de def
@ tasks.loop(seconds=MINUTE)
async def temps():
    rand = random.randint(1, 2048)  # 1 chance sur 2048 pour l'instant
    if rand == 5:
        rand = True

    users = db.keys()
    for user in users:
        # On retire 1 minute au temps restant avant que daily soit dispo
        timer_edit_less(user, PREFIXES["daily"])
        # On retire 1 minute au temps restant avant que hebdo soit dispo
        timer_edit_less(user, PREFIXES["hebdo"])
        # On retire 1 minute au temps restant avant que beg soit dispo
        timer_edit_less(user, PREFIXES["beg"])
        # On retire 1 minute au temps restant avant que steal soit dispo
        timer_edit_less(user, PREFIXES["steal"])
        # On retire 1 minute au temps restant avant que le sablier temporel soit dispo
        timer_edit_less(user, PREFIXES["sablier"])
        # On ajoute 1 minute au temps d'inactivité
        timer_edit_more(user, PREFIXES["inactivity"])

        try:
            # On retire 1 minute au temps restant avant que shield soit dispo
            timer_edit_less(user, PREFIXES["shield"])
        except KeyError:
            pass
            report_edit(user)
        if rand:
            exploitation(user)  # On ajoute l'argent de l'exploitation

    rand = random.randint(1, 5)  # 1 chance sur 5 pour l'instant
    if rand == 5:
        print("Je modifie le cours de la bourse")
        edit_actions_RGB()

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
            if user.startswith(PREFIXES["bannis"]):
                if str(author) in user:
                    print(
                        f"{author}, utilisateur bannis, a tenté de faire une commande."
                    )
                    return
        add_xp(author, 49)

    cl_command = classic_commands.commands(
        message, PREFIXES, SHOP, BASE_ACTION)
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

    elif content.lower().startswith(PREFIXE + "actionbuy"):
        notation = f"{PREFIXE}action buy [action_number] [count]"
        args = get_args(content, PREFIXE + "actionbuy")

        await cl_command.action_buy(notation, args)

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

    elif content.lower().startswith(PREFIXE + "actions"):
        notation = f"{PREFIXE}actions"
        args = get_args(content, PREFIXE + "actions")

        await cl_command.actions(notation, args)

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
        db[PREFIXES["inactivity"] + str(author)] = 0

ls = ["Red_actions", "Green_actions", "Blue_actions"]
for element in ls:
    try:
        to_sell = db[PREFIXES[element]]
    except KeyError:
        db[PREFIXES[element]] = input(
            f"\nLa database du prix de {element} n'est pas encore définie. A combien voulez-vous la mettre ?\nValeur : ")

CLIENT.run(TOKEN)
