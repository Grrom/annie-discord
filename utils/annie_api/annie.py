import requests
import discord


async def get_recommendations(discordId, offset=0):

    async def _get_recommendations():
        try:
            response = requests.get(
                # f"http://localhost:8080/recommendations-discord?discord_id={discordId}&offset={offset}")
                f"https://annie-api.azurewebsites.net/recommendations-discord?discord_id={discordId}&offset={offset}")
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            return []

    recommendations = await _get_recommendations()

    if recommendations.get("error") is not None:
        return None

    return recommendations


async def get_quiz(writing_system, ordering_system):
    async def send_request():
        url = f"http://localhost:8080/kana-quiz?writing={writing_system}&ordering={ordering_system}"
        if writing_system == "kanji":
            url = f"http://localhost:8080/kanji-quiz?writing={writing_system}&ordering={ordering_system}"

        try:
            response = requests.get(url)
            # f"https://annie-api.azurewebsites.net/search-anime?queryString={queryString}")
            if response.status_code == 200:
                return response.json()
            else:
                return {error: "no response"}
        except Exception as e:
            return {error: "no response"}

    result = await send_request()

    return result


async def search_anime(queryString):

    async def search():
        try:
            response = requests.get(
                f"http://localhost:8080/search-anime?queryString={queryString}")
            # f"https://annie-api.azurewebsites.net/search-anime?queryString={queryString}")
            if response.status_code == 200:
                return response.json()
            else:
                return {error: "no response"}
        except Exception as e:
            return {error: "no response"}

    result = await search()

    if result.get("error") is not None:
        return None

    return result["results"]


async def update_anime(animeId, status, score, num_watched_episodes, discord_id):
    async def update():
        params = {}
        if score is not None:
            params = {
                "animeId": animeId,
                "status": status,
                "score": score,
                "num_watched_episodes": num_watched_episodes,
                "discord_id": f"{discord_id}"
            }
        else:
            params = {
                "animeId": animeId,
                "status": status,
                "discord_id": f"{discord_id}"
            }

        try:
            response = requests.post(
                f"http://localhost:8080/update-anime-status-discord", json=params)
            # f"https://annie-api.azurewebsites.net/update-anime-status-discord", json=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {error: "Something went wrong"}
        except Exception as e:
            return {error: "Something went wrong"}

    result = await update()

    return result


def anime_to_embed(anime, title):

    embed = discord.Embed(
        title=title,
        color=discord.Color.yellow()
    )
    embed.set_thumbnail(url=anime["thumbnail"])
    embed.add_field(
        name="Title", value=anime["name"] or "unknown", inline=True)
    embed.add_field(
        name="MAL url", value=anime["malUrl"] or "unknown", inline=True)
    embed.add_field(
        name="Genres", value=anime["genres"] or "unknown", inline=False)
    embed.add_field(
        name="Score", value=anime["score"] or "unknown", inline=True)
    embed.add_field(
        name="MAL id", value=anime["id"] or "unknown", inline=True)
    embed.add_field(name="Synopsis",
                    value=f"{(anime['synopsis'] or 'no synopsis')[:998]}...", inline=False)
    embed.add_field(
        name="Trailer", value=anime["trailer"] or "link not available", inline=False)

    return embed


def quiz_embed(writing_system, ordering_system, current_index, current_score, questions):
    embed = discord.Embed(
        title=f"{writing_system} {ordering_system} quiz.",
        color=discord.Color.yellow()
    )

    embed.add_field(
        name="Question Number", value=current_index, inline=True)
    embed.add_field(
        name="Current Score", value=current_score, inline=True)
    embed.add_field(
        name="Choose the corresponding reading for the character below.", value=questions[current_index]["kana"], inline=False)

    return embed


class AnotherRecommendation(discord.ui.View):
    def __init__(self, index, channel):
        super().__init__()
        self.index = index
        self.channel = channel

    @ discord.ui.button(label="Get another recommendation.", style=discord.ButtonStyle.primary, emoji="⏭️")
    async def button_callback(self, button, interaction):
        self.index += 1

        await interaction.response.send_message(
            "hmm... wait I'll think of something else...")

        async with self.channel.typing():
            response = await get_recommendations(interaction.user.id, self.index)
            await interaction.message.reply(embed=await anime_to_embed(response, title="How about this?"), view=AnotherRecommendation(self.index, self.channel))
            if response.get("trailerUrl") is not None:
                await interaction.message.reply("Here's a trailer for it: " + response["trailerUrl"])
                return


