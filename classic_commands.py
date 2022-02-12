import discord
from replit import db
import random

CLIENT = discord.Client()
PREFIXE = "?"

SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24

WHITE = 16775930

SHIELD_PROTECT_TIME = 10080  # min (1 semaine)
DAGGER_TIME = 10080  # min (1 semaine)

DAILY_ADD = 800
HEBDO_ADD = 2600
BEG_ADD = [50, 100]
STEAL_VALUE = 1000


def delete_item(self, number_of_item: int, cible: str, count: int):
    number = number_of_item
    items_dans_db_for_author = self.PREFIXES["items"] + f"{cible}"
    ls = extract_data_encoded_NT1_for_shop(self, cible)

    i = 0
    for group in ls:
        if int(group[0]) == number:
            if (int(group[1]) - count) == 0:
                del (ls[i])
            else:
                group[1] = str(int(group[1]) - count)
        i += 1

    reformat = []
    for element in ls:
        reformat.append("-".join(element))

    reformated = "|".join(reformat)

    db[items_dans_db_for_author] = reformated


def use_items(self, cible: str, item: str) -> str:
    try:
        item = int(item)
    except ValueError:
        return "Merci d'utiliser le numéro de cet item et non pas le nom. (vous pouvez trouver le numéro de l'item avec `?shop`)"

    cible = str(cible)
    not_usable = "Cet objet n'est pas utilisable."

    if item > len(self.SHOP):
        return "Cet objet n'existe pas. Ce n'est pas le bon numéro."

    number = item
    ls = extract_data_encoded_NT1_for_shop(self, cible)
    i = 0
    found = False
    for group in ls:
        if int(group[0]) == number:
            # La personne ne possède pas l'item qu'il veut utiliser.
            if int(group[1]) == 0:
                return "Vous ne possédez pas cet objet. Veuillez l'acheter ou l'acquérir."
            if int(group[1]
                   ) > 0:  # La personne possède l'item qu'il veut utilisateur
                found = True
        i += 1

    if found is False:
        return "Vous ne possédez pas cet objet. Veuillez l'acheter ou l'acquérir."

    group_item = self.SHOP[item - 1]

    if item == 1:
        return not_usable

    elif item == 5:  # Excalibur
        dagger_in_db = self.PREFIXES["excalibur"] + cible  # Dagger = Exalibur
        db[dagger_in_db] = str(DAGGER_TIME)
        minute = DAGGER_TIME
        heure = minute // 60
        minute = minute % 60
        jour = heure // 24
        heure = heure % 24

        delete_item(self, 5, cible, 1)

        return f"Vous êtes désormais virtuose pendant {jour}jours {heure}h {minute}min ! :dagger: (Vous pouvez voler des personnes protégées par un bouclier)"

    elif item == 8:  # Exploitation pétrolière
        name = group_item["name"]
        return f"{name} est actif dès son achat."

    elif item == 9:  # Sablier Temporel
        sablier_dans_db = self.PREFIXES["sablier"] + cible

        if int(db[sablier_dans_db]) == 0:
            daily_dans_db = self.PREFIXES["daily"] + str(self.author)
            beg_dans_db = self.PREFIXES["beg"] + str(self.author)
            hebdo_dans_db = self.PREFIXES["hebdo"] + str(self.author)
            steal_dans_db = self.PREFIXES["steal"] + str(self.author)

            my_list = [
                daily_dans_db, beg_dans_db, hebdo_dans_db, steal_dans_db
            ]
            for timer in my_list:
                db[timer] = "0"
            db[sablier_dans_db] = "720"
            delete_item(self, 9, cible, 1)
            return "Tous vos délais sont réinitialisés !"
        else:
            minute = int(db[sablier_dans_db])
            heure = minute // 60
            minute = minute % 60
            return f"Vous ne pouvez pas utilser trop de sablier !!! Revenez donc dans {heure}h {minute}min pour l'utiliser à nouveau ! :hourglass:"

    elif item == 10:  # Bouclier Divin
        shield_in_db = self.PREFIXES["shield"] + cible
        db[shield_in_db] = str(SHIELD_PROTECT_TIME)
        minute = SHIELD_PROTECT_TIME
        heure = minute // 60
        minute = minute % 60
        jour = heure // 24
        heure = heure % 24

        delete_item(self, 10, cible, 1)

        return f"Vous êtes désormais protégé des vols pendant {jour}jours {heure}h {minute}min ! :shield:"

    else:
        return "Cet objet n'a pas encore été programmé."

# Retourne la première mention ou le premier nom d'utilisateur dans le message (pas forcément correct)


def get_mention(self, args: list) -> str:
    if len(self.message.mentions) == 0:  # Il n'y a pas de @mention
        if len(args) > 0:
            for arg in args:
                if "#" in str(arg):
                    ls_arg = list(arg)
                    if ls_arg[-5] == "#":
                        return arg
        return None

    else:
        return str(self.message.mentions[0])


