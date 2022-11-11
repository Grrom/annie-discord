import os

import discord

from discord.enums import MessageType

from dotenv import load_dotenv
from utils.saucenao import saucenao
from utils.annie_api import annie

from discord.ext import commands, pages
from utils.intention_recognition.load import get_intention

load_dotenv()

client = discord.Bot(intents=discord.Intents.default())
annie_id = "<@955202644702556260>"


@ client.event
async def on_ready():
    print("========================")
    print("|-- Annie is online! --|")
    print("========================")


@ client.command(description="Search an anime.")
async def search(ctx, anime_title: discord.Option(str)):
    await ctx.respond("Wait lemme look it up.")
    await ctx.trigger_typing()
    results = await annie.search_anime(anime_title)
    if len(results) == 0:
        await ctx.respond("Sorry I couldn't find that show, try another keyword.")
        return

    sample_pages = []

    for result in results:
        sample_pages.append(await annie.anime_to_embed(result, title="Found it!"))

    paginator = pages.Paginator(
        pages=sample_pages, loop_pages=True, custom_view=annie.MalActions(ctx))
    await paginator.respond(ctx.interaction, ephemeral=False)
    return


@ client.event
async def on_message(message):

    if message.author == client.user:
        return

    async def is_reply_to_annie():
        if message.type == MessageType.reply:
            return ((await message.channel.fetch_message(message.reference.message_id)).author.id == client.user.id)
        else:
            return False

    if (annie_id in message.content) or (str(message.channel.type) == "private" and ".register" not in message.content) or await is_reply_to_annie():

        intention = get_intention(message.content)

        if intention == "ask_sauce":
            await saucenao.get_sauce(message)
            return

        if intention == "quiz":
            # await ctx.trigger_typing()
            await message.reply("Which writing system would you like to practice?", view=annie.PickWritingSystem(message.author.id, message.channel))
            return

        if intention == "ask_recommendation":
            await message.reply("Hmmm... wait, I'll check some titles you might like.")

            async with message.channel.typing():
                response = await annie.get_recommendations(message.author.id)
                if response is None:
                    await message.reply("Sorry but I don't recognize your discord account, have you linked you discord account in https://client-annie.me ?")
                    return
                await message.reply(embed=await annie.anime_to_embed(response, title="I think you might like"), view=annie.AnotherRecommendation(0, message.channel))

                if response.get("trailerUrl") is not None:
                    await message.reply("Here's a trailer for it: " + response["trailerUrl"])
                return
            return

        if intention in ["add_to_watchlist", "drop_from_watchlist", "put_on_hold", "mark_as_complete"]:
            await message.reply("Use /search to search a show and perform MyAnimeList actions")
            return

        if "hello" in message.content:
            await message.reply("hello there!")
            return

        if "thanks" in message.content:
            await message.reply("No worries mate!")
            return

        if intention == "unsure":
            await message.reply("I have no Idea what you're talking about.")

        return

    return

client.run(os.getenv("TOKEN"))
