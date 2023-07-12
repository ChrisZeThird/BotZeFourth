import discord

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

embed.set_image(url="")  # OC illustration

embed.set_thumbnail(url="")  # Artist avatar

embed.set_footer(text="Author: ")
