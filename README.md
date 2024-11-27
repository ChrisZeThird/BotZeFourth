*DISCLAIMER: This README file isn't up to date with the current Bot version. It concerns the `legacy` branch only.*

# About the project
BotZeFourth is a powerful and versatile Discord bot designed specifically for artists to streamline the management and organization of their artwork and character information.

Key features include:

- **Automated Thread Creation**: When artists post artwork in designated channels, the bot automatically creates threads for each piece, ensuring discussions can take place without cluttering the main chat.
- **Custom Information Cards**: Artists can easily create, modify, or delete detailed information cards, presented in an embedded format. These cards help keep communities informed about the artist’s creations and characters. The bot offers various templates for character information, including basic details and more complex options like D&D-style character sheets.

For more information, you send me a direct message on discord or by email at *chriszethird.contact@gmail.com*

You can also join my [discord server](https://discord.gg/TcwjZhE) to stay up to date on the development of the bot and 
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

Using `/ocadd` you will be asked to fill several boxes as shown below:

![image](https://github.com/ChrisZeThird/BotZeFourth/assets/86256324/9d968273-c77a-4556-8b89-88a5f903a289)

Then you will have to choose a colour for your character thanks to a drop down menu:

![image](https://github.com/ChrisZeThird/BotZeFourth/assets/86256324/151563d2-8330-4307-9014-59e8f7735225)

### Checking one or multiple OC(s)

This is the most interesting part for your discorc community as an artist. You can use `/ocinfo` to get information on a specific OC from a specific artist or `ocrandom` to get a random OC from any artist on your server:

![image](https://github.com/ChrisZeThird/BotZeFourth/assets/86256324/df02ce21-f9b3-4dfd-a601-3fe9c26eccb3)

The bot will then send an embed with all the information set by the original artist:

![image](https://github.com/ChrisZeThird/BotZeFourth/assets/86256324/fc9d39f1-edbb-47b6-ba15-fae8ff5c416a)

You can also get the list of OC(s) owned by an artist with `/oclist` or check who has OC(s) on your server using `/artistlist`.

# Acknowledgements

I would like to thank AlexFlipnote for the time he took to help me while I was developing this bot. He also provided a 
very nice quick setup [template](https://github.com/AlexFlipnote/discord_bot.py) to create a discord bot on his own 
GitHub page and even updated his [PostgresLite](https://github.com/AlexFlipnote/PostgresLite) library with async support.
