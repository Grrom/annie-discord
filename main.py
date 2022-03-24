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
    annie_id = "<@!955202644702556260>"

    if message.author == client.user:
        return

    if annie_id in message.content:
        if "hello" in message.content:
            await message.channel.send("hello there!")
            return

        if "sauce" in message.content:
            sauce = None
            try:
                if not message.attachments:
                    link = None
                    for word in message.content.replace(annie_id, "").split():
                        if "http" in word:
                            link = word
                    if link:
                        sauce = await get_sauce(link)
                    else:
                        await message.channel.send("Please include an anime screenshot or a link to a screenshot.")
                else:
                    sauce = await get_sauce(message.attachments[0].url)

            except Exception as exception:
                await message.channel.send(str(exception))

            if sauce:
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

        if "test" in message.content:
            await message.channel.send("test")
        return

    elif annie_id in message.content:
        await message.channel.send("I have no Idea what you're talking about")
        return

    return

client.run(os.getenv("TOKEN"))