def get_items_of_user(self, cible: str) -> list:
    ls = extract_data_encoded_NT1_for_shop(self, cible)

    lst_of_items = []
    lst_of_items_num = []

    for group_item in range(len(ls)):
        # 0 : Name		1 : Comment		2 : Prix		3 : Number
        item_in_shop = self.SHOP[(int(ls[group_item][0])) - 1]
        name = item_in_shop["name"]

        lst_of_items.append(name)
        lst_of_items_num.append(ls[group_item][1])

    return lst_of_items, lst_of_items_num


def create_user(self, UserToCreate):
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
        if not self.PREFIXES[key] + UserToCreate in users:
            db[self.PREFIXES[key] + UserToCreate] = "0"

    if not self.PREFIXES["items"] + UserToCreate in users:  # Items
        db[self.PREFIXES["items"] + UserToCreate] = "11-1"

    # Possessions of actions
    # Possessions of actions
    if not self.PREFIXES["user_action_possessions"] + UserToCreate in users:
        new_value = []
        for i in range(3):
            new_value.append((str(self.BASE_ACTION[i]["name"])) + "-0")
        new_value = "|".join(new_value)
        db[self.PREFIXES["user_action_possessions"] +
            UserToCreate] = new_value


# NT1 Nolann's Technic 1 (spécifique)
def extract_data_encoded_NT1_for_shop(self, cible: str) -> list:
    items_dans_db_for_author = self.PREFIXES["items"] + f"{cible}"
    try:
        value = db[items_dans_db_for_author]

        if list(value) == []:
            raise ValueError
    except ValueError:  # Il ne possède pas encore d'objets
        create_user(self, cible)
        value = db[items_dans_db_for_author]
    finally:
        ls = value.split("|")
        i = 0
        for item in ls:
            ls[i] = item.split("-")
            i += 1

        return ls


def extract_data_encoded_NT1_for_actions(self, cible: str) -> list:
    actions_dans_db_for_author = self.PREFIXES["user_action_possessions"] + \
        f"{cible}"
    try:
        value = db[actions_dans_db_for_author]

        if list(value) == []:
            raise ValueError
    except ValueError:  # Il ne possède pas encore d'objets
        create_user(self, cible)
        value = db[actions_dans_db_for_author]
    finally:
        ls = value.split("|")
        i = 0
        for item in ls:
            ls[i] = item.split("-")
            i += 1

        return ls


