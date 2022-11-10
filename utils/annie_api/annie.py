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


async def search_anime(queryString):

    async def search():
        try:
            response = requests.get(
                # f"http://localhost:8080/search-anime?queryString={queryString}")
                f"https://annie-api.azurewebsites.net/search-anime?queryString={queryString}")
            if response.status_code == 200:
                return response.json()
            else:
                return {error: "no response"}
        except Exception as e:
            return {error: "no response"}

    result = await search()

    if result.get("error") is not None:
        return None

    return result["result"]


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
            # f"https://annie-api.azurewebsites.net/search-anime?queryString={queryString}")
            if response.status_code == 200:
                return response.json()
            else:
                return {error: "Something went wrong"}
        except Exception as e:
            return {error: "Something went wrong"}

    result = await update()

    return result


async def anime_to_embed(anime, title):

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
        name="Score", value=anime["score"] or "unknown", inline=False)
    embed.add_field(name="Synopsis",
                    value=f"{(anime['synopsis'] or 'no synopsis')[:998]}...", inline=False)
    embed.add_field(
        name="Trailer", value=anime["trailer"] or "link not available", inline=False)

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
            await interaction.message.reply(embed=await anime_to_embed(response, title="I think you might like"), view=AnotherRecommendation(self.index, self.channel))
            if response.get("trailerUrl") is not None:
                await interaction.message.reply("Here's a trailer for it: " + response["trailerUrl"])
                return


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
    def __init__(self, animeId, animeName, ctx):
        super().__init__()
        self.animeId = animeId
        self.animeName = animeName
        self.ctx = ctx

    async def update(self, status, interaction):
        await interaction.response.send_message("Updating wait a sec.")

        await self.ctx.trigger_typing()
        response = await update_anime(self.animeId, status, 0, 0, interaction.user.id)
        if response.get("error") is not None:
            await interaction.message.reply(response["error"])
        else:
            if status is "plan_to_watch":
                await interaction.message.reply(f"I've Added {self.animeName} to your watchlist.")
            if status is "on_hold":
                await interaction.message.reply(f"I've put {self.animeName} on hold.")
            if status is "dropped":
                await interaction.message.reply(f"Dropped {self.animeName}, sadge 😢")

    @ discord.ui.button(label="Plan to Watch", style=discord.ButtonStyle.blurple, emoji="➕")
    async def planToWathc(self, button, interaction):
        await self.update("plan_to_watch", interaction)

    @ discord.ui.button(label="Mark Complete", style=discord.ButtonStyle.green, emoji="✔️")
    async def completed(self, button, interaction):
        await interaction.response.send_message("Wanna rate the show before marking it as complete?", view=LeaveRating(self.animeId, self.animeName, self.ctx))

    @ discord.ui.button(label="Put on Hold", style=discord.ButtonStyle.gray, emoji="⏱️")
    async def hold(self, button, interaction):
        await self.update("on_hold", interaction)

    @ discord.ui.button(label="Drop", style=discord.ButtonStyle.danger, emoji="⏹")
    async def drop(self, button, interaction):
        await self.update("dropped", interaction)
