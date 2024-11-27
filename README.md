# About the project
BotZeFourth is a powerful and versatile Discord bot designed specifically for artists to streamline the management and organization of their artwork and character information.

Key features include:

- **Automated Thread Creation**: When artists post artwork in designated channels, the bot automatically creates threads for each piece, ensuring discussions can take place without cluttering the main chat.
- **Custom Information Cards**: Artists can easily create, modify, or delete detailed information cards, presented in an embedded format. These cards help keep communities informed about the artist’s creations and characters. The bot offers various templates for character information, including basic details and more complex options like D&D-style character sheets, with **pagination**!

For more information, write me at *chriszethird.contact@gmail.com*. You can also join my [discord server](https://discord.gg/TcwjZhE) to stay up to date on the development of the bot and 
submit ideas (you can also use the `/suggest` command on your server).

**Please note BotZeFourth is not a moderation bot and won't be supporting moderation 
features**.

# Quick set-up
You will first have to give the bot roles that can use the database system. Otherwise, you won't be able to use any
command related to OC management. You'll need the `/addrole` command:

![ezgif-7-c6842f338c](https://github.com/user-attachments/assets/99ce5601-eeda-4fe1-ae50-9175cd526bda)


Then give the bot channel where 
artworks are being posted using `/addchannel` command:


![ezgif-7-f1e8baa41a](https://github.com/user-attachments/assets/dc428d2d-5448-41a4-a3f4-249d632aacdc)



This way, you can allow artists to post their creation and immediately create a thread to 
enable interactions between the author and viewers without cluttering the main channel (any message without an 
attachment will be deleted). This command is not mandatory.

# Commands

## List

To access the list of all the commands, you just need to use the `/help` command. It takes an optional argument, whether you need to know the command directly, or
the commands of a specific category.

## Examples

### Adding an OC

To create a new character sheet, use `/ocadd`. You will be asked to send a picture for your character first, and then select options using different drop down menus. A pop-up form should then appear on your screen where you will fill your OC information.

![ezgif-2-294ad19be9](https://github.com/user-attachments/assets/609739bd-e768-4589-856f-a3ba3e35d596)


### Checking one or multiple OC(s)

This is the most interesting part for your discorc community as an artist. You can use `/ocinfo` to get information on a specific OC from a specific artist or `ocrandom` to get a random OC from any artist on your server. The bot will then send an embed with all the information set by the original artist:

<img src="https://github.com/user-attachments/assets/6d66395e-3a51-459f-b8b1-cf91b1189298" width="600" />


You can also get the list of OC(s) owned by an artist with `/oclist`.

# Acknowledgements

I would like to thank AlexFlipnote for the time he took to help me on various issues when I first started coding this bot. He also provided a 
very nice quick setup [template](https://github.com/AlexFlipnote/discord_bot.py) to create a discord bot on his own 
GitHub page and even updated his [PostgresLite](https://github.com/AlexFlipnote/PostgresLite) library with async support.
