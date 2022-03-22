import os

import discord
import requests

from dotenv import load_dotenv

load_dotenv()

client = discord.Client()


async def get_sauce():
    try:
        response = requests.get("http://localhost:8080/sauce")
        if response.status_code == 200:
            return response.json()
        raise Exception("Sorry I couldn't find the sauce for that image.")
    except Exception as exception:
        if "Connection refused" in str(exception):
            raise Exception(
                "Sorry my Image Search Server is not available right now.") from exception
        raise Exception(
            "Sorry I couldn't find the sauce for that image.") from exception


@ client.event
async def on_ready():
    print("========================")
    print("|-- Annie is online! --|")
    print("========================")


@ client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "<@!955202644702556260>" in message.content:
        if "hello" in message.content:
            await message.channel.send("hello there!")
            return

        if "test" in message.content:
            try:
                sauce = await get_sauce()
                embed = discord.Embed(
                    title="✅ Sauce Found!",
                    color=discord.Color.yellow()
                )
                embed.set_thumbnail(
                    url="https://raw.githubusercontent.com/Grrom/my_wallpapers/main/mylofi.png")
                embed.add_field(name="Database",
                                value=sauce["database"], inline=True)
                embed.add_field(name="Accuracy",
                                value=f"{sauce['accuracy']}%", inline=True)
                embed.add_field(
                    name="Author", value=sauce["author"], inline=True)
                embed.add_field(
                    name="Title", value=sauce["title"], inline=True)

                await message.channel.send(embed=embed)
            except Exception as exception:
                await message.channel.send(str(exception))

    elif "<@!955202644702556260>" in message.content:
        await message.channel.send("I have no Idea what you're talking about")
        return

    return

client.run(os.getenv("TOKEN"))