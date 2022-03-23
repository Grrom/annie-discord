import os

import discord
import requests

from dotenv import load_dotenv

load_dotenv()

client = discord.Client()


async def get_sauce(image_url):
    try:
        response = requests.get(
            f"http://localhost:8080/sauce?image_url={image_url}")
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

        if "sauce" in message.content:
            try:
                if not message.attachments:
                    await message.channel.send("Please include an anime screenshot.")
                else:
                    sauce = await get_sauce(message.attachments[0].url)

                    embed = discord.Embed(
                        title="✅ Sauce Found!",
                        color=discord.Color.yellow()
                    )
                    embed.set_thumbnail(url=sauce["thumbnail"])
                    embed.add_field(
                        name="Title", value=sauce["title"] or "unknown", inline=True)
                    embed.add_field(name="Accuracy",
                                    value=f"{sauce['accuracy']}%", inline=True)
                    embed.add_field(
                        name="Source", value=sauce["link"] or "link not available", inline=False)

                    await message.channel.send(embed=embed)

                    if sauce['accuracy'] < 60:
                        await message.channel.send(
                            "Sorry I couldn't find good matches, are you sure this is an anime screenshot?"
                        )

            except Exception as exception:
                await message.channel.send(str(exception))
        if "pic" in message.content:
            print(message.attachments[0].url)
            await message.channel.send("test")
            return

    elif "<@!955202644702556260>" in message.content:
        await message.channel.send("I have no Idea what you're talking about")
        return

    return

client.run(os.getenv("TOKEN"))
