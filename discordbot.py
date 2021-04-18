import os
import traceback
import discord
import time
import asyncio
import sys


# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

guild_id_num = XXXXXXXXXXXXXXXXXX   #使用するサーバーのID
startmsg = 'AmongUs用のBOT起動しました\n下のリアクションを用いて生存者・幽霊を自動で振り分けられます'
textch_name = 'メイン部屋'
textch_id_num = XXXXXXXXXXXXXXXXXX  #テキストチャンネルのID

survivor_name = '生存者'
survivor_id_num = XXXXXXXXXXXXXXXXXX   #生存者の役職ID
survivor_emoji_id_num = XXXXXXXXXXXXXXXXXX #生存者の絵文字のID
survivor_emoji_id = "<:amongus:XXXXXXXXXXXXXXXXXX>" #生存者の絵文字
ghost_name = '幽霊'
ghost_id_num = XXXXXXXXXXXXXXXXXX   #幽霊の役職ID
ghost_emoji_id_num = XXXXXXXXXXXXXXXXXX #幽霊の絵文字のID
ghost_emoji_id = "<:amongus:XXXXXXXXXXXXXXXXXX>"    #幽霊の絵文字
meetingch_name = 'ミーティング'
meeting_id_num = XXXXXXXXXXXXXXXXXX #ミーティング部屋のID
alive_name = '生存部屋'
alive_id_num = XXXXXXXXXXXXXXXXXX   #探索者部屋のID
haunted_name = '幽霊部屋'
haunted_id_num = XXXXXXXXXXXXXXXXXX #幽霊部屋のID

survival_emoji_id_num = XXXXXXXXXXXXXXXXXX ##探索の絵文字のID
survival_emoji_id = "<:survival:XXXXXXXXXXXXXXXXXX>"    #探索の絵文字
emergency_emoji_id_num = XXXXXXXXXXXXXXXXXX #エマージェンシーの絵文字のID
emergency_emoji_id = "<:emergency:XXXXXXXXXXXXXXXXXX>"    #エマージェンシーの絵文字

startbutton_emoji_id = "<:startbutton:XXXXXXXXXXXXXXXXXX>"  #スタートボタンの絵文字のid
startbutton_emoji_id_num = XXXXXXXXXXXXXXXXXX   #スタートボタンの絵文字

no_reaction_member_list = []    #リアクションをしていないor2つともついている人検出

all_emoji = [survivor_emoji_id, ghost_emoji_id,survival_emoji_id,emergency_emoji_id] #botが自分のメッセージにするリアクション一覧
setup_emoji_list = [survivor_emoji_id, startbutton_emoji_id] #ゲームセットアップ時のbotのリアクション
gamestart_emoji_add_list = [ghost_emoji_id, emergency_emoji_id] #ゲームセットアップ時のbotのリアクション

GAME_STATE = "game_setup" #["game_setup", "game_ready", "survival", "emergency", "game_end"]

Warning_message = []

@client.event
async def on_ready():
    guild = client.get_guild(guild_id_num) #サーバのID

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    # await game_setup()
    global GAME_STATE
    GAME_STATE = "game_setup"


#ゲームセットアップ
@client.event
async def game_setup():
    guild = client.get_guild(guild_id_num) #サーバのID
    mch  = guild.get_channel(meeting_id_num) #ミーティングチャンネルのID
    global GAME_STATE
    Main_Text_Channel  = guild.get_channel(textch_id_num) #テキスト（メイン）チャンネルのID
    message = []
    Warning_message = []

    async for x in Main_Text_Channel.history(limit = 99):
        message.append(x)
        # print(x)
    await Main_Text_Channel.delete_messages(message)

    bot_message = await guild.get_channel(textch_id_num).send(startmsg)
    for reaction_emoji in setup_emoji_list :
        await bot_message.add_reaction(reaction_emoji)

    for voice_channel in guild.voice_channels:
        if voice_channel.name == meetingch_name or voice_channel.name == haunted_name or voice_channel.name == alive_name:
            for member in voice_channel.members:
                await member.edit(mute=False)
                await member.edit(deafen=False)
                await member.move_to(mch) #サーバのID)


    for member in mch.members:
        for member_role in member.roles:
            if member_role.id == survivor_id_num or member_role.id == ghost_id_num:
                await member.remove_roles(member_role)

    GAME_STATE = "game_ready"



