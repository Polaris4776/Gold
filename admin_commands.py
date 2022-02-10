import discord
from replit import db
from classic_commands import create_user

CLIENT = discord.Client()
PREFIXE = "?"

WHITE = 16775930


# Retourne la première mention ou le premier nom d'utilisateur dans le message (pas forcément correct)
def get_mention(message, args):
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


class commands:

    def __init__(self, message, prefixes):
        self.message = message
        self.content = message.content
        self.author = message.author
        self.channel = message.channel
        self.CLIENT = CLIENT
        self.user_id = message.author.id
        self.prefixes = prefixes

    async def delete(self, notation, args):
        cible = None
        if len(self.message.mentions) == 0:  # IL n'y a pas de @mention
            if len(args) > 0:
                for arg in args:
                    if "#" in str(arg):
                        ls_arg = list(arg)
                        if ls_arg[-5] == "#":
                            cible = arg

        else:
            cible = self.message.mentions[0]
        cible = str(cible)

        create_user(self, cible)

        to_delete = cible
        users = db.keys()
        found = False
        for user in users:
            if to_delete in user:
                del db[user]
                found = True

        if found:
            embed = discord.Embed(title=f"{to_delete} supprimé avec succès !",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
        if not (found):
            embed = discord.Embed(
                title=f"{to_delete} n'a pas été trouvé dans la base de données !",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)

    async def remove_my_data(self, notation, args):
        cible = str(self.author)

        users = db.keys()

        exist = False
        for user in users:
            for prefix in self.prefixes:
                if prefix in user:
                    user = user.replace(prefix, "")
                    if cible in user:
                        exist = True

        if exist:
            for user in users:
                if cible in user:
                    del db[user]
            embed = discord.Embed(title="Compte supprimé avec succès !",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Vous ne pouvez pas supprimer votre compte car vous n'existez pas encore.",
                description="",
                color=WHITE)
            await self.channel.send(embed=embed)

    async def reset_data(self, notation, args):
        if len(args) == 0:
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="Entrez le nom de *prefixes*",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        users = db.keys()

        for user in users:
            if user.startswith(self.prefixes[args[0]]):
                del db[user]
        embed = discord.Embed(title="Variable supprimée avec succès !",
                              description="",
                              color=WHITE)
        await self.channel.send(embed=embed)

    async def blockgold(self, notation, args):
        cible = str(get_mention(self.message, args))

        if cible != "None":
            create_user(self, cible)

        if cible == "None":
            embed = discord.Embed(
                title=f"Merci de faire ```{notation}```",
                description="Bloquer définitivement l'accès à Gold.",
                color=WHITE)
            await self.channel.send(embed=embed)
            return

        db[self.prefixes["bannis"] + cible] = "True"

        embed = discord.Embed(title="Compte bannis !",
                              description="",
                              color=WHITE)
        await self.channel.send(embed=embed)

    async def unblockgold(self, notation, args):
        cible = str(get_mention(self.message, args))

        if cible != "None":
            create_user(self, cible)

        if cible == "None":
            embed = discord.Embed(title=f"Merci de faire ```{notation}```",
                                  description="Débloquer l'accès à Gold.",
                                  color=WHITE)
            await self.channel.send(embed=embed)
            return

        try:
            del db[self.prefixes["bannis"] + cible]
        except KeyError:
            embed = discord.Embed(title="Ce compte n'étais pas bannis !",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Compte débannis !",
                                  description="",
                                  color=WHITE)
            await self.channel.send(embed=embed)
