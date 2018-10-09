import discord
import asyncio
import requests
import logging
import time
from datetime import datetime, date
import string
import random
import copy
import apiai, json
import asyncpg
import copy
import dbl
from discord.ext import commands
from config.settings import *
from cogs.const import *
from cogs.locale import *

logger = logging.getLogger('tomori-music')
logger.setLevel(logging.DEBUG)
now = datetime.now()
logname = 'logs/music/{}_{}.log'.format(now.day, now.month)
try:
    f = open(logname, 'r')
except:
    f = open(logname, 'w')
    f.close()
finally:
    handler = logging.FileHandler(
        filename=logname,
        encoding='utf-8',
        mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

loop = asyncio.get_event_loop()

global conn
conn = None
global bot
bot = None
global dblpy
dblpy = None
async def get_prefixes():
    global bot
    # con = await asyncpg.connect(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"])
    # dat = await con.fetch("SELECT prefix FROM settings")
    # prefixes = []
    # if not dat:
    #     prefixes = ["!"]
    # else:
    #     for s in dat:
    #         ss = str(s)[16:17]
    #         if not ss in prefixes:
    #             prefixes.append(ss)
    # await con.close()
    #
    # print(prefixes)
    bot = commands.Bot(command_prefix="!", shard_count=10)
    #bot = commands.Bot(command_prefix=prefix_list, shard_count=10)
    bot.remove_command('help')
    bot.load_extension('cogs.music')

async def run_base():
    global conn
    try:
        conn = await asyncpg.create_pool(dsn="postgres://{user}:{password}@{host}:5432/{database}".format(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"]), command_timeout=60)
        global top_guilds
        top_guilds = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
        logger.info('PostgreSQL was successfully loaded.')
    except:
        logger.error('PostgreSQL doesn\'t load.')
        exit(0)
    #await init_locale(conn, bot)


loop.run_until_complete(get_prefixes())
loop.run_until_complete(run_base())

@bot.event
async def on_command_error(error, ctx):
    pass




global voice_clients
voice_clients = []

@bot.event
async def on_voice_state_update(member, before, after):
    ret = '---------[voice_state_update]:{0.guild.name} | {0.guild.id}\n'.format(member)
    if before.channel:
        ret += '\tbefore - {0.name} | {0.id} -> {1.channel.name} | {1.channel.id}\n'.format(member, before)
    if after.channel:
        ret += '\tafter - {0.name} | {0.id} -> {1.channel.name} | {1.channel.id}\n'.format(member, after)
    logger.info(ret[:-1])
    # if member.bot:
    #     return
    const = await conn.fetchrow("SELECT create_lobby_id, em_color FROM settings WHERE discord_id = '{}'".format(member.guild.id))
    if not const:
        logger.error('Сервер {0.name} | {0.id} отсутствует в базе! User - {1.name} | {1.id}'.format(member.guild, member))
        return
    if not const["create_lobby_id"]:
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    global voice_clients
    if before.channel and before.channel != after.channel:
        if member.id in voice_clients:
            voice_clients.pop(voice_clients.index(member.id))
        dat = await conn.fetchrow("SELECT voice_channel_id FROM users WHERE discord_id = '{0.id}'".format(member))
        if dat:
            if before.channel.id == dat[0]:
                await conn.execute("UPDATE users SET voice_channel_id = Null WHERE discord_id = '{0.id}'".format(member))
                try:
                    await bot.delete_channel(member.voice.channel)
                except:
                    logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал пользователя. User - {1.name} | {1.id}'.format(member.guild, member))
                    em.description = '{}, не удалось удалить канал пользователя. Свяжитесь с администратором сервера.'.format(clear_name(member.display_name[:50]))
                    await bot.send(embed=em)
    if after.channel and after.channel.id == const["create_lobby_id"]:
        logger.info("const = {const}\n".format(const=const))
        if member.id in voice_clients:
            return
        voice_clients.append(member.id)
        try:
            #for_everyone = discord.ChannelPermissions(target=after.guild.default_role, overwrite=discord.PermissionOverwrite(read_messages=True))
            #for_after = discord.ChannelPermissions(target=after, overwrite=discord.PermissionOverwrite(create_instant_invite=True, manage_roles=False, read_messages=True, manage_channels=True, connect=True, speak=True, mute_members=False, deafen_members=False, use_voice_activation=True, move_members=False))
            private = await member.guild.create_voice_channel("test channel")#, for_everyone, for_after, type=discord.ChannelType.voice)
            #await bot.edit_channel(private, user_limit=2)
            #await bot.move_channel(private,  0)
            dat = await conn.fetchrow("SELECT name FROM users WHERE  discord_id = '{0.id}'".format(member))
            if dat:
                await conn.execute("UPDATE users SET voice_channel_id = '{0}' WHERE discord_id = '{1.id}'".format(private.id, member))
            else:
                await conn.execute("INSERT INTO users(name, discord_id, discriminator, voice_channel_id, background) VALUES('{}', '{}', '{}', '{}')".format(member.name, member.id, before.discriminator, private.id, random.choice(background_list)))
        except:
            logger.error('Сервер {0.name} | {0.id}. Не удалось создать канал. User - {1.name} | {1.id}'.format(member.guild, member))
            em.description = '{}, не удалось создать канал. Свяжитесь с администратором сервера.'.format(clear_name(member.display_name[:50]))
            await bot.send(embed=em)
            return
        try:
            await member.move_to(private)
        except:
            try:
                await bot.delete_channel(private)
            except:
                logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал {1.name} | {1.id}. User - {2.name} | {1.id}'.format(member.guild, private, member))
            logger.error('Сервер {0.name} | {0.id}. Не удалось переместить пользователя. User - {1.name} | {1.id}'.format(member.guild, member))
            em.description = '{}, не удалось переместить Вас в Ваш канал. Свяжитесь с администратором сервера.'.format(clear_name(member.display_name[:50]))
            await bot.send(embed=em)
            return






@bot.event
async def on_ready():
    logger.info("Logged in as | who - {} | id - {}\n".format(bot.user.display_name, bot.user.id))

@bot.command()
@commands.has_permissions(manage_guild=True)
async def reload(ctx):
    ctx.bot.unload_extension('cogs.music')
    ctx.bot.load_extension('cogs.music')
    await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

bot.run("NDkwOTkxMDIzMjc1NjM4Nzg0.Dp4ObA.Q3q1EVTuBHf_If4ul5jmbl5ECrg") #Tomori Music Token