class PickWritingSystem(discord.ui.View):
    def __init__(self, discordId, channel):
        super().__init__()
        self.discordId = discordId
        self.channel = channel

    async def choose_ordering_system(self, interaction, writing_system):
        if self.discordId == interaction.user.id:
            await interaction.response.send_message(f"Choose {writing_system} Quiz", view=PickOrderingSystem(writing_system, self.channel))

    @ discord.ui.button(label="Hiragana", style=discord.ButtonStyle.primary)
    async def hiragana(self, button, interaction):
        await self.choose_ordering_system(interaction, "hiragana")

    @ discord.ui.button(label="Katakana", style=discord.ButtonStyle.primary)
    async def katakana(self, button, interaction):
        await self.choose_ordering_system(interaction, "katakana")

    @ discord.ui.button(label="Kanji", style=discord.ButtonStyle.primary)
    async def kanji(self, button, interaction):
        await interaction.response.send_message("Choose Quiz", view=PickKanjiReading())


class PickOrderingSystem(discord.ui.View):
    def __init__(self, writing_system, channel):
        super().__init__()
        self.writing_system = writing_system
        self.channel = channel

    async def get_quiz(self, ordering_system, interaction):
        async with self.channel.typing():
            await interaction.response.send_message(f"Preparing {self.writing_system} {ordering_system} Quiz pls wait a bit...")
            questions = await get_quiz(self.writing_system, ordering_system)

            _quiz_embed = quiz_embed(
                self.writing_system, ordering_system, 0, 0, questions)

            await interaction.message.reply("First Question:", embed=_quiz_embed, view=QuizChoices(questions, 0, 0, self.writing_system, ordering_system))
            return

    @ discord.ui.button(label="Gojuuon", style=discord.ButtonStyle.primary)
    async def gojuuon(self, button, interaction):
        await self.get_quiz("gojuuon", interaction)

    @ discord.ui.button(label="Dakuon", style=discord.ButtonStyle.primary)
    async def dakuon(self, button, interaction):
        await self.get_quiz("dakuon", interaction)

    @ discord.ui.button(label="Youon", style=discord.ButtonStyle.primary)
    async def youon(self, button, interaction):
        await self.get_quiz("youon", interaction)


class QuizChoices(discord.ui.View):
    def __init__(self, questions, current_index,  current_score, writing_system, ordering_system):
        super().__init__()
        self.questions = questions
        self.current_index = current_index
        self.current_score = current_score
        self.writing_system = writing_system
        self.ordering_system = ordering_system

        self.choice1.label = questions[current_index]["romajiChoices"][0]
        self.choice2.label = questions[current_index]["romajiChoices"][1]
        self.choice3.label = questions[current_index]["romajiChoices"][2]
        self.choice4.label = questions[current_index]["romajiChoices"][3]

    async def next_question(self, answer, interaction):
        if self.questions[self.current_index]["correctAnswer"] == answer:
            await interaction.response.send_message("Correct!")
            self.current_score += 1
        else:
            await interaction.response.send_message(f"the answer is {self.questions[self.current_index]['correctAnswer']}")

        self.current_index += 1
        if self.current_index == 10:
            score_embed = discord.Embed(
                title=f"You got: {self.current_score} out of 10!",
                color=discord.Color.green()
            )
            await interaction.message.reply(f"Quiz Done: ", embed=score_embed)
        else:
            _quiz_embed = quiz_embed(
                self.writing_system, self.ordering_system, self.current_index, self.current_score, self.questions)
            await interaction.message.reply(f"Next Question:", embed=_quiz_embed, view=QuizChoices(self.questions, self.current_index, self.current_score, self.writing_system, self.ordering_system))

    @ discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def choice1(self, button, interaction):
        await self.next_question(button.label, interaction)

    @ discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def choice2(self, button, interaction):
        await self.next_question(button.label, interaction)

    @ discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def choice3(self, button, interaction):
        await self.next_question(button.label, interaction)

    @ discord.ui.button(label="4", style=discord.ButtonStyle.primary)
    async def choice4(self, button, interaction):
        await self.next_question(button.label, interaction)


