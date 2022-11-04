import requests
import discord


async def get_recommendations(discordId):

    async def _get_recommendations():
        try:
            response = requests.get(
                # f"http://localhost:8080/recommendations-discord?discord_id=${discordId}")
                f"https://annie-api.azurewebsites.net/recommendations-discord?discord_id=${discordId}")
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


async def anime_to_embed(anime):

    embed = discord.Embed(
        title="I think you might like.",
        color=discord.Color.yellow()
    )
    embed.set_thumbnail(url=anime["thumbnail"])
    embed.add_field(
        name="Title", value=anime["name"] or "unknown", inline=True)
    embed.add_field(
        name="MAL url", value=anime["malUrl"] or "unknown", inline=True)
    embed.add_field(
        name="Genres", value=anime["genres"] or "unknown", inline=False)
    embed.add_field(name="Synopsis",
                    value=f"{anime['synopsis'][:998]}...", inline=False)
    embed.add_field(
        name="Trailer", value=anime["trailer"] or "link not available", inline=False)

    return embed
