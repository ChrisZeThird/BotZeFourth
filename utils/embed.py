import discord
from io import BytesIO


# -- DEFAULT CHARACTER EMBED -- #
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


# -- DND EMBED TEMPLATE -- #
def dnd_character_embed(character_data):
    """
    Create an embed for a D&D character sheet.
    :param character_data: A dictionary containing character data
    :return: A discord.Embed object
    """
    embed = discord.Embed(
        title=f"{character_data['character_name']} - Level {character_data['level']} {character_data['class']}",
        description=f"Background: {character_data['background']} | Species: {character_data['species']}\nSubclass: {character_data['subclass']}",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=character_data['oc_picture'])  # Artist avatar

    # Basic stats
    embed.add_field(name="**Basic Stats**",
                    value=f"**AC**: {character_data['ac']}\n"
                          f"**HP**: {character_data['current_hp']}/{character_data['max_hp']} (Temp: {character_data['temp_hp']})\n"
                          f"**Initiative**: {character_data['initiative']}\n"
                          f"**Speed**: {character_data['speed']} ft\n"
                          f"**Proficiency Bonus**: {character_data['proficiency_bonus']}",
                    inline=False)

    # Abilities
    embed.add_field(name="**Ability Scores**",
                    value=f"**STR**: {character_data['strength']} ({character_data['str_mod']})\n"
                          f"**DEX**: {character_data['dexterity']} ({character_data['dex_mod']})\n"
                          f"**CON**: {character_data['constitution']} ({character_data['con_mod']})\n"
                          f"**INT**: {character_data['intelligence']} ({character_data['int_mod']})\n"
                          f"**WIS**: {character_data['wisdom']} ({character_data['wis_mod']})\n"
                          f"**CHA**: {character_data['charisma']} ({character_data['cha_mod']})",
                    inline=True)

    # Weapons, traits, and feats
    embed.add_field(name="**Weapons & Damage**", value=character_data['weapons'], inline=False)
    embed.add_field(name="**Species Traits**", value=character_data['species_traits'], inline=False)
    embed.add_field(name="**Feats**", value=character_data['feats'], inline=False)

    # Equipment and other proficiencies
    embed.add_field(name="**Equipment & Proficiencies**",
                    value=f"**Armor**: {character_data['armor_training']}\n"
                          f"**Weapons**: {character_data['weapon_training']}\n"
                          f"**Tools**: {character_data['tools_training']}",
                    inline=False)

    # Backstory and Appearance
    embed.add_field(name="**Backstory**", value=character_data['backstory'], inline=False)
    embed.add_field(name="**Appearance**", value=character_data['appearance'], inline=False)

    # Footer
    embed.set_footer(text=f"Character sheet created by {character_data['user_name']}")

    return embed