@client.event
async def game_ready(message):
    guild = client.get_guild(guild_id_num) #サーバのID
    text_channel = guild.get_channel(textch_id_num)

    delmsg =  [x async for x in text_channel.history(limit = 99) if x != message]
    await text_channel.delete_messages(delmsg)


##役職がついていない人検出
    no_reaction_member_list = []
    for voice_channel in guild.voice_channels:
        for member in voice_channel.members :
            print(member.roles)
            if (ghost_name  in str(member.roles) and survivor_name in str(member.roles)) \
                    or (not(ghost_name  in str(member.roles)) and not(survivor_name in str(member.roles))) :
                no_reaction_member_list.append(member.name)

    if len(no_reaction_member_list) == 0:
        await message.clear_reaction(startbutton_emoji_id)
        for reaction_emoji in gamestart_emoji_add_list :
            await message.add_reaction(reaction_emoji)
        global GAME_STATE
        GAME_STATE = "survival"
        await survival()
    else :
        print(str(no_reaction_member_list))
        await text_channel.send('次の人がリアクションをつけていない、もしくは役職付与が適切にできていないためゲームを開始できません。')
        await text_channel.send(str(no_reaction_member_list))


#サーバの役職による移動と各々のミュート設定
async def survival():
    guild = client.get_guild(guild_id_num) #サーバのID
    sch  = guild.get_channel(alive_id_num) #生存チャンネルのID
    ych  = guild.get_channel(haunted_id_num) #幽霊チャンネルのID
    for voice_channel in guild.voice_channels:
        if voice_channel.name == meetingch_name:
            for member in voice_channel.members:
                if survivor_name in str(member.roles):
                    print(str(member.name)+'　を生存者に移動')
                    await member.edit(mute=True)
                    await member.edit(deafen=True)
                    await member.move_to(sch)
                elif ghost_name  in str(member.roles):
                    print(str(member.name) + '　を幽霊に移動')
                    await member.edit(mute=False)
                    await member.edit(deafen=False)
                    await member.move_to(ych)
    print('----------------------------------------survival')

async def emergency():
    guild = client.get_guild(guild_id_num) #サーバのID
    mch  = guild.get_channel(meeting_id_num) #ミーティングチャンネルのID
    Warning_message = []

    for voice_channel in guild.voice_channels:
        if voice_channel.name == haunted_name or voice_channel.name == alive_name:
            for member in voice_channel.members:
                if survivor_name in str(member.roles):
                    await member.edit(mute=False)
                    await member.edit(deafen=False)
                    await member.move_to(mch)
                elif ghost_name  in str(member.roles):
                    await member.edit(mute=True)
                    await member.edit(deafen=False)
                    await member.move_to(mch)
    print('----------------------------------------meeting')



@client.event
async def botend():
    guild = client.get_guild(guild_id_num) #サーバのID
    Main_Text_Channel  = guild.get_channel(textch_id_num) #テキスト（メイン）チャンネルのID
    mch  = guild.get_channel(meeting_id_num) #ミーティングチャンネルのID

    message = []
    
    async for x in Main_Text_Channel.history(limit = 99):
        message.append(x)
        # print(x)
    await Main_Text_Channel.delete_messages(message)

    for voice_channel in guild.voice_channels:
        if voice_channel.name == meetingch_name or voice_channel.name == haunted_name or voice_channel.name == alive_name:
            for member in voice_channel.members:
                await member.edit(deafen=False)
                await member.edit(mute=False)
                await member.move_to(mch) #サーバのID)


    for member in mch.members:
        for member_role in member.roles:
            if member_role.id == survivor_id_num or member_role.id == ghost_id_num:
                await member.remove_roles(member_role)



