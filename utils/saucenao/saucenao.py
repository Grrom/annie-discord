import requests
import discord
import re


async def get_sauce(message=None, ctx=None, image_link=None):
    if message is not None:
        await message.reply("Hmmm... lemme check.")
    if ctx is not None:
        await ctx.respond("Hmmm... lemme check.")

    async def _get_sauce():
        no_link = Exception(
            "Please include an anime screenshot or a link to a screenshot.")
        no_sauce = Exception(
            "Sorry I couldn't find the sauce for that image.")

        link = None

        if image_link is None:
            try:
                if not message.attachments:
                    for word in message.content.replace("sauce", "").split():
                        word = word[word.find("http"):]
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
        else:
            link = image_link

        try:
            response = requests.post(
                f"https://annie-api.azurewebsites.net/sauce", json={
                    "imageLink": link
                })
            if response.status_code == 200:
                return response.json()
            raise no_sauce
        except Exception as exception:
            if "Connection refused" in str(exception):
                raise Exception(
                    "Sorry my Image Search Server is not available right now.") from exception
            raise no_sauce from exception

    try:
        response = await _get_sauce()

        if len(response["data"]) == 0:
            if message is not None:
                await message.reply(
                    "Hmmm... I can't seem to find this one. are you sure this is an anime screenshot?"
                )
            if ctx is not None:
                await message.reply(
                    "Hmmm... I can't seem to find this one. are you sure this is an anime screenshot?"
                )
            return

        sauce = response["data"][0]
        embed = discord.Embed(
            title="✅ Sauce Found!",
            color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=sauce["thumbnail"])
        embed.add_field(
            name="Title", value=sauce["sauce"] or "unknown", inline=True)
        embed.add_field(name="Similarity",
                        value=f"{sauce['similarity']}%", inline=True)
        embed.add_field(
            name="Source", value=sauce["extUrls"][0] or "link not available", inline=False)

        if message is not None:
            await message.reply(embed=embed)
        if ctx is not None:
            await ctx.send_followup(embed=embed)

        if float(sauce['similarity']) < 40:
            if message is not None:
                await message.reply(
                    "Sorry I couldn't find good matches, are you sure this is an anime screenshot?"
                )
            if ctx is not None:
                await ctx.send_followup(
                    "Sorry I couldn't find good matches, are you sure this is an anime screenshot?"
                )

    except Exception as exception:
        if message is not None:
            await message.reply(str(exception))
        if ctx is not None:
            await ctx.send_followup(str(exception))
        return