class PickKanjiReading(discord.ui.View):
    @ discord.ui.button(label="Onyomi", style=discord.ButtonStyle.primary)
    async def onyomi(self, button, interaction):
        await interaction.response.send_message("Onyomi")

    @ discord.ui.button(label="Kunyomi", style=discord.ButtonStyle.primary)
    async def kunyomi(self, button, interaction):
        await interaction.response.send_message("Kunyomi")

    @ discord.ui.button(label="English", style=discord.ButtonStyle.primary)
    async def english(self, button, interaction):
        await interaction.response.send_message("English")


class LeaveRating(discord.ui.View):

    def __init__(self, animeId, animeName, ctx):
        super().__init__()
        self.animeId = animeId
        self.animeName = animeName
        self.ctx = ctx

    async def update_completed(self, score, interaction):
        await interaction.response.send_message("Updating wait a sec.")

        await self.ctx.trigger_typing()
        response = await update_anime(self.animeId, "completed", score, 999, interaction.user.id)

        if response.get("error") is not None:
            await interaction.message.reply(response["error"])
        else:
            await interaction.message.reply(f"Marked {self.animeName} as completed.")

    @ discord.ui.button(label="No rating", style=discord.ButtonStyle.primary, emoji="🙅🏻‍♂️")
    async def no_rating(self, button, interaction):
        await self.update_completed(0, interaction)

    @ discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def one(self, button, interaction):
        await self.update_completed(1, interaction)

    @ discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def two(self, button, interaction):
        await self.update_completed(2, interaction)

    @ discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def three(self, button, interaction):
        await self.update_completed(3, interaction)

    @ discord.ui.button(label="4", style=discord.ButtonStyle.primary)
    async def four(self, button, interaction):
        await self.update_completed(4, interaction)

    @ discord.ui.button(label="5", style=discord.ButtonStyle.primary)
    async def five(self, button, interaction):
        await self.update_completed(5, interaction)

    @ discord.ui.button(label="6", style=discord.ButtonStyle.primary)
    async def six(self, button, interaction):
        await self.update_completed(6, interaction)

    @ discord.ui.button(label="7", style=discord.ButtonStyle.primary)
    async def seven(self, button, interaction):
        await self.update_completed(7, interaction)

    @ discord.ui.button(label="8", style=discord.ButtonStyle.primary)
    async def eight(self, button, interaction):
        await self.update_completed(8, interaction)

    @ discord.ui.button(label="9", style=discord.ButtonStyle.primary)
    async def nine(self, button, interaction):
        await self.update_completed(9, interaction)

    @ discord.ui.button(label="10", style=discord.ButtonStyle.primary)
    async def ten(self, button, interaction):
        await self.update_completed(10, interaction)


class MalActions(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    async def update(self, status, interaction):
        await interaction.response.send_message("Updating wait a sec.")

        animeId = interaction.message.embeds[0].fields[4].value
        animeName = interaction.message.embeds[0].fields[0].value

        await self.ctx.trigger_typing()
        response = await update_anime(animeId, status, 0, 0, interaction.user.id)
        if response.get("error") is not None:
            await interaction.message.reply(response["error"])
        else:
            if status == "plan_to_watch":
                await interaction.message.reply(f"I've Added {animeName} to your watchlist.")
            if status == "on_hold":
                await interaction.message.reply(f"I've put {animeName} on hold.")
            if status == "dropped":
                await interaction.message.reply(f"Dropped {animeName}, sadge 😢")

    @ discord.ui.button(label="Plan to Watch", style=discord.ButtonStyle.blurple, emoji="➕")
    async def planToWatch(self, button, interaction):
        await self.update("plan_to_watch", interaction)

    @ discord.ui.button(label="Mark Complete", style=discord.ButtonStyle.green, emoji="✔️")
    async def completed(self, button, interaction):
        animeId = interaction.message.embeds[0].fields[4].value
        animeName = interaction.message.embeds[0].fields[0].value

        await interaction.response.send_message("Wanna rate the show before marking it as complete?", view=LeaveRating(animeId, animeName, self.ctx))

    @ discord.ui.button(label="Put on Hold", style=discord.ButtonStyle.gray, emoji="⏱️")
    async def hold(self, button, interaction):
        await self.update("on_hold", interaction)

    @ discord.ui.button(label="Drop", style=discord.ButtonStyle.danger, emoji="⏹")
    async def drop(self, button, interaction):
        await self.update("dropped", interaction)