@client.event
async def on_message(message):
    global GAME_STATE
    guild = client.get_guild(guild_id_num) #サーバのID

    if message.content.startswith('.end'):#!SHUTDOWN_BOTが入力されたら強制終了
        GAME_STATE = "game_end"
        await botend()
    elif message.content.startswith('.start'):
        GAME_STATE = "game_setup"
        await game_setup()


#ユーザがリアクションをつけた時、対応する役職を付与（生存、幽霊）
@client.event
async def on_reaction_add(reaction, user):
    print(reaction.emoji.id)
    global GAME_STATE
    guild = client.get_guild(guild_id_num) #サーバのID
    #botの正しいメッセージにリアクションをしたか＆ボットがしたリアクションではないか
    if reaction.message.content == startmsg and (not user.bot):
        checked_emoji = reaction.emoji.id   #つけたリアクションのチェック
        if checked_emoji == survivor_emoji_id_num or checked_emoji == ghost_emoji_id_num:
            if GAME_STATE == "survival" :
                if (survivor_name in str(user.roles) and checked_emoji == ghost_emoji_id_num) \
                        or (ghost_name in str(user.roles) and checked_emoji == survivor_emoji_id_num):
                    Warning_message.append(await guild.get_channel(textch_id_num).send('サバイバル状態はロールの変更はできません。間違えて押した方はすぐにリアクションを戻してください'))
                else :
                    await Warning_message.pop(0).delete()
            elif checked_emoji == survivor_emoji_id_num:
                await reaction.message.remove_reaction(ghost_emoji_id, user)
                role = guild.get_role(survivor_id_num)
                member = guild.get_member(user.id)
                await member.add_roles(role)
                if GAME_STATE == "emergency":
                    await member.edit(mute=False)
                    await member.edit(deafen=False)
            elif checked_emoji == ghost_emoji_id_num :
                await reaction.message.remove_reaction(survivor_emoji_id, user)
                role = guild.get_role(ghost_id_num)
                member = guild.get_member(user.id)
                await member.add_roles(role)
                if GAME_STATE == "emergency":
                    await member.edit(mute=True)
                    await member.edit(deafen=False)
        elif checked_emoji == survival_emoji_id_num :
            await reaction.message.clear_reaction(survival_emoji_id)
            await reaction.message.add_reaction(emergency_emoji_id)
            GAME_STATE = "survival"
            await survival()
        elif checked_emoji == emergency_emoji_id_num :
            if len(Warning_message) == 0:
                await reaction.message.clear_reaction(emergency_emoji_id)
                await reaction.message.add_reaction(survival_emoji_id)
                GAME_STATE = "emergency"
                await emergency()
            else :
                await reaction.message.remove_reaction(emergency_emoji_id_num, user)
        elif checked_emoji == startbutton_emoji_id_num :
            await game_ready(reaction.message)
            await reaction.message.remove_reaction(startbutton_emoji_id, user)



#ユーザがリアクションを消した時、役職を外す（生存、幽霊）
@client.event
async def on_reaction_remove(reaction, user):
    global GAME_STATE
    guild = client.get_guild(guild_id_num) #サーバのID
    #botの正しいメッセージのリアクションを消したか＆ボットがしたリアクションではないか
    if reaction.message.content == startmsg and (not user.bot):
        checked_emoji = reaction.emoji.id   #外したリアクションのチェック
        if checked_emoji == survivor_emoji_id_num or checked_emoji == ghost_emoji_id_num:
            if GAME_STATE == "survival" :
                if (survivor_name in str(user.roles) and checked_emoji == survivor_emoji_id_num) \
                        or (ghost_name in str(user.roles) and checked_emoji == ghost_emoji_id_num):
                    Warning_message.append(await guild.get_channel(textch_id_num).send('サバイバル状態はロールの変更はできません。間違えて押した方はすぐにリアクションを戻してください'))
                else :
                    await Warning_message.pop(0).delete()
            elif checked_emoji == survivor_emoji_id_num:
                role = guild.get_role(survivor_id_num)
                member = guild.get_member(user.id)
                await member.remove_roles(role)
            elif checked_emoji == ghost_emoji_id_num :
                role = guild.get_role(ghost_id_num)
                member = guild.get_member(user.id)
                await member.remove_roles(role)

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)