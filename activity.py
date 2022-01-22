import discord
import asyncio
import os


TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()


@client.event
async def on_ready():
    while True:
        with open("activity.txt", "r") as f:
            activity_name = f.read()
        activity = discord.Game(name=activity_name)
        status = discord.Status.online
        await client.change_presence(status=status, activity=activity)
        await asyncio.sleep(10)


client.run(TOKEN)
