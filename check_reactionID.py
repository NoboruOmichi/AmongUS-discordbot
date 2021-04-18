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

#ユーザがリアクションをつけた時、対応する役職を付与（生存、幽霊）
@client.event
async def on_reaction_add(reaction, user):
    channel = client.get_channel(DEBUG_CHANNEL_ID)
    print(reaction.emoji.id)
    await channel.send(str(reaction.emoji.id))

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)