# About the project
I started developing this bot a year ago, after talking with my girlfriend about how you could share characters 
description as an artist on discord. This was the opportunity to (re) discover *SQL* database, and *discord.py*. I put 
this project on hold due to exam and lack the enthusiasm to continue (I also lost the project). Now I feel more 
confident tackling this project, especially thanks to *GitHub* and *Pycharm*.

Artists can create information cards about their characters, and users on discord just have to run a command to read the 
card. For now, there are basic functionalities. I'm actively looking for feedbacks!

# Quick set-up
You can find the source code at this [address](https://github.com/ChrisZeThird/BotZeFourth).
You will first have to give the bot roles that can use the database system. I indeed to want anyone to add their own 
creation, as it can quickly get messy. You'll need the `/addrole roleid` command. Then give the bot channel where 
artworks are being posted. This was you can allow artists to post their creation and immediately create a thread to 
enable interactions between the author and viewers without cluttering the main channel (any message without an 
attachment will be deleted). Please note BotZeFourth **is not a moderation bot and won't be supporting moderation 
features**.

I suggest you join my discord server (link in bio) to stay informed on the development on the bot and submit ideas 
(even though you can also use `/suggest`).

# Acknowledgements

I would like to thank AlexFlipnote for the time he took to help me while I was developing this bot. He also provided a 
very nice quick setup [template](https://github.com/AlexFlipnote/discord_bot.py) to create a discord bot on his own 
GitHub page and even updated his [PostgresLite](https://github.com/AlexFlipnote/PostgresLite) library with async support.