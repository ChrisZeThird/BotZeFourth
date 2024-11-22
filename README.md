*DISCLAIMER: This README file isn't up to date with the current Bot version. It concerns the `legacy` branch only.*

# About the project
I started developing this bot a year ago, after talking with my girlfriend about how you could share characters 
description as an artist on discord. This was the opportunity to (re) discover *SQL* database, and *discord.py*. I put 
this project on hold due to exam and lack the enthusiasm to continue (I also lost the project). Now I feel more 
confident tackling this project, especially thanks to *GitHub* and *Pycharm*.

Artists can create information cards about their characters, and users on discord just have to run a command to read the 
card. For now, there are basic functionalities. I'm actively looking for feedbacks!

***The bot is currently not in public mode, so only I can add it to a server, if you want to test it out, send me a direct message on discord or by email at chriszethird.contact@gmail.com***

# Quick set-up
Start by inviting the bot to your server using this
[link](https://discord.com/api/oauth2/authorize?client_id=848583084119031808&permissions=397553036369&scope=bot).

You will first have to give the bot roles that can use the database system. Otherwise, you won't be able to use any
command related to OC management. You'll need the `/addrole` command:

![image](https://github.com/ChrisZeThird/BotZeFourth/assets/86256324/ac244c11-726a-464c-a955-556f44200fd8)

Then give the bot channel where 
artworks are being posted using `/addchannel` command:

![image](https://github.com/ChrisZeThird/BotZeFourth/assets/86256324/b0cf44f4-c29e-4d42-9f31-73cef7e3b6a7)

This way, you can allow artists to post their creation and immediately create a thread to 
enable interactions between the author and viewers without cluttering the main channel (any message without an 
attachment will be deleted). This command is not mandatory.

**Please note BotZeFourth is not a moderation bot and won't be supporting moderation 
features**.

I suggest you join my [discord server](https://discord.gg/TcwjZhE) to stay up to date on the development on the bot and 
submit ideas (even though you can also use the `/suggest` command on your server).

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
