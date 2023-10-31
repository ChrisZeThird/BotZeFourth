import discord


def init_embed(user_name,
               oc_name,
               oc_age,
               oc_nationality,
               oc_gender,
               oc_sexuality,
               oc_universe,
               oc_story,
               oc_picture,
               oc_colour,
               avatar_url):
    # Name and description
    embed = discord.Embed(title=oc_name,
                          description=oc_story,
                          colour=oc_colour)

    # Misc information
    embed.add_field(name="Age",
                    value=oc_age,
                    inline=True)

    embed.add_field(name="Nationality",
                    value=oc_nationality,
                    inline=True)

    embed.add_field(name="Universe",
                    value=oc_universe,
                    inline=True)

    embed.add_field(name="Gender",
                    value=oc_gender,
                    inline=True)

    embed.add_field(name="Sexuality",
                    value=oc_sexuality)

    embed.set_thumbnail(url=avatar_url)  # Artist avatar
    embed.set_image(url=oc_picture)  # OC illustration
    embed.set_footer(text=f"Author: {user_name}")  # Artist name at the bottom

    return embed
