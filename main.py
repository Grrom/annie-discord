import os

import discord

from dotenv import load_dotenv
from utils.saucenao import saucenao
from utils.annie_api import annie

from utils.intention_recognition.load import get_intention
from utils.title_recognition.load import get_title

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

    if annie_id in message.content or str(message.channel.type) == "private" and ".register" not in message.content:

        if get_intention(message.content) == "ask_sauce":
            await saucenao.get_sauce(message)
            return

        if get_intention(message.content) == "ask_recommendation":
            response = await annie.get_recommendations(message.author.id)
            if response is None:
                await message.channel.send("Sorry but I don't recognize your discord account, have you linked you discord account in https://client-annie.me ?")
                return
            await message.channel.send(response)
            return

        if get_intention(message.content) == "add_to_watchlist":
            await message.channel.send("edit watchlist?")
            return

        if "hello" in message.content:
            await message.channel.send("hello there!")
            return

        await message.channel.send("I have no Idea what you're talking about")
        return

    return

client.run(os.getenv("TOKEN"))
