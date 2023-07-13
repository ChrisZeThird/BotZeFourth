import discord


def init_embed():
    # Name and description
    embed = discord.Embed(title="OC Name",
                          description="",
                          colour=0x00b0f4)

    # Misc information
    embed.add_field(name="Age",
                    value="",
                    inline=True)

    embed.add_field(name="Nationality",
                    value="",
                    inline=True)

    embed.add_field(name="Gender",
                    value="",
                    inline=True)

    embed.add_field(name="Sexuality",
                    value="")

    return embed
