import discord
from io import BytesIO


# Basic card
def default_embed(user_name,
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

    # Create a discord.File object from the image data
    file = discord.File(BytesIO(oc_picture), filename='oc_picture.png')

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
    embed.set_image(url=f"attachment://{file.filename}")  # Set the image using the discord.File object
    embed.set_footer(text=f"Author: {user_name}")  # Artist name at the bottom

    return embed, file

# TODO Add different type of template with pages


# DnD Template
def dnd_template(user_name,
                 oc_name,
                 oc_age,
                 oc_nationality,
                 oc_gender,
                 oc_sexuality,
                 oc_universe,
                 oc_story,
                 oc_picture,
                 oc_colour,
                 avatar_url,
                 oc_class,
                 oc_level,
                 oc_background,
                 oc_alignment,
                 oc_languages,
                 oc_strength,
                 oc_dexterity,
                 oc_constitution,
                 oc_intelligence,
                 oc_wisdom,
                 oc_charisma):

    # Set first page as default page
    page1, file = default_embed(user_name, oc_name, oc_age, oc_nationality, oc_gender, oc_sexuality, oc_universe,
                                oc_story, oc_picture, oc_colour, avatar_url)

    # Set second page (extra details)
    page2 = discord.Embed(title="Character Details", colour=oc_colour)
    page2.add_field(name="Class", value=oc_class, inline=True)
    page2.add_field(name="Level", value=oc_level, inline=True)
    page2.add_field(name="Background", value=oc_background, inline=True)
    page2.add_field(name="Alignment", value=oc_alignment, inline=True)
    page2.add_field(name="Languages", value=oc_languages)

    # Set third page (stats)
    page3 = discord.Embed(title="Stats", colour=oc_colour)
    page3.add_field(name="Strength", value=oc_strength, inline=True)
    page3.add_field(name="Dexterity", value=oc_dexterity, inline=True)
    page3.add_field(name="Constitution", value=oc_constitution, inline=True)
    page3.add_field(name="Intelligence", value=oc_intelligence, inline=True)
    page3.add_field(name="Wisdom", value=oc_wisdom, inline=True)
    page3.add_field(name="Charisma", value=oc_charisma)

    return page1, page2, page3, file

# Furry Template

# Comics Template
