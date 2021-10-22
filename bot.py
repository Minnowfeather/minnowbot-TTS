# bot.py

import discord
from gtts import gTTS
import os

tokenReader = open("token.txt", "r")
token = tokenReader.read()

prefixReader = open("prefix.txt", "r")
prefix = prefixReader.read()

vc = None
vol = 100
speed = 1.0
user = 0
language = "en"
lang_dict = {
    "english":"en",
    "spanish":"es",
    "brazillian":"pt-BR",
    "japanese":"ja",
    "australian":"en-AU",
    "england":"en-GB",
    "korean":"ko",
    "indian":"en-IN",
    "chinese":"zh"
}

rChan = None

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global vc, vol, prefix, language, speed, user, rChan
    if message.author == client.user:
        return

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
            else:
                user = message.author.id
                await message.channel.send("`Bound to: " + message.author.display_name + " and restricted to: " + message.channel.name + "`")
            rChan = message.channel
            
        elif msg[0] == "unattach" and message.author.id == user:
            user = 0
            if rChan != None:
                rChan = None
        elif msg[0] == "bind" and user == 0:
            user = message.mentions[0].id
            await message.channel.send("`Now bound to: " + message.mentions[0].display_name + "`")
            
        elif msg[0] == "unbind" and message.author.id == user:
            user = 0
            if rChan != None:
                rChan = None
            await message.channel.send("`No longer bound.`")

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

    elif message.author.id == user:
        if rChan == None:
            await connect(message.author.voice.channel)
            await speak(message.content)
        elif message.channel == rChan:
            await connect(message.author.voice.channel)
            await speak(message.content)


async def connect(channel):
    global vc, vol, prefix, language, speed
    
    try:
        vc = await channel.connect()
    except:
        await vc.move_to(channel)
    
    
async def speak(message):
    global vc, vol, prefix, language, speed

    speechObject = gTTS(text=message, lang=language, slow=False)
    speechObject.save("speech.mp3")
  
    vc.play(discord.FFmpegPCMAudio("speech.mp3"))
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

# @client.event
# async def on_voice_state_update(member, before, after):
#     global user, vc
#     if member == client.user:
#         return
#     print(member.id)
#     print(user)
#     if member.id == user and after.channel != None:
#         print("deez")
#         try:
#             vc = await after.channel.connect()
#         except:
#             await vc.move_to(after.channel)


client.run(token)
