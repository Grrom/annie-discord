import os

import discord

from dotenv import load_dotenv
from utils.saucenao import saucenao

from utils.intention_recognition import load as intention_recognition
# from utils.title_recognition import load as title_recognition

load_dotenv()

client = discord.Client(intents=discord.Intents.default())
annie_id = "<@955202644702556260>"


@ client.event
async def on_ready():
    print("========================")
    print("|-- Annie is online! --|")
    print("========================")


@ client.event
async def on_message(message):

    if message.author == client.user:
        return

    if annie_id in message.content or str(message.channel.type) == "private":

        # await message.channel.send(get_title(message.content))
        return

        if "hello" in message.content:
            await message.channel.send("hello there!")
            return

        if "sauce" in message.content:
            await saucenao.get_sauce(message)
            return

        if "test" in message.content:
            await message.channel.send("test")
            return

        await message.channel.send("I have no Idea what you're talking about")
        return

    return

client.run(os.getenv("TOKEN"))
