# About the project
I started developing this bot a year ago, after talking with my girlfriend about how you could share characters 
description as an artist on discord. This was the opportunity to (re) discover *SQL* database, and *discord.py*. I put 
this project on hold due to exam and lack the enthusiasm to continue (I also lost the project). Now I feel more 
confident tackling this project, especially thanks to *GitHub* and *Pycharm*.

Artists can create information cards about their characters, and users on discord just have to run a command to read the 
card. For now, there are basic functionalities. I'm actively looking for feedbacks!

# Quick set-up
Start by inviting the bot to your server using this 
[link](https://discord.com/api/oauth2/authorize?client_id=848583084119031808&permissions=397553036369&scope=bot).

You will first have to give the bot roles that can use the database system. Otherwise, you won't be able to use any
command related to OC management. You'll need the `/addrole roleid` command:
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

Here is the full list of commands available so far. Please note the `help` command stil uses the prefix `>`:

```yaml
Admin:
  addchannel        
  addrole           Add roles allowed to use the bot
  createdatabase    Create a database for your server. You can either make it...
  removerole        Remove roles allowed to use the bot
DiscordInfo:
  avatar            Get the avatar of you or someone else 
  joindate          Check when a user joined the current server 
  roles             Get all roles in current server 
Information:
  botserver         Get an invitation to our support server! 
  ping              Pong! 
OCmanager:
  addoc             Add OC to the database with respect to user and guild id 
  deleteoc          Delete an oc from the database 
  listartist        List all artists of a server 
  listoc            List all oc of an artist 
  modifyoc          Modify OC in the database with respect to user and guild id 
  ocinfo            Gives the information sheet of an OC 
  randomoc          Send the description of a random selected OC 
Suggestion:
  suggest           Make a suggestion to the developer 
  suggestionranking Check ranking of suggestion 
  suggestionvote    Vote for a suggestion 
​No Category:
  help              Shows this message
```

# Acknowledgements

I would like to thank AlexFlipnote for the time he took to help me while I was developing this bot. He also provided a 
very nice quick setup [template](https://github.com/AlexFlipnote/discord_bot.py) to create a discord bot on his own 
GitHub page and even updated his [PostgresLite](https://github.com/AlexFlipnote/PostgresLite) library with async support.