class commands:

    def __init__(self, message, PREFIXES, SHOP, BASE_ACTION):
        self.message = message
        self.content = message.content
        self.author = message.author
        self.channel = message.channel
        self.CLIENT = CLIENT
        self.user_id = message.author.id
        self.PREFIXES = PREFIXES
        self.SHOP = SHOP
        self.BASE_ACTION = BASE_ACTION

    async def help(self, notation, args):
        if len(args) == 0:
            with open("help.txt", "r") as lg:
                Lines = lg.readlines()
                commandes = []
                descriptif = []
                line_number = 1
                for line in Lines:
                    if line_number % 2 == 0:
                        if line.strip() == "":
                            continue
                        descriptif.append(line.strip().replace(
                            "{prefixe}", PREFIXE))
                    else:
                        if line.strip() == "":
                            continue
                        commandes.append(line.strip().replace(
                            "{prefixe}", PREFIXE))

                    line_number += 1

            embed = discord.Embed(
                title="Commandes possibles : ",
                description=":white_check_mark: : Commande disponible\n:arrows_counterclockwise: : En développement, peut ne pas marcher ou marcher partiellement.\n:x: : Commande non disponible.",
                color=WHITE)
            for i in range(len(commandes)):
                embed.add_field(name=f"{commandes[i]}",
                                value=f"{descriptif[i]}")
            await self.channel.send(embed=embed)

        else:
            with open("help.txt", "r") as lg:
                Lines = lg.readlines()
                commandes = []
                line_number = 1
                for line in Lines:
                    if line_number % 2 == 0:
                        if line.strip() == "":
                            continue
                    else:
                        if line.strip() == "":
                            continue

                    to_append = line.strip().replace("{PREFIXE}", "")
                    to_append = to_append.split(" ")
                    print(to_append)
                    commandes.append(to_append[0])
                    line_number += 1
            print(commandes)

    async def shop_print(self, notation):
        Item_Name = "name"
        Item_Info = "description"
        Item_Price = "price"
        Item_Number = "item_number"

        to_print = ""
        for group_item in self.SHOP:
            to_print += "\n"
            to_print += f"**{group_item[Item_Number]} : {group_item[Item_Name]}**"

            to_print += "\n"
            to_print += f"*{group_item[Item_Info]}*"

            to_print += "\n"
            to_print += f"{group_item[Item_Price]} :dollar: "

            to_print += "\n"

        to_print += str("")

        embed = discord.Embed(
            title="Boutique (version temporaire)",
            description=f"{to_print}\n\n```{PREFIXE}buy [item_number] [count]```ex : ```{PREFIXE}buy 11 2```(pour acheter deux objets du numéro 11)",
            color=WHITE)
        await self.channel.send(embed=embed)

    async def buy(self, notation, args):
        cible = str(self.author)

        try:
            item = int(args[0]) - 1
        except ValueError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre et non du texte.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return
        except IndexError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre indiquant l'objet que vous souhaitez acheter.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        try:
            count = int(args[1])
            if count < 0:
                embed = discord.Embed(
                    title="Vous n'essayez quand même pas de me vendre ces objets ?!",
                    description="Non merci, je refuse. Achetez plutout en positif.",
                    color=WHITE)
                await self.channel.send(embed=embed)
                return
        except ValueError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre et non du texte.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return
        except IndexError:  # Il n'y a pas de valeur spécifiée
            count = 1

        if (item < 0) or (item > len(self.SHOP)):
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="L'objet demandé n'existe pas !",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        # 0 : Name		1 : Comment		2 : Prix		3 : Number
        item_in_shop = self.SHOP[item]
        name = item_in_shop["name"]
        price = item_in_shop["price"]
        number = item_in_shop["item_number"]

        gold_dans_db_for_cible = self.PREFIXES["gold"] + str(cible)

        gold_of_cible = int(db[gold_dans_db_for_cible])

        valeur = price * count

        if not ((gold_of_cible - valeur) >= 0):  # Trop pauvre !
            embed = discord.Embed(
                title="Vous ne possédez pas assez d'argent pour acheter cet objet !",
                description=f"Vous possédez {gold_of_cible} :dollar: et votre achat vous coûterai {valeur} :dollar: !",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        items_dans_db_for_author = self.PREFIXES["items"] + f"{cible}"
        ls = extract_data_encoded_NT1_for_shop(self, cible)

        exists = False
        for group in ls:
            if int(group[0]) == number:
                if item == 7:  # 7 + 1 = 8 Exploitation
                    # La personne souhaite acheter une exploitation
                    if int(group[1]) + count > 30:
                        # La personne possèdera plus de trente exploitations
                        embed = discord.Embed(
                            title="Vous ne pouvez pas posséder plus de 30 exploitations !",
                            description=f"Vous possédez {int(group[1])} exploitations et votre achat vous en ferais posséder {int(group[1]) + count} !",
                            color=WHITE)
                        await self.channel.send(embed=embed)
                        return

                exists = True
                group[1] = str(int(group[1]) + count)

        if not exists:
            ls.append([str(number), str(count)])

        # On retire le prix de l'objet.
        db[gold_dans_db_for_cible] = str(gold_of_cible - valeur)

        reformat = []
        for element in ls:
            reformat.append("-".join(element))

        reformated = "|".join(reformat)
        db[items_dans_db_for_author] = reformated

        embed = discord.Embed(
            title="",
            description=f"Vous avez acheté {count} {name} pour {valeur} :dollar: !",
            color=WHITE)
        await self.channel.send(embed=embed)

    async def action_buy(self, notation, args):
        cible = str(self.author)

        try:
            item = int(args[0]) - 1
        except ValueError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre et non du texte.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return
        except IndexError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre indiquant quelle action vous souhaitez acheter.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        try:
            count = int(args[1])
            if count < 0:
                embed = discord.Embed(
                    title="Vous n'essayez quand même pas de me vendre ces actions ?!",
                    description="Non merci, je refuse. Achetez plutout en positif.",
                    color=WHITE)
                await self.channel.send(embed=embed)
                return
        except ValueError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre et non du texte.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return
        except IndexError:  # Il n'y a pas de nombre spécifié
            count = 1

        if (item < 0) or (item > len(self.BASE_ACTION)):
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="L'action demandé n'existe pas !",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        action_in_shop = self.BASE_ACTION[item]
        name = action_in_shop["name"]
        price = db[self.PREFIXES[action_in_shop["price_key"]]]
        print(price)
        number = action_in_shop["number"]

        gold_dans_db_for_cible = self.PREFIXES["gold"] + str(cible)

        gold_of_cible = int(db[gold_dans_db_for_cible])

        valeur = price * count

        if not ((gold_of_cible - valeur) >= 0):  # Trop pauvre !
            embed = discord.Embed(
                title="Vous ne possédez pas assez d'argent pour acheter cette action !",
                description=f"Vous possédez {gold_of_cible} :dollar: et votre achat vous coûterai {valeur} :dollar: !",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        actions_dans_db_for_author = self.PREFIXES["user_action_possessions"] + \
            f"{cible}"
        ls = extract_data_encoded_NT1_for_actions(self, cible)
        print(f"ls = {ls}")

        for group in ls:
            if int(group[0]) == number:
                exists = True
                group[1] = str(int(group[1]) + count)

        if not exists:
            ls.append([str(number), str(count)])

        print(f"new_ls = {ls}")

        # On retire le prix de l'objet.
        db[gold_dans_db_for_cible] = str(gold_of_cible - valeur)

        reformat = []
        for element in ls:
            reformat.append("-".join(element))

        reformated = "|".join(reformat)
        print(f"Reformated = {reformated}")
        db[actions_dans_db_for_author] = reformated

        embed = discord.Embed(
            title="",
            description=f"Vous avez acheté {count} {name} pour {valeur} :dollar: !",
            color=WHITE)
        await self.channel.send(embed=embed)

    async def sell(self, notation, args):
        cible = str(self.author)

        try:
            item = int(args[0]) - 1
        except ValueError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre et non du texte.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return
        except IndexError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre indiquant l'objet que vous souhaitez vendre.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        try:
            count = int(args[1])
            if count < 0:
                embed = discord.Embed(
                    title="Vous n'essayez quand même pas de m'acheter ces objets ?!",
                    description="Non merci, je refuse. Vendez plutout en positif.",
                    color=WHITE)
                await self.channel.send(embed=embed)
                return
        except ValueError:
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Merci d'entrer un nombre et non du texte.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return
        except IndexError:  # Il n'y a pas de valeur spécifiée
            count = 1

        if (item < 0) or (item > len(self.SHOP)):
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="L'objet demandé n'existe pas !",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        # 0 : Name		1 : Comment		2 : Prix		3 : Number
        item_in_shop = self.SHOP[item]
        name = item_in_shop["name"]
        price = item_in_shop["price"]
        number = item_in_shop["item_number"]

        gold_dans_db_for_cible = self.PREFIXES["gold"] + str(cible)

        gold_of_cible = int(db[gold_dans_db_for_cible])

        valeur = (price * count) - (price * count) // 10

        items_dans_db_for_author = self.PREFIXES["items"] + f"{cible}"
        ls = extract_data_encoded_NT1_for_shop(self, cible)

        exists = False
        i = 0
        for group in ls:
            if int(group[0]) == number:
                exists = True

                if count > int(group[1]):
                    # La personne veut vendre plus qu'elle ne possède
                    embed = discord.Embed(
                        title="Vous essayez de me vendre plus que vous ne possédez !!!",
                        description="Vous ne m'aurez pas ainsi, petit voyou !!!",
                        color=WHITE)
                    await self.channel.send(embed=embed)
                    return

                group[1] = str(int(group[1]) - count)
                if group[1] == "0":
                    del (ls[i])
            i += 1

        if not exists:
            embed = discord.Embed(
                title="Vous ne possédez pas cet objet.",
                description="A moins que vous ne le sortiez de votre chapeau magique, vous n'en possédez pas !",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        # On retire le prix de l'objet.
        db[gold_dans_db_for_cible] = str(gold_of_cible + valeur)

        reformat = []
        for element in ls:
            reformat.append("-".join(element))

        reformated = "|".join(reformat)
        db[items_dans_db_for_author] = reformated

        embed = discord.Embed(
            title="",
            description=f"Vous avez vendu {count} {name} pour {valeur} :dollar: !",
            color=WHITE)
        await self.channel.send(embed=embed)

    async def bag(self, notation, args):
        cible = str(get_mention(self, args))

        if cible == "None":
            cible = str(self.author)

        retour = get_items_of_user(self, cible)

        lst_of_items = retour[0]
        lst_of_items_num = retour[1]

        formated = ""

        for item in range(len(lst_of_items)):
            formated += f"**{lst_of_items[item]}** × {lst_of_items_num[item]}\n"

        embed = discord.Embed(title=f"Inventaire de {cible}",
                              description=f"{formated}",
                              color=WHITE)
        await self.channel.send(embed=embed)

    async def use(self, notation, args):
        if len(args) == 0:
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        item = args[0]

        cible = str(self.author)

        text = use_items(self, cible, item)

        embed = discord.Embed(title="", description=f"{text}", color=WHITE)
        await self.channel.send(embed=embed)

    async def profile(self, notation, args):
        cible = str(get_mention(self, args))

        if cible != "None":
            create_user(self, cible)
        else:
            cible = str(self.author)

        gold_dans_db = self.PREFIXES["gold"] + cible

        equip_and_power = "Equipements et pouvoirs actifs : "

        shield_dans_db = self.PREFIXES["shield"] + str(cible)
        gold_dans_db = self.PREFIXES["gold"] + str(cible)
        dagger_in_db = self.PREFIXES["excalibur"] + str(cible)

        have_a_shield = True
        have_a_dagger = True

        try:
            shield = int(db[shield_dans_db])
        except KeyError:
            have_a_shield = False
        else:
            if shield == 0:
                have_a_shield = False

        try:
            dagger = int(db[dagger_in_db])

        except KeyError:
            create_user(self, cible)
            dagger = int(db[dagger_in_db])
            have_a_dagger = False
        else:
            if dagger == 0:
                have_a_dagger = False

        if have_a_shield:
            minute = shield
            heure = minute // 60
            minute = minute % 60
            equip_and_power += f"\n- **Bouclier Divin** :shield: : `{heure}h {minute}min`"

        if have_a_dagger:
            minute = dagger
            heure = minute // 60
            minute = minute % 60
            equip_and_power += f"\n- **Virtuose du vol** :dagger: : `{heure}h {minute}min`"

        retour = get_items_of_user(self, cible)

        lst_of_items = retour[0]
        lst_of_items_num = retour[1]

        exploitation_name = self.SHOP[7]["name"]

        have_an_exploitation = False
        for i in range(len(lst_of_items)):
            if str(lst_of_items[i]) == str(exploitation_name):
                number = i
                have_an_exploitation = True
                break

        if have_an_exploitation:
            number_of_exploitations = lst_of_items_num[number]

            rapport_dans_db = self.PREFIXES["auto_gold_won"] + cible
            rapport = db[rapport_dans_db]

            equip_and_power += f"\n- **Exploitation pétrolière** :construction_site: : `{number_of_exploitations} actifs` (`{rapport}` :dollar: de bénéfices)"

        formated = ""

        for item in range(len(lst_of_items)):
            formated += f"**{lst_of_items[item]}** × {lst_of_items_num[item]}\n"

        objects = "Inventaire : \n" + formated

        gold = f"**Monnaie** : `{db[gold_dans_db]}` :dollar:"

        if (cible == "None") or (cible == str(self.author)):
            level_dans_db = self.PREFIXES["level"] + str(self.author)
            xp_dans_db = self.PREFIXES["xp"] + str(self.author)
        else:
            level_dans_db = self.PREFIXES["level"] + cible
            xp_dans_db = self.PREFIXES["xp"] + cible

        try:
            lvl = int(db[level_dans_db])
        except KeyError:
            db[level_dans_db] = "0"
            lvl = 0
        try:
            xp = int(db[xp_dans_db])
        except KeyError:
            db[xp_dans_db] = "0"
            xp = 0

        level = f"**Level** : `{lvl}`\n**Expérience** : `{xp}/{lvl*500}`"

        inactivity_dans_db = self.PREFIXES["inactivity"] + str(cible)

        try:
            inactivity = int(db[inactivity_dans_db])
        except KeyError:
            db[inactivity_dans_db] = "0"
            inactivity = 0

        if inactivity < 5:
            inactivity = "Actif"
            inactivity = f"**Durée d'inactivité : ** `{inactivity}` :fire:"
        else:
            min = inactivity % 60
            hour = inactivity // 60
            inactivity = f"**Durée d'inactivité : ** `{hour}h {min}min` :fire:"
            if hour > 24:
                days = hour % 24
                hour = hour % 24
                inactivity = f"**Durée d'inactivité : ** `{days} jours {hour}h {min}min` :o:"
                if days > 30:
                    months = days // 30
                    inactivity = f"**Durée d'nactivité : ** `{months} mois` :no_entry_sign:"

        cube = "▬" * 18
        embed = discord.Embed(
            title=f"Profil de {cible}",
            description=f"{cube}\n{gold}\n{level}\n{inactivity}\n{cube}\n{equip_and_power}\n{cube}\n{objects}",
            color=WHITE)
        await self.channel.send(embed=embed)

    async def gold(self, notation, args):
        cible = str(get_mention(self, args))

        if cible != "None":
            create_user(self, cible)

        if (cible == "None") or (cible == str(self.author)):
            gold_dans_db = self.PREFIXES["gold"] + str(self.author)

            embed = discord.Embed(title=f"{self.author}",
                                  description="Tu as {} :dollar:.".format(
                                      db[gold_dans_db]),
                                  color=WHITE)
            await self.channel.send(embed=embed)

        else:
            gold_dans_db = self.PREFIXES["gold"] + cible

            embed = discord.Embed(
                title="",
                description="Cette personne a {} :dollar:.".format(
                    db[gold_dans_db]),
                color=WHITE)
            await self.channel.send(embed=embed)

    async def level(self, notation, args):
        cible = str(get_mention(self, args))

        if cible != "None":
            create_user(self, cible)

        if (cible == "None") or (cible == str(self.author)):
            level_dans_db = self.PREFIXES["level"] + str(self.author)
            xp_dans_db = self.PREFIXES["xp"] + str(self.author)
        else:
            level_dans_db = self.PREFIXES["level"] + cible
            xp_dans_db = self.PREFIXES["xp"] + cible

        try:
            lvl = int(db[level_dans_db])
        except KeyError:
            db[level_dans_db] = "0"
            lvl = 0
        try:
            xp = int(db[xp_dans_db])
        except KeyError:
            db[xp_dans_db] = "0"
            xp = 0

        embed = discord.Embed(
            title="",
            description=f"Niveau : `{lvl}`\nxp : `{xp}/{lvl*500}`",
            color=WHITE)
        await self.channel.send(embed=embed)

    async def give(self, notation, args):
        cible = str(get_mention(self, args))
        if cible != "None":
            create_user(self, cible)

        if cible == "None":
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        cible_user = cible
        gold_dans_db_for_author = self.PREFIXES["gold"] + str(self.author)
        gold_dans_db_for_cible = self.PREFIXES["gold"] + cible_user

        if str(self.author) == cible_user:
            embed = discord.Embed(
                title="Vous ne pouvez pas vous donner de l'argent à vous même !!!!",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        gold_of_author = int(db[gold_dans_db_for_author])
        gold_of_cible = int(db[gold_dans_db_for_cible])

        try:
            valeur = int(args[1])
            if valeur < 0:
                raise ValueError

        except IndexError:
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        except ValueError:
            embed = discord.Embed(
                title="Moi qui vous croyais moins machiavélique... Vous ne pouvez pas donner un montant négatif !!!",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        if not (((gold_of_author - valeur) > 0) or
                ((gold_of_author - valeur) == 0)):  # Trop pauvre !
            embed = discord.Embed(
                title=f"Vous ne possédez pas suffisament d'argent pour envoyer {valeur} :dollar: à {cible_user}",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)
            return
        else:  # Suffisament riche !
            # On retire l'argent à l'auteur
            db[gold_dans_db_for_author] = str(gold_of_author - valeur)
            db[gold_dans_db_for_cible] = str(
                gold_of_cible + valeur)  # Ajoute l'argent à la cible
            embed = discord.Embed(
                title="⇄ Transfert effectué : ",
                description=f"{self.author} : **{gold_of_author}** :dollar: - {valeur} :dollar: = **{gold_of_author - valeur}** :dollar:\n⇄\n{cible_user} : **{gold_of_cible}** :dollar: + {valeur} :dollar: = **{gold_of_cible + valeur}** :dollar:",
                color=WHITE)
            await self.channel.send(embed=embed)

    async def rank_level(self, notation):
        users = db.keys()
        all_users = []
        for user in users:
            if user.startswith(self.PREFIXES["level"]):
                to_append = str(user.replace(self.PREFIXES["level"], ""))
                create_user(self, to_append)
                all_users.append(to_append)

        value_of_all_users = []
        for user in all_users:
            value_of_all_users.append(
                int(db[str(self.PREFIXES["level"] + user)]))
        dict_all_users = {}

        for i in range(len(all_users)):
            dict_all_users[all_users[i]] = value_of_all_users[i]

        # Trié dans l'ordre croissant
        tri = reversed(sorted(dict_all_users.items(), key=lambda t: t[1]))

        to_print = ""
        i = 0
        for user in tri:
            if i == 0:
                to_print += ":heart_on_fire:"
            elif i == 1:
                to_print += ":cyclone:"
            elif i == 2:
                to_print += ":trident:"
            elif i > 2:  # Fin du top 3
                to_print += ":fleur_de_lis:"

            to_print += f" **{user[1]}** —— {user[0]}\n"
            i += 1

        embed = discord.Embed(title="🏆 Classement des niveaux : ",
                              description=f"{to_print}",
                              color=WHITE)
        await self.channel.send(embed=embed)

    async def rank_gold(self, notation):
        users = db.keys()
        all_users = []
        for user in users:
            if user.startswith(self.PREFIXES["gold"]):
                to_append = str(user.replace(self.PREFIXES["gold"], ""))
                create_user(self, to_append)
                all_users.append(to_append)

        value_of_all_users = []
        for user in all_users:
            value_of_all_users.append(
                int(db[str(self.PREFIXES["gold"] + user)]))
        dict_all_users = {}

        for i in range(len(all_users)):
            dict_all_users[all_users[i]] = value_of_all_users[i]

        # Trié dans l'ordre croissant
        tri = reversed(sorted(dict_all_users.items(), key=lambda t: t[1]))

        to_print = ""
        i = 0
        for user in tri:
            if i == 0:
                to_print += "🥇"
            elif i == 1:
                to_print += "🥈"
            elif i == 2:
                to_print += "🥉"
            elif i > 2:  # Fin du top 3
                to_print += "💎"

            to_print += f" **{user[1]}** :dollar: —— {user[0]}\n"
            i += 1

        embed = discord.Embed(title="🏆 Classement : ",
                              description=f"{to_print}",
                              color=WHITE)
        await self.channel.send(embed=embed)

    async def beg(self):
        beg_dans_db = self.PREFIXES["beg"] + str(self.author)
        gold_dans_db = self.PREFIXES["gold"] + str(self.author)
        level_dans_db = self.PREFIXES["level"] + str(self.author)

        if int(db[beg_dans_db]) == 0:
            rand = random.randint(1, 2)
            lvl = int(db[level_dans_db])
            if rand == 1:
                rand = int(BEG_ADD[0] + (BEG_ADD[0] * (lvl / 20)))
            if rand == 2:
                rand = int(BEG_ADD[1] + (BEG_ADD[1] * (lvl / 20)))

            db[gold_dans_db] = int(db[gold_dans_db]) + rand
            db[beg_dans_db] = 5  # minute a attendre
            embed = discord.Embed(title="Tu as mendié un peu d'argent",
                                  description=f"*+{rand}* :dollar:",
                                  color=WHITE)
            await self.channel.send(embed=embed)

        elif int(db[beg_dans_db]) > 0:
            minute = db[beg_dans_db]
            embed = discord.Embed(
                title=f"Tu dois encore attendre {minute} min avant de mendier à nouveau.",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)

    async def daily(self):
        daily_dans_db = self.PREFIXES["daily"] + str(self.author)
        gold_dans_db = self.PREFIXES["gold"] + str(self.author)
        level_dans_db = self.PREFIXES["level"] + str(self.author)

        lvl = int(db[level_dans_db])

        if int(db[daily_dans_db]) == 0:
            db[gold_dans_db] = int(db[gold_dans_db]) + \
                int(DAILY_ADD + (DAILY_ADD * (lvl/20)))
            db[daily_dans_db] = 1439
            embed = discord.Embed(
                title="Tu as récupéré ta récompense journalière.",
                description=f"*+{int(DAILY_ADD + (DAILY_ADD * (lvl/20)))}* :dollar:",
                color=WHITE)
            await self.channel.send(embed=embed)

        elif int(db[daily_dans_db]) > 0:
            minute = db[daily_dans_db]
            heure = minute // 60
            embed = discord.Embed(
                title=f"Tu dois encore attendre {heure}h {minute % 60}min.",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)

    async def ping(self):
        embed = discord.Embed(title="Pong :ping_pong:",
                              description="",
                              color=WHITE)
        await self.channel.send(embed=embed)

    async def hebdo(self):
        hebdo_dans_db = self.PREFIXES["hebdo"] + str(self.author)
        gold_dans_db = self.PREFIXES["gold"] + str(self.author)
        level_dans_db = self.PREFIXES["level"] + str(self.author)

        lvl = int(db[level_dans_db])

        if int(db[hebdo_dans_db]) == 0:
            db[gold_dans_db] = int(db[gold_dans_db]) + \
                int(HEBDO_ADD + (HEBDO_ADD * (lvl/20)))
            db[hebdo_dans_db] = 10079
            embed = discord.Embed(
                title="Tu as récupéré ta récompense hebdomadaire.",
                description=f"*+{int(HEBDO_ADD + (HEBDO_ADD * (lvl/20)))}* :dollar:",
                color=WHITE)
            await self.channel.send(embed=embed)
        elif int(db[hebdo_dans_db]) > 0:
            minute = db[hebdo_dans_db]
            heure = minute // 60
            jour = heure // 24
            embed = discord.Embed(
                title=f"Tu dois encore attendre {jour}j {heure % 24}h {minute % 60}min.",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)

    async def steal(self, notation, args):
        cible = str(get_mention(self, args))
        if cible != "None":
            create_user(self, cible)

        if str(self.author) == cible:
            embed = discord.Embed(
                title="Vous ne pouvez pas vous voler vous même !!!!",
                description=" Ou alors, vous êtes plus bête que je ne le pensait.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        if cible == "None":
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        gold_dans_db_for_author = self.PREFIXES["gold"] + str(self.author)
        gold_dans_db_for_cible = self.PREFIXES["gold"] + str(cible)
        report_dans_db_for_author = self.PREFIXES["report"] + f"{self.author}"
        steal_dans_db = self.PREFIXES["steal"] + str(self.author)

        if int(db[steal_dans_db]) == 0:
            shield_in_db = self.PREFIXES["shield"] + cible
            dagger_in_db = self.PREFIXES["excalibur"] + str(self.author)
            try:
                shield = int(db[shield_in_db])
                dagger = int(db[dagger_in_db])

            except KeyError:
                create_user(self, cible)
                create_user(self, self.author)
                shield = int(db[shield_in_db])
                dagger = int(db[dagger_in_db])

            else:
                if shield > 0:
                    if dagger > 0:
                        embed = discord.Embed(
                            title="La personne est protégée par un bouclier, mais en votre qualité de virtuose, vous pouvez quand même la détrousser !",
                            description="",
                            color=WHITE)
                        await self.channel.send(embed=embed)
                    else:
                        db[steal_dans_db] = 1439
                        embed = discord.Embed(
                            title="Vous vous êtes lamentablement fracassé la tête sur son bouclier :shield:, vous échouez donc à le voler.",
                            description="",
                            color=WHITE)
                        await self.channel.send(embed=embed)
                        return

            gold_of_author = int(db[gold_dans_db_for_author])
            gold_of_cible = int(db[gold_dans_db_for_cible])
            level_dans_db = self.PREFIXES["level"] + str(self.author)
            lvl = int(db[level_dans_db])

            valeur = gold_of_cible // 1000 + (lvl * gold_of_cible // 1000)
            print(valeur)
            if valeur < STEAL_VALUE:
                valeur = STEAL_VALUE
            print(valeur)

            if not (((gold_of_cible - valeur) > 0) or
                    ((gold_of_cible - valeur) == 0)):  # Trop pauvre !
                valeur = gold_of_cible

            db[gold_dans_db_for_author] = str(
                gold_of_author + valeur)  # Ajoute l'argent à la cible
            db[gold_dans_db_for_cible] = str(gold_of_cible -
                                             valeur)  # On vole l'argent !
            db[report_dans_db_for_author] = f"5|{cible}|{valeur}"
            db[steal_dans_db] = 1439
            embed = discord.Embed(
                title=f"Vous avez dérobé dans le porte-feuille bien garni de {cible} *+{valeur}* :dollar: !",
                description=f"Cet idiot a 5 minutes pour vous rattrapper avant que vous soyez loin ! (avec `{PREFIXE}report`)\n\n{self.author} : **{gold_of_author}** :dollar: + {valeur} :dollar: = **{gold_of_author + valeur}** :dollar:\n⇄\n{cible} : **{gold_of_cible}** :dollar: - {valeur} :dollar: = **{gold_of_cible - valeur}** :dollar:",
                color=WHITE)

            await self.channel.send(embed=embed)

        elif int(db[steal_dans_db]) > 0:
            minute = db[steal_dans_db]
            heure = minute // 60
            embed = discord.Embed(
                title=f"Tu dois encore attendre {heure % 24}h {minute % 60}min avant de voler à nouveau.",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)

    async def report(self, notation, args):
        cible = str(get_mention(self, args))
        if cible != "None":
            create_user(self, cible)

        if cible == "None":
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        if str(self.author) == cible:
            embed = discord.Embed(
                title="Vous ne pouvez pas vous dénoncer vous même !!!!",
                description=" Ou alors, vous êtes plus bête que je ne le pensait.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        report_dans_db_for_author = self.PREFIXES["report"] + f"{cible}"
        try:
            value = db[report_dans_db_for_author]
            ls = value.split("|")
            ls[0] = int(ls[0])
            value = ls[0]  # Temps restant en minute pour reporter
            stolen = str(ls[1])
            valeur_stolen = int(ls[2])
        except KeyError:
            embed = discord.Embed(
                title="Cette personne n'est pas un voyou, contrairement à toi, qui a fait appel à la police pour rien !!!!",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        if value == 0:
            embed = discord.Embed(
                title="Cette personne est déjà loin ! Il aurait fallu m'appeller plus tôt !",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        if stolen != str(self.author):
            embed = discord.Embed(
                title=f"Seul {stolen} peut m'appeller pour dénoncer un voleur.",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        # Si on arrive là, c'est qu'on peut bien reporter.

        level_dans_db = self.PREFIXES["level"] + str(self.author)
        lvl = db[level_dans_db]

        valeur = valeur_stolen * (1, 5 + (lvl // 50))

        gold_dans_db_for_author = self.PREFIXES["gold"] + str(self.author)
        gold_dans_db_for_cible = self.PREFIXES["gold"] + str(cible)

        gold_of_author = int(db[gold_dans_db_for_author])
        gold_of_cible = int(db[gold_dans_db_for_cible])

        if not (((gold_of_cible - valeur) > 0) or
                ((gold_of_cible - valeur) == 0)):  # Trop pauvre !
            valeur = gold_of_cible

        db[gold_dans_db_for_author] = str(gold_of_author +
                                          valeur)  # On ajoute l'argent
        # On enlève l'argent à la cible
        db[gold_dans_db_for_cible] = str(gold_of_cible - valeur)
        del db[report_dans_db_for_author]
        embed = discord.Embed(
            title=f"On a rattrapé ce voleur ! Ce voyou de {cible} vous a payé une amende de *+{valeur}* :dollar: pour sa fourberie !",
            description=f"Il n'aurait jamais du s'attaquer à vous !\n\n{self.author} : **{gold_of_author}** :dollar: + {valeur} :dollar: = **{gold_of_author + valeur} :dollar:**\n⇄\n{cible} : **{gold_of_cible}** :dollar: - {valeur} :dollar: = **{gold_of_cible - valeur}** :dollar:",
            color=WHITE)

        await self.channel.send(embed=embed)

    async def actions(self, notation, args):
        Red_in_db = self.PREFIXES["Red_actions"]
        Green_in_db = self.PREFIXES["Green_actions"]
        Blue_in_db = self.PREFIXES["Blue_actions"]

        Red_Historic_in_db = self.PREFIXES["Red_historic"]
        Green_Historic_in_db = self.PREFIXES["Green_historic"]
        Blue_Historic_in_db = self.PREFIXES["Blue_historic"]

        Red = int(db[Red_in_db])
        Green = int(db[Green_in_db])
        Blue = int(db[Blue_in_db])

        try:
            Red_Historic = "` :dollar: - `".join(
                (db[Red_Historic_in_db]).split("|"))
            Green_Historic = "` :dollar: - `".join(
                (db[Green_Historic_in_db]).split("|"))
            Blue_Historic = "` :dollar: - `".join(
                (db[Blue_Historic_in_db]).split("|"))
        except KeyError:
            Hist = "Il n'y a pas encore d'historique pour le moment. :zzz:"
        else:
            Hist = "Historique de la valeur des actions de base :"
            Hist += f"\n**1 : Red :** `{Red_Historic}` :dollar:"
            Hist += f"\n**2 : Green :** `{Green_Historic}` :dollar:"
            Hist += f"\n**3 : Blue :** `{Blue_Historic}` :dollar:"

        RGB = "Valeur des actions de base :"
        RGB += f"\n**- Red :** `{Red}` :dollar:"
        RGB += f"\n**- Green :** `{Green}` :dollar:"
        RGB += f"\n**- Blue :** `{Blue}` :dollar:"

        info = "\nAchetez des actions avec `?actionbuy` suivi du numéro de l'action !\nExemple pour acheter une action red : \n`?actionbuy 1`"

        cube = "▬" * 18
        embed = discord.Embed(
            title="Actions et évolution : ",
            description=f"{cube}\n{RGB}\n{cube}\n{Hist}\n{info}",
            color=WHITE)
        await self.channel.send(embed=embed)
