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
import discord
from typing import Callable


# Function to fetch DnD character details
async def get_dnd_character_page(index: int, character_id: int):
    # Fetch character data from the database
    result = db.execute("""
        SELECT * FROM DnDCharacters WHERE character_id = ?
    """, (character_id,)).fetchone()

    if not result:
        return None, 0

    # Extract details from the result
    character_name = result['character_name']
    class_name = result['class']
    subclass = result['subclass']
    species = result['species']
    age = result['age']
    gender = result['gender']
    sexuality = result['sexuality']
    background = result['background']
    alignment = result['alignment']
    lvl = result['lvl']
    strength = result['strength']
    dexterity = result['dexterity']
    constitution = result['constitution']
    intelligence = result['intelligence']
    wisdom = result['wisdom']
    charisma = result['charisma']
    color = result['color']
    oc_picture = result['oc_picture']
    backstory = result['backstory']
    appearance = result['appearance']

    # Paginate based on index
    if index == 1:
        embed = discord.Embed(
            title=f"{character_name}'s DnD Character Sheet",
            description=f"**Class**: {class_name}\n**Subclass**: {subclass}\n**Age**: {age}\n**Species**: {species}\n**Gender**: {gender}\n**Sexuality**: {sexuality}\n**Background**: {background}\n**Alignment**: {alignment}\n**Level**: {lvl}",
            color=int(color, 16) if color else 0x3498db
        )
    elif index == 2:
        embed = discord.Embed(
            title=f"{character_name}'s Ability Scores",
            description=(
                f"**Strength**: {strength}\n**Dexterity**: {dexterity}\n"
                f"**Constitution**: {constitution}\n**Intelligence**: {intelligence}\n"
                f"**Wisdom**: {wisdom}\n**Charisma**: {charisma}"
            ),
            color=int(color, 16) if color else 0x3498db
        )
    elif index == 3:
        embed = discord.Embed(
            title=f"{character_name}'s Training and Weapons",
            description=(
                f"**Weapons**: {result['weapons']}\n**Armor Training**: {result['armor_training']}\n"
                f"**Weapon Training**: {result['weapon_training']}\n**Tools Training**: {result['tools_training']}"
            ),
            color=int(color, 16) if color else 0x3498db
        )
    elif index == 4:
        embed = discord.Embed(
            title=f"{character_name}'s Saving Throws and Proficiencies",
            description=(
                f"**Proficiency Bonus**: {result['proficiency_bonus']}\n**Strength Save**: {result['strength_save']}\n"
                f"**Dexterity Save**: {result['dexterity_save']}\n**Constitution Save**: {result['constitution_save']}\n"
                f"**Intelligence Save**: {result['intelligence_save']}\n**Wisdom Save**: {result['wisdom_save']}\n"
                f"**Charisma Save**: {result['charisma_save']}"
            ),
            color=int(color, 16) if color else 0x3498db
        )
    elif index == 5:
        embed = discord.Embed(
            title=f"{character_name}'s Backstory and Appearance",
            description=(
                f"**Backstory**: {backstory}\n**Appearance**: {appearance}"
            ),
            color=int(color, 16) if color else 0x3498db
        )
    elif index == 6:
        embed = discord.Embed(
            title=f"{character_name}'s Picture",
            description="Here's a picture of the character.",
            color=int(color, 16) if color else 0x3498db
        )
        embed.set_thumbnail(url=oc_picture)

    # Set the total pages based on the amount of data (we assume 6 pages for now)
    total_pages = 6

    return embed, total_pages


# Integration with Pagination View
class DndPagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, character_id: int):
        self.interaction = interaction
        self.character_id = character_id
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = discord.Embed(
                description="Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False

    async def edit_page(self, interaction: discord.Interaction):
        emb, total_pages = await get_dnd_character_page(self.index, self.character_id)
        self.update_buttons(total_pages)
        await interaction.response.edit_message(embed=emb, view=self)

    def update_buttons(self, total_pages: int):
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == total_pages
        self.children[2].disabled = total_pages <= 1

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        self.index = 1 if self.index == 6 else 6
        await self.edit_page(interaction)

    async def on_timeout(self):
        message = await self.interaction.original_response()
        await message.edit(view=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1
