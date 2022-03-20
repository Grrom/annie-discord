import discord
import os

from dotenv import load_dotenv

load_dotenv()

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "<@!955202644702556260>" in message.content and "hello" in message.content:
        await message.channel.send("hello there!")
        return
    elif "<@!955202644702556260>" in message.content:
        await message.channel.send("I have no Idea what you're talking about")
        return

    return


client.run(os.getenv("TOKEN"))
