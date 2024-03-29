# bot.py

import discord
from gtts import gTTS
import gtts.lang
import os

import argparse

argParser = argparse.ArgumentParser(prog="minnowbot-tts", description="Discord bot for text-to-speech.")
argParser.add_argument('-t', '--token', nargs=1, help="Sets the token. Will otherwise read from token.txt")
argParser.add_argument('-p', '--prefix', nargs=1, help="Sets the prefix. Will otherwise read from prefix.txt")

args = vars(argParser.parse_args())

token = ""
prefix = ""
if args['token'] is not None:
    token = args['token'][0]
else:
    tokenReader = open("token.txt", "r")
    token = tokenReader.read()
if args['prefix'] is not None:
    prefix = args['prefix'][0]
else:
    prefixReader = open("prefix.txt", "r")
    prefix = prefixReader.read()

vc = None
vol = 100
speed = 1.0
user = 0
language = "en"
lang_dict = dict([(value,key) for key, value in gtts.lang.tts_langs().items()])

rChan = None

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents);

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global vc, vol, prefix, language, speed, user, rChan
    if message.author == client.user:
        return

    # process message
    msg = message.content
    is_command = msg[:len(prefix)] == prefix
    msg = msg[len(prefix):]
    msg = msg.split(' ')
    
    if is_command:
        if msg[0] == "lang" and message.author.id == user:
            l = await set_lang(msg[1])
            if l:
                await message.channel.send("`Language set to: " + language + "`")
            else:
                await message.channel.send("`Not a valid language.`")
        elif msg[0] == "language" and message.author.id == user:
            l = await set_lang(msg[1])
            if l:
                await message.channel.send("`Language set to: " + language + "`")
            else:
                await message.channel.send("`Not a valid language.`")
        elif msg[0] == "volume" or msg[0] == "vol":
            if(len(msg) != 2):
                await message.channel.send("`Volume is: " + str((vol*100)) + "%`")
                return
            vol = clamp(float(msg[1]) / 100, 0, 1)
            vc.source.volume = vol
            
        elif msg[0] == "attach" and user == 0:
            if(len(message.mentions) != 0):
                user = message.mentions[0].id
                await message.channel.send("`Bound to: " + message.mentions[0].display_name + " and restricted to: " + message.channel.name + "`")
                await message.guild.me.edit(nick=message.mentions[0].display_name + "Bot")
            else:
                user = message.author.id
                await message.channel.send("`Bound to: " + message.author.display_name + " and restricted to: " + message.channel.name + "`")
                await message.guild.me.edit(nick=message.author.display_name + "Bot")
            rChan = message.channel
            
        elif (msg[0] == "unattach" or msg[0] == "detatch") and message.author.id == user:
            user = 0
            if rChan != None:
                rChan = None
            await message.guild.me.edit(nick="MinnowBot")
        elif msg[0] == "bind" and user == 0:
            user = message.mentions[0].id
            await message.channel.send("`Now bound to: " + message.mentions[0].display_name + "`")
            await message.guild.me.edit(nick=message.mentions[0].display_name + "Bot")
        elif msg[0] == "unbind" and message.author.id == user:
            user = 0
            if rChan != None:
                rChan = None
            await message.channel.send("`No longer bound.`")
            await message.guild.me.edit(nick="MinnowBot")
        elif msg[0] == "restrict" and message.author.id == user and rChan == None:
            rChan = message.channel
            await message.channel.send("`Restricted to " + message.channel.name + "`")
        
        elif msg[0] == "unrestrict" and message.author.id == user and message.channel == rChan:
            rChan = None
            await message.channel.send("`No longer restricted to " + message.channel.name + "`")
        
        elif msg[0] == "stop":
            vc.stop()
        elif msg[0] == "deaf" and message.author.id == user:
            deafStat = message.author.voice.deaf
            deafStat = not deafStat
            await message.author.edit(mute=deafStat, deafen=deafStat)
        elif msg[0] == "disconnect" or msg[0] == "dc":
            await disconnect(msg.guild.voice_client)
        elif msg[0] == "quit" or msg[0] == "exit":
            await client.close()
        elif msg[0] == "langs":
            tmpLangs = "```"
            for myKey in lang_dict.keys():
                tmpLangs += myKey + "\n"
            tmpLangs += "```"
            await message.channel.send(tmpLangs)
    elif message.author.id == user:
        if rChan == None:
            await connect(message.author.voice.channel)
            await speak(message.content)
        elif message.channel == rChan:
            await connect(message.author.voice.channel)
            await speak(message.content)


async def connect(channel):
    global vc
    try:
        vc = await channel.connect()
    except:
        await vc.move_to(channel)
    
async def disconnect(voiceclient):
    try:
        await voiceclient.disconnect()
        vc = None
    except:
        print("Error disconnecting")



async def speak(message):
    global vc, vol, language, user

    filename = str(user) + ".mp3"
    speechObject = gTTS(text=message, lang=language, slow=False)
    speechObject.save(filename)
  
    vc.play(discord.FFmpegPCMAudio(filename))
    vc.source = discord.PCMVolumeTransformer(vc.source)
    vc.source.volume = vol
    vc.resume()


async def set_lang(lang):
    global language
    
    prev_lang = language
    if lang in lang_dict:
        language = lang_dict[lang]
    else:
        language = lang
    
    try:
        gTTS(text = "a", lang = language, slow=False)
    except:
        language = prev_lang
        return False
    
    return True
    
 
def clamp(num, mi, ma):
    return max(min(num, ma), mi)

client.run(token)
