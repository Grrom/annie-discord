import requests


async def get_recommendations(discordId):

    async def _get_recommendations():
        try:
            response = requests.get(
                f"http://localhost:8080/recommendations-discord?discord_id=${discordId}")
            # f"https://annie-api.azurewebsites.net/sauce?discord_id=${discordId}")
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            return []

    recommendations = await _get_recommendations()
    return recommendations
