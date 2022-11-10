import requests
import discord


async def get_recommendations(discordId, offset=0):

    async def _get_recommendations():
        try:
            response = requests.get(
                # f"http://localhost:8080/recommendations-discord?discord_id=${discordId}&offset=${offset}")
                f"https://annie-api.azurewebsites.net/recommendations-discord?discord_id=${discordId}&offset=${offset}")
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
                # f"http://localhost:8080/search-anime?queryString=${queryString}")
                f"https://annie-api.azurewebsites.net/search-anime?queryString=${queryString}")
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

    @discord.ui.button(label="Get another recommendation.", style=discord.ButtonStyle.primary, emoji="⏭️")
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


class MalActions(discord.ui.View):

    @discord.ui.button(label="Plan to Watch", style=discord.ButtonStyle.blurple, emoji="➕")
    async def planToWathc(self, button, interaction):

        await interaction.response.send_message(
            "hmm... wait I'll think of something else...")

    @discord.ui.button(label="Mark Complete", style=discord.ButtonStyle.green, emoji="✔️")
    async def completed(self, button, interaction):

        await interaction.response.send_message(
            "hmm... wait I'll think of something else...")

    @discord.ui.button(label="Put on Hold", style=discord.ButtonStyle.gray, emoji="⏱️")
    async def hold(self, button, interaction):

        await interaction.response.send_message(
            "hmm... wait I'll think of something else...")

    @discord.ui.button(label="Drop", style=discord.ButtonStyle.danger, emoji="⏹")
    async def drop(self, button, interaction):

        await interaction.response.send_message(
            "hmm... wait I'll think of something else...")
