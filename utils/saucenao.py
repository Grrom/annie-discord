import requests
import discord


async def get_sauce(message):

    async def _get_sauce():
        no_link = Exception(
            "Please include an anime screenshot or a link to a screenshot.")
        no_sauce = Exception(
            "Sorry I couldn't find the sauce for that image.")

        link = None

        try:
            if not message.attachments:
                for word in message.content.replace("sauce", "").split():
                    if "https://" in word or "http://" in word:
                        link = word
                        break
                else:
                    raise no_link
            else:
                link = message.attachments[0].url

        except Exception as exception:
            raise exception
            return

        if link is None:
            raise no_link
            return

        try:
            response = requests.get(
                f"http://localhost:8080/sauce?image_url={link}")
            if response.status_code == 200:
                return response.json()
            raise no_sauce
        except Exception as exception:
            if "Connection refused" in str(exception):
                raise Exception(
                    "Sorry my Image Search Server is not available right now.") from exception
            raise no_sauce from exception

    try:
        sauce = await _get_sauce()
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
        return
