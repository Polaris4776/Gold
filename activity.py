import discord
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT = discord.Client()


@CLIENT.event
async def on_ready():
    while True:
        with open("activity.txt", "r") as f:
            activity_name = f.read()
        activity = discord.Game(name=activity_name)
        status = discord.Status.online
        await CLIENT.change_presence(status=status, activity=activity)
        await asyncio.sleep(10)


CLIENT.run(TOKEN)
