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
from discord.ext import commands
from discord.ext.commands import Bot
from config.settings import settings
from cogs.const import *
from cogs.economy import *
from cogs.fun import *
from cogs.admin import *
from cogs.other import *
from cogs.util import *
from cogs.locale import *
from cogs.api import *
from cogs.ids import *


__name__ = "Konoha"
__version__ = "3.25.0"


logger = logging.getLogger('konoha')
logger.setLevel(logging.DEBUG)
now = datetime.now()
logname = 'logs/konoha-{}_{}.log'.format(now.day, now.month)
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

loggers = logging.getLogger('konoha-inform')
loggers.setLevel(logging.DEBUG)
now = datetime.now()
logname = 'logs/konoha-inform->{}_{}.log'.format(now.day, now.month)
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
    '%(message)s'))
loggers.addHandler(handler)


loop = asyncio.get_event_loop()

global conn
conn = None
global client
client = None
global dblpy
dblpy = None
async def get_prefixes():
    global client
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
    client = Bot(command_prefix=prefix_list, shard_count=10)
    client.remove_command('help')

async def run_base():
    global conn
    try:
        conn = await asyncpg.create_pool(dsn="postgres://{user}:{password}@{host}:5432/{database}".format(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"]), command_timeout=60)
        global top_servers
        top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
    except:
        logger.error('PostgreSQL doesn\'t load.\n')
        exit(0)
    await init_locale(conn, client)


loop.run_until_complete(get_prefixes())
loop.run_until_complete(run_base())



def is_it_admin():
    def predicate(ctx):
        if ctx.message.author == ctx.message.server.owner:
            return True
        return any(role.permissions.administrator for role in ctx.message.author.roles)
    return commands.check(predicate)

def is_it_owner():
    def predicate(ctx):
        return True if ctx.message.author == ctx.message.server.owner else False
    return commands.check(predicate)

def is_it_admin_or_dev():
    def predicate(ctx):
        if ctx.message.author.id in admin_list:
            return True
        if ctx.message.author == ctx.message.server.owner:
            return True
        return any(role.permissions.administrator for role in ctx.message.author.roles)
    return commands.check(predicate)

def is_it_me():
    def predicate(ctx):
        return ctx.message.author.id in admin_list
    return commands.check(predicate)

def is_it_support():
    def predicate(ctx):
        if ctx.message.author.id in admin_list:
            return True
        return ctx.message.author.id in support_list
    return commands.check(predicate)

def is_it_local_server():
    def predicate(ctx):
        return True if ctx.message.server.id in local_stats_servers else False
    return commands.check(predicate)




WORK_COOLDOWN = 1800
WORK_DELAY = 60

async def working():
    await client.wait_until_ready()
    while not client.is_closed:
        now = int(time.time())
        begin_time = datetime.now()
        workCooldownNow = now - WORK_COOLDOWN
        servers = await conn.fetch("SELECT discord_id, work_count FROM settings WHERE is_work = True")

        if not servers:
            await asyncio.sleep(WORK_DELAY)
            continue

        for discordId, workCount in servers:
            await conn.execute("UPDATE users SET work_time = 0, cash = cash + {workCount} WHERE work_time > 0 AND work_time <= {workCooldown}".format(
                workCount=workCount,
                workCooldown=workCooldownNow
            ))

        logger.info("working time = {}ms\n".format(int((datetime.utcnow() - begin_time).microseconds / 1000)))
        await asyncio.sleep(WORK_DELAY)


async def statuses():
    await client.wait_until_ready()
    while not client.is_closed:
        await client.change_presence(game=discord.Game(type=3, name="на Коноху | !help"))
        await asyncio.sleep(20)

        users_count = client.get_server("502913055559254036").member_count
        await client.change_presence(game=discord.Game(type=3, name="на {users_count} шиноби | !help".format(users_count=users_count)))
        await asyncio.sleep(20)

        # for status in piar_statuses:
        #     await client.change_presence(game=discord.Game(type=1, name=status))
        #     await asyncio.sleep(10)



@client.event
async def on_socket_raw_receive(raw_msg):
    if not isinstance(raw_msg, str):
        return
    msg = json.loads(raw_msg)
    type = msg.get("t")
    data = msg.get("d")
    if not data:
        return
    if type == "MESSAGE_REACTION_ADD":
        await u_reaction_add(client, conn, logger, data)
    if type == "MESSAGE_REACTION_REMOVE":
        await u_reaction_remove(client, conn, logger, data)








@client.event
async def on_member_join(member):
    logger.info("{0.name} | {0.id} joined at server - {1.name} | {1.id}\n".format(member, member.server))
    dat = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{id}'".format(id=member.server.id))

    await u_check_travelling(client, member)

    if member.server.id in welcome_responses_dm.keys():
        text, em = await dict_to_embed(welcome_responses_dm.get(member.server.id))
        try:
            await client.send_message(member, content=text, embed=em)
        except:
            pass

    if dat:
        role = discord.utils.get(member.server.roles, id=dat["autorole_id"])
        if role:
            await client.add_roles(member, role)

        welcome_channel = client.get_channel(dat["welcome_channel_id"])
        if welcome_channel:
            await send_welcome_pic(client, welcome_channel, member, dat)


@client.event
async def on_member_remove(member):
    logger.info("{0.name} | {0.id} removed from server - {1.name} | {1.id}\n".format(member, member.server))
    await client.send_message(client.get_channel('486591862157606913'), "*{2}*\n``({0.name} | {0.mention}) <== [{1.name} | {1.id}] ({delta} дней)``".format(member, member.server, time.ctime(time.time()), delta=(datetime.utcnow() - member.created_at).days))
    dat = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{}'".format(member.server.id))
    if dat:
        welcome_channel = discord.utils.get(member.server.channels, id=dat["welcome_channel_id"])
        if welcome_channel and dat["welcome_leave_text"]:
            message = welcomer_format(dat["welcome_leave_text"], member)
            await client.send_message(welcome_channel, message)








@client.event
async def on_ready():
    dat = await conn.fetch("SELECT name, discord_id FROM settings")
    for server in client.servers:
        if server.id in not_monitoring_servers:
            continue
        if not any(server.id == value["discord_id"] for value in dat):
            try:
                await conn.execute("INSERT INTO settings(name, discord_id) VALUES('{}', '{}')".format(clear_name(server.name[:50]), server.id))
            except:
                pass
        else:
            await conn.execute("UPDATE settings SET name = '{}' WHERE discord_id = '{}'".format(clear_name(server.name[:50]), server.id))
    client.loop.create_task(working())
    print('Logged in as')
    logger.info("Logged in as | who - {} | id - {}\n".format(clear_name(client.user.display_name), client.user.id))
    print(clear_name(client.user.display_name))
    print(client.user.id)
    print('------')
    client.loop.create_task(statuses())

@client.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        msg = await client.send_message(ctx.message.channel, "{who}, Чакра закончилась, восстановление через {seconds} секунд".format(who=ctx.message.author.mention, seconds=int(error.retry_after)))
        try:
            await client.delete_message(ctx.message)
        except:
            pass
        await asyncio.sleep(5)
        try:
            await client.delete_message(msg)
        except:
            pass
    pass








@client.command(pass_context=True, name="timely", help="Cобрать печенюхи.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def timely(context):
    await e_timely(client, conn, context)

@client.command(pass_context=True, name="work", help="Выйти на работу.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def work(context):
    await e_work(client, conn, context)

@client.command(pass_context=True, name="help", aliases=['h'], hidden=True, help="Показать список команд.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def helps(context):
    await o_help(client, conn, context)

@client.command(pass_context=True, name="webhook", aliases=["wh"])
@commands.cooldown(1, 1, commands.BucketType.user)
async def webhook(context, name: str=None, *, value: str=None):
    await o_webhook(client, conn, context, name, value)

@client.command(pass_context=True, name="region")
@is_it_me()
@commands.cooldown(1, 1, commands.BucketType.user)
async def region(context):
    await client.send_message(context.message.channel, context.message.server.region)

@client.command(pass_context=True, name="buy", hidden=True, help="Купить роль.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def buy(context, *, value: str):
    await e_buy(client, conn, context, value)

@client.command(pass_context=True, name="shop", help="Показать магазин ролей.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def shop(context, page: int=None):
    await e_shop(client, conn, context, page)

@client.command(pass_context=True, name="lvlup", help="Показать список ролей за уровень.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def lvlup(context, page: int=None):
    await o_lvlup(client, conn, context, page)

@client.command(pass_context=True, name="pay", help="Получить печенюхи из банка сервера.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin()
async def pay(context, count: str):
    await e_pay(client, conn, context, count)

@client.command(pass_context=True, name="send", help="Переслать файл от имени бота.")
@commands.cooldown(1, 15, commands.BucketType.user)
@is_it_admin()
async def _send(context, url: str):
    await a_send(client, conn, context, url)

@client.command(pass_context=True, name="say", hidden=True, help="Напишет ваш текст.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin()
async def say(context, *, value: str):
    await a_say(client, conn, context, value)

@client.command(pass_context=True, name="find_user", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_support()
async def find_user(context, member_id: str):
    if not member_id:
        return
    await a_find_user(client, conn, context, member_id)

@client.command(pass_context=True, name="find_voice", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_support()
async def find_voice(context, member_id: str):
    await a_find_voice(client, conn, context, member_id)

@client.command(pass_context=True, name="base", hidden=True, help="Запрос в базу.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def base(context, mes: str=None):
    await a_base(client, conn, context)

@client.command(pass_context=True, name="add", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def add(context, who: discord.Member, role_id: str):
    message = context.message
    await client.delete_message(message)
    await client.add_roles(who, discord.utils.get(message.server.roles, id=role_id))

@client.command(pass_context=True, name="del", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def dele(context, who: discord.Member, role_id: str):
    message = context.message
    await client.delete_message(message)
    await client.remove_role(who, discord.utils.get(message.server.roles, id=role_id))

@client.command(pass_context=True, name="invite_server", hidden=True, help="Создать инвайт на данный сервер.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def invite_server(context, server_id: str=None):
    await u_invite_server(client, conn, context, server_id)

@client.command(pass_context=True, name="leave_server", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def leave_server(context, server_id: str):
    server = client.get_server(server_id)
    if server:
        await client.leave_server(server)


@client.command(pass_context=True, name="invite_channel", hidden=True, help="Создать инвайт на данный канал.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def invite_channel(context, channel_id: str=None):
    await u_invite_channel(client, conn, context, channel_id)

@client.command(pass_context=True, name="give", help="Передать свои печенюхи.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def give(context, who: discord.Member, count: str):
    await e_give(client, conn, context, who, count)

@client.command(pass_context=True, name="gift")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_local_server()
@is_it_owner()
async def gift(context, count: int):
    await e_gift(client, conn, context, count)

@client.command(pass_context=True, name="top", help="Показать топ юзеров.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def top(context, page: int=None):
    await f_top(client, conn, context, page)

@client.command(pass_context=True, name="set", help="Настройка.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def set(context, arg1: str=None, arg2: str=None, *, args: str=None):
    await o_set(client, conn, context, arg1, arg2, args)

@client.command(pass_context=True, name="remove", aliases=["rm"], help="Настройка.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def remove(context, arg1: str=None, arg2: str=None, *, args: str=None):
    await o_remove(client, conn, context, arg1, arg2, args)

@client.command(pass_context=True, name="backgrounds", aliases=["backs"], help="Показать список фонов.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def backgrounds(context, pages: int=None):
    await o_backgrounds(client, conn, context)

@client.command(pass_context=True, name="$", help="Посмотреть свой баланс.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def cash(context):
    await e_cash(client, conn, context)

@client.command(pass_context=True, name="hug", help="Обнять.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def hug(context, who: discord.Member):
    await f_hug(client, conn, context, who)

@client.command(pass_context=True, name="wink", help="Подмигнуть.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def wink(context, who: discord.Member):
    await f_wink(client, conn, context, who)

@client.command(pass_context=True, name="five", help="Дать пять.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def five(context, who: discord.Member):
    await f_five(client, conn, context, who)

@client.command(pass_context=True, name="fuck", help="Показать фак.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def fuck(context, who: discord.Member):
    await f_fuck(client, conn, context, who)

@client.command(pass_context=True, name="punch", help="Дать леща.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def punch(context, who: discord.Member):
    await f_punch(client, conn, context, who)

@client.command(pass_context=True, name="kiss", help="Поцеловать.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def kiss(context, who: discord.Member):
    await f_kiss(client, conn, context, who)

@client.command(pass_context=True, name="drink", help="Уйти в запой.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def drink(context):
    await f_drink(client, conn, context)

@client.command(pass_context=True, name="shiki", help="Найти аниме на Shikimori.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def shiki(context, *, name: str):
    await api_shiki(client, conn, logger, context, name)

# @client.command(pass_context=True, name="google", help="Найти что-то в гугле.")
# @commands.cooldown(1, 1, commands.BucketType.user)
# async def google_search(context, *, name: str):
#     await api_google_search(client, conn, logger, context, name)

@client.command(pass_context=True, name="createclan", help="Создать клан.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def createclan(context, *, name: str):
    await c_createclan(client, conn, context, name)

@client.command(pass_context=True, name="br", aliases=["roll"], help="Поставить деньги на рулетке.")
@commands.cooldown(1, 2, commands.BucketType.user)
async def br(context, count: str):
    await e_br(client, conn, context, count)

@client.command(pass_context=True, name="slots", aliases=["slot"], help="Поставить деньги на рулетке.")
@commands.cooldown(1, 2, commands.BucketType.user)
async def slots(context, count: str):
    await e_slots(client, conn, context, count)

@client.command(pass_context=True, name="rep", help="Выразить свое почтение.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def rep(context, who: discord.Member):
    await f_rep(client, conn, context, who)

@client.command(pass_context=True, name="setall")
@is_it_me()
async def setall(context, role_id: str):
    message = context.message
    role = discord.utils.get(message.server.roles, id=role_id)
    if not role:
        return
    for member in message.server.members:
        if not role in member.roles:
            await client.add_roles(member, role)


@client.command(pass_context=True, name="avatar", help="Показать аватар пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def avatar(context, who: discord.Member=None):
    await o_avatar(client, conn, context, who)

@client.command(pass_context=True, name="me", aliases=["profile"], help="Вывести статистику пользователя картинкой.")
@commands.cooldown(1, 15, commands.BucketType.user)
async def me(context, who: discord.Member=None):
    await f_me(client, conn, context, who)

@client.command(pass_context=True, name="kick", help="Кикнуть пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def kick(context, who: discord.Member, reason: str=None):
    await a_kick(client, conn, context, who, reason)

@client.command(pass_context=True, name="ban", help="Забанить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def ban(context, who: discord.Member, reason: str=None):
    await a_ban(client, conn, context, who, reason)

@client.command(pass_context=True, name="unban", help="Разбанить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def unban(context, whos: str, reason: str=None):
    await a_unban(client, conn, context, whos, reason)

@client.command(pass_context=True, name="start", help="Test.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin_or_dev()
async def start(context, channel_id: str, *, name: str=None):
    if not channel_id:
        return
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    request_channel = client.get_channel(channel_id)
    if not request_channel:
        for server in client.servers:
            request_channel = server.get_member(channel_id)
            if request_channel:
                break
    if request_channel:
        if not message.author.id in admin_list and not request_channel in message.server.channels:
            em.description = "Соединение с каналом {name} не может быть установлено. Выберите любой канал на этом сервере".format(name=request_channel.name)
            await client.send_message(message.channel, embed=em)
            return
        if message.channel.is_private:
            chan_id = message.author.id
        else:
            chan_id = message.channel.id
        if not name:
            name="NULL"
        else:

            name = "'" + clear_name(name[:20]) + "'"
        dat = await conn.fetchrow("SELECT * FROM tickets WHERE request_id = '{request_id}'".format(request_id=request_channel.id))
        if not dat:
            await conn.execute("INSERT INTO tickets(request_id, response_id, name) VALUES('{request_id}', '{response_id}', {name})".format(request_id=request_channel.id, response_id=chan_id, name=name))
        else:
            await conn.execute("UPDATE tickets SET response_id = '{response_id}', name = {name} WHERE request_id = '{request_id}'".format(request_id=request_channel.id, response_id=chan_id, name=name))
        em.description = "Соединение с каналом {name} установлено".format(name=request_channel.name)
    else:
        em.description = "Соединение с каналом ID:{id} не было установлено. Проверьте ID канала".format(id=channel_id)
    await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="stop", help="Test.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin_or_dev()
async def stop(context):
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    if message.channel.is_private:
        chan_id = message.author.id
    else:
        chan_id = message.channel.id
    dat = await conn.fetchrow("SELECT * FROM tickets WHERE response_id = '{response_id}'".format(response_id=chan_id))
    if dat:
        em.description = "Соединение с каналом закрыто"
        try:
            await client.send_message(u_get_channel(client, dat["request_id"]), embed=em)
        except:
            pass
        await conn.execute("DELETE FROM tickets WHERE response_id = '{response_id}'".format(response_id=chan_id))
    else:
        em.description = "Нет активных соединений"
    try:
        await client.send_message(message.channel, embed=em)
    except:
        pass

@client.command(pass_context=True, name="clear", aliases=["cl"], hidden=True, help="Удалить последние сообщения.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def clear(context, count: int=1, who: discord.Member=None):
    await a_clear(client, conn, context, count, who)


@client.event
async def on_message(message):
    if not message.channel.is_private and message.server.id in not_log_servers:
        return
    await u_check_support(client, conn, logger, message)

    if "᠌" in message.content:
        await client.delete_message(message)

    if not message.channel.is_private:
        logger.info("server - {} | server_id - {} | channel - {} | name - {} | mention - {} | message_id - {}\ncontent - {}\n".format(message.server.name, message.server.id, message.channel.name, message.author.name,message.author.mention, message.id, message.content))
    else:
        logger.info("private_message | name - {} | mention - {} | message_id - {}\ncontent - {}\n".format(message.author.name,message.author.mention, message.id, message.content))
        await client.process_commands(message)
        return

    server_id = message.server.id
    serv = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = \'{}\'".format(server_id))
    if message.author.bot or not serv or not serv["is_enable"]:
        return

    client.loop.create_task(check_words(client, message))

    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"

    dat = await conn.fetchrow("SELECT xp_time, xp_count, messages, cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    t = int(time.time())
    if dat:
        if (int(t) - dat["xp_time"]) >= serv["xp_cooldown"]:
            global top_servers
            count = 2
            if any(server_id == server["discord_id"] for server in top_servers):
                count *= 2
            await conn.execute("UPDATE users SET xp_time = {time}, xp_count = {count}, messages = {messages}, cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                stats_type=stats_type,
                time=t,
                count=dat["xp_count"] + 1,
                messages=dat["messages"]+1,
                cash=dat["cash"] + count,
                id=message.author.id
            ))
            if str(dat["xp_count"]+1) in xp_lvlup_list.keys():
                client.loop.create_task(u_check_lvlup(client, conn, message.channel, message.author, serv, str(dat["xp_count"]+1)))
        await conn.execute("UPDATE users SET messages = {messages} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            stats_type=stats_type,
            messages=dat["messages"]+1,
            id=message.author.id)
        )
    else:
        await conn.execute("INSERT INTO users(name, discord_id, discriminator, xp_count, xp_time, messages, background, stats_type) VALUES('{}', '{}', '{}', {}, {}, {}, '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, message.author.discriminator, 1, t, 1, random.choice(konoha_background_list), stats_type))

    if message.content.startswith(serv["prefix"]) or message.content.startswith("!help"):
        await client.process_commands(message)



def max(list):
    maximum = -1
    p = 0
    for s in range(len(list)):
        if int(list[s]) > maximum:
            maximum = int(list[s])
            p = s
    return p

async def strcmp(s1, s2):
    i1 = 0
    i2 = 0
    s1 = s1 + '\0'
    s2 = s2 + '\0'
    while ((s1[i1] != '\0') & (s2[i2] != '\0')):
        if(s1[i1] != s2[i2]):
            return 0
        i1 = i1 + 1
        i2 = i2 + 1
    if(s1[i1] != s2[i2]):
        return 0
    else:
        return 1

client.run(settings["konoha_token"])
