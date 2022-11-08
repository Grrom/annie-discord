import os

import discord

from discord.enums import MessageType

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

    if (annie_id in message.content) or (str(message.channel.type) == "private" and ".register" not in message.content) or ((await message.channel.fetch_message(message.reference.message_id)).author.id == client.user.id):

        if get_intention(message.content) == "ask_sauce":
            await saucenao.get_sauce(message)
            return

        if get_intention(message.content) == "ask_recommendation":
            await message.reply("Hmmm... wait, I'll check some titles you might like.")

            async with message.channel.typing():
                response = await annie.get_recommendations(message.author.id)
                if response is None:
                    await message.reply("Sorry but I don't recognize your discord account, have you linked you discord account in https://client-annie.me ?")
                    return
                await message.reply(embed=await annie.anime_to_embed(response), view=annie.AnotherRecommendation(0, message.channel))

                if response.get("trailerUrl") is not None:
                    await message.reply("Here's a trailer for it: " + response["trailerUrl"])
                return

        # MAL ACTIONS STARTS HERE
        if get_intention(message.content) == "add_to_watchlist":
            await message.reply("add")
            return

        if get_intention(message.content) == "drop_from_watchlist":
            await message.reply("drop")
            return

        if get_intention(message.content) == "put_on_hold":
            await message.reply("hold")
            return

        if get_intention(message.content) == "mark_as_complete":
            await message.reply("complete")
            return

        if "hello" in message.content:
            await message.reply("hello there!")
            return

        if "thanks" in message.content:
            await message.reply("No worries mate!")
            return

        if "unsure" in message.content:
            await message.reply("unsure")
        # MAL ACTIONS ENDS HERE

        await message.reply("I have no Idea what you're talking about")
        return

    return

client.run(os.getenv("TOKEN"))
