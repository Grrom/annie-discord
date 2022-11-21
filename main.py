from enum import Enum
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


@ client.command(description="Take a  hiragana, katakana or kanji quiz.")
async def quiz(ctx):
    await ctx.respond(f"<@{ctx.author.id}> Which writing system would you like to practice?", view=annie.PickWritingSystem(ctx.author.id, ctx.channel))
    return


class WeekDays(Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"

# TODO add recommend slash command


@ client.command(description="Display the anime release schedule for the day")
async def schedule(ctx, day: discord.Option(WeekDays,  "Which day do you want the schedule of?")):
    theDay = day.value
    await ctx.respond(f"Checking schedule for {theDay}, please wait a bit")
    await ctx.trigger_typing()

    scheds = await annie.get_schedule(theDay)
    scheds = sorted(scheds, key=lambda d: d['score'] or 0, reverse=True)

    sample_pages = []

    for result in scheds:
        sample_pages.append(annie.anime_to_embed(
            result, title=f"{theDay}'s scheduled shows are..."))

    paginator = pages.Paginator(
        pages=sample_pages, loop_pages=True, custom_view=annie.MalActions(ctx=ctx))

    await paginator.respond(ctx.interaction, ephemeral=False)
    return


@ client.command(description="Search an anime.")
async def search(ctx, anime_title: discord.Option(str,  "The name of the anime you want to search.")):
    await ctx.respond("Wait lemme look it up.")
    await ctx.trigger_typing()
    results = await annie.search_anime(anime_title)
    if len(results) == 0:
        await ctx.respond("Sorry I couldn't find that show, try another keyword.")
        return

    sample_pages = []

    for result in results:
        sample_pages.append(annie.anime_to_embed(result, title="Found it!"))

    paginator = pages.Paginator(
        pages=sample_pages, loop_pages=True, custom_view=annie.MalActions(ctx))
    await paginator.respond(ctx.interaction, ephemeral=False)
    return


@ client.command(description="Get a list of commands available.")
async def help(ctx):
    embed = discord.Embed(
        title=f"Commands available:",
        color=discord.Color.yellow()
    )

    embed.add_field(
        name="/schedule", value="Get the airing shows for a specified day of the week.", inline=False)
    embed.add_field(
        name="/search", value="Search for an anime.", inline=False)
    embed.add_field(
        name="/quiz", value="Take a Kanji or Kana quiz.", inline=False)
    embed.add_field(
        name="/sauce", value="Get the title of an anime based on a screenshot, Note:  you can also use simply send .sauce and attach an image if you don't have an image link available.", inline=False)

    await ctx.respond(embed=embed)
    return


@ client.command(description='Get the title of the anime from a screenshot. You can also type "sauce" and attach the screenshot.')
async def sauce(ctx, image_link: discord.Option(str,  "Link to the screenshot.")):
    await saucenao.get_sauce(ctx=ctx, image_link=image_link)
    return


@ client.command(description="Get an anime recommendation.")
async def recommend(ctx):
    await ctx.respond("Hmmm... wait, I'll check some titles you might like.")

    await ctx.trigger_typing()
    response = await annie.get_recommendations(ctx.author.id)
    if response is None:
        await ctx.send_followup("Sorry but I don't recognize your discord account, have you linked you discord account in https://client-annie.me ?")
        return
    await ctx.send_followup(embed=annie.anime_to_embed(response, title="I think you might like"), view=annie.AnotherRecommendation(0, ctx.channel))

    if response.get("trailerUrl") is not None:
        await ctx.send_followup("Here's a trailer for it: " + response["trailerUrl"])
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

        if ".sauce" in message.content or intention == "ask_sauce":
            await saucenao.get_sauce(message=message)
            return

        if intention == "quiz":
            await message.reply(f"<@{message.author.id}> Which writing system would you like to practice?", view=annie.PickWritingSystem(message.author.id, message.channel))
            return

        if intention == "ask_recommendation":
            await message.reply("Hmmm... wait, I'll check some titles you might like.")

            async with message.channel.typing():
                response = await annie.get_recommendations(message.author.id)
                if response is None:
                    await message.reply("Sorry but I don't recognize your discord account, have you linked you discord account in https://client-annie.me ?")
                    return
                await message.reply(embed=annie.anime_to_embed(response, title="I think you might like"), view=annie.AnotherRecommendation(0, message.channel))

                if response.get("trailerUrl") is not None:
                    await message.reply("Here's a trailer for it: " + response["trailerUrl"])
                return
            return

        if intention == "schedule":
            await message.reply("Use /schedule to get the schedule")
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
