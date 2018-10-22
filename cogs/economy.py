import discord
import asyncio
import requests
import time
from datetime import datetime, date
import string
import random
import copy
import json
import asyncpg
import re
from discord.ext import commands
from cogs.const import *
from cogs.ids import *
from cogs.ids import *
from cogs.locale import *

async def e_timely(client, conn, context):
    message = context.message
    server_id = message.server.id
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash, daily_time FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{discord_id}'".format(stats_type=stats_type, discord_id=message.author.id))
    const = await conn.fetchrow("SELECT server_money, daily_count, daily_cooldown, em_color, is_timely, locale, likes FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_timely"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    count = const["daily_count"]
    global top_servers
    top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
    if any(server_id == server["discord_id"] for server in top_servers):
        count *= 2
    if dat:
        tim = int(time.time()) - dat["daily_time"]
        if tim < const["daily_cooldown"]:
            t=const["daily_cooldown"] - tim
            h=str(t//3600)
            m=str((t//60)%60)
            s=str(t%60)
            em.description = "{later1}\n{later2}".format(
            later1=locale[lang]["economy_try_again_later1"].format(
                who=clear_name(message.author.display_name+"#"+message.author.discriminator),
                money=const["server_money"]
                ),
            later2=locale[lang]["economy_try_again_later2"].format(
                hours=h,
                minutes=m,
                seconds=s
                )
            )
            if not message.server.id in servers_without_follow_us:
                em.add_field(
                    name=locale[lang]["global_follow_us"],
                    value=tomori_links,
                    inline=False
                )
            await client.send_message(message.channel, embed=em)
        else:
            await conn.execute("UPDATE users SET cash = {cash}, daily_time = {time} WHERE stats_type = '{stats_type}' AND discord_id = '{discord_id}'".format(stats_type=stats_type, cash=dat["cash"] + count, time=int(time.time()), discord_id=message.author.id))
            em.description = locale[lang]["economy_received_money"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), count, const[0])
            await client.send_message(message.channel, embed=em)
    else:
        await conn.execute("INSERT INTO users(name, discord_id, cash, daily_time, stats_type) VALUES('{}', '{}', {}, {}, '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, count, int(time.time()), stats_type))
        em.description = locale[lang]["economy_received_money"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), count, const[0])
        await client.send_message(message.channel, embed=em)
    return

async def e_give(client, conn, context, who, count):
    message = context.message
    server_id = message.server.id
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    const = await conn.fetchrow("SELECT server_money, server_money_name_net, em_color, is_give, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_give"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not who:
        em.description = locale[lang]["global_not_display_name_on_user"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if who.bot:
        em.description = locale[lang]["global_bot_display_nameed"].format(
            who=clear_name(message.author.display_name+"#"+message.author.discriminator),
            bot=clear_name(who.display_name[:50])
        )
        await client.send_message(message.channel, embed=em)
        return
    if who.id == message.author.id:
        em.description =locale[lang]["global_choose_someone_else"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if not count.isdigit() and not count == 'all':
        em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if count == '0':
        em.description = locale[lang]["economy_cant_give_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    count = count[:20]
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    dates = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
        dates = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if dat:
        if count == 'all':
            cooks = dat["cash"]
        elif dat["cash"] < int(count):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[1])
            if not message.server.id in servers_without_follow_us:
                em.add_field(
                    name=locale[lang]["global_follow_us"],
                    value=tomori_links,
                    inline=False
                )
            await client.send_message(message.channel, embed=em)
            return
        else:
            cooks = int(count)
        await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            cash=dat["cash"] - cooks,
            stats_type=stats_type,
            id=message.author.id
        ))
        await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            cash=dates["cash"] + cooks,
            stats_type=stats_type,
            id=who.id
        ))
        em.description = locale[lang]["economy_give"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), cooks, const[0], clear_name(who.display_name[:50]))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[1])
        if not message.server.id in servers_without_follow_us:
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
    await client.send_message(message.channel, embed=em)
    return

async def e_gift(client, conn, context, count):
    message = context.message
    server_id = message.server.id
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    const = await conn.fetchrow("SELECT server_money, em_color, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not server_id in local_stats_servers:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            cash=dat["cash"] + count,
            stats_type=stats_type,
            id=message.author.id
        ))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, cash, stats_type) VALUES('{}', '{}', {}, '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, count, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
    em.description = locale[lang]["economy_gift"].format(count=count, money=const["server_money"])
    await client.send_message(message.author, embed=em)
    return

async def e_cash(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, is_cash, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_cash"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        count = dat["cash"]
    else:
        count = 0
    em.description = locale[lang]["economy_user_have"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), count, const[0])
    await client.send_message(message.channel, embed=em)
    return

async def e_work(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, is_work, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_work"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT work_time FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        if dat["work_time"] == 0:
            await conn.execute("UPDATE users SET work_time = {time} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                time=int(time.time()),
                stats_type=stats_type,
                id=message.author.id
            ))
            em.description = locale[lang]["economy_went_to_work"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            await client.send_message(message.channel, embed=em)
        else:
            em.description = locale[lang]["economy_already_at_work"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            if not message.server.id in servers_without_follow_us:
                em.add_field(
                    name=locale[lang]["global_follow_us"],
                    value=tomori_links,
                    inline=False
                )
            await client.send_message(message.channel, embed=em)
    else:
        await conn.execute("INSERT INTO users(name, discord_id, work_time, stats_type) VALUES('{}', '{}', {}, '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, int(time.time()), stats_type))
        em.description = locale[lang]["economy_went_to_work"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
    return

async def e_br(client, conn, context, count):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, is_br, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_br"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not count or not count.isdigit() and not count == 'all':
        em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if count == '0':
        em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    count = count[:20]
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        if count == 'all':
            summ = dat["cash"]
        elif dat["cash"] < int(count):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em.add_field(
                    name=locale[lang]["global_follow_us"],
                    value=tomori_links,
                    inline=False
                )
            await client.send_message(message.channel, embed=em)
            return
        else:
            summ = int(count)
        if summ > BR_MAX_BET:
            em.description = locale[lang]["economy_max_bet_is"].format(
                who=clear_name(message.author.display_name+"#"+message.author.discriminator),
                bet=BR_MAX_BET,
                money=const["server_money"])
            await client.send_message(message.channel, embed=em)
            return
        if summ == 0:
            em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            await client.send_message(message.channel, embed=em)
            return
        if (random.randint(0, 99)) > 49:
            summ = int(summ/2)
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                cash=dat["cash"] + summ,
                stats_type=stats_type,
                id=message.author.id
            ))
            em.description = locale[lang]["economy_you_win"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), summ, const[0])
            await client.send_message(message.channel, embed=em)
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                cash=dat["cash"] - summ,
                stats_type=stats_type,
                id=message.author.id
            ))
            em.description = locale[lang]["economy_you_lose"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), summ, const[0])
            await client.send_message(message.channel, embed=em)
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        await client.send_message(message.channel, embed=em)
    return

async def e_slots(client, conn, context, count):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, is_slots, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_slots"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not count or not count.isdigit() and not count == 'all':
        em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if count == '0':
        em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    count = count[:20]
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash, name FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    em.set_author(name=locale[lang]["economy_slots"].format(dat["name"]), icon_url=message.author.avatar_url)
    if dat:
        if count == 'all':
            summ = dat["cash"]
        elif dat["cash"] < int(count):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em.add_field(
                    name=locale[lang]["global_follow_us"],
                    value=tomori_links,
                    inline=False
                )
            await client.send_message(message.channel, embed=em)
            return
        else:
            summ = int(count)
        if summ > SLOTS_MAX_BET:
            em.description = locale[lang]["economy_max_bet_is"].format(
                who=clear_name(message.author.display_name+"#"+message.author.discriminator),
                bet=SLOTS_MAX_BET,
                money=const["server_money"])
            await client.send_message(message.channel, embed=em)
            return
        if summ == 0:
            em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            await client.send_message(message.channel, embed=em)
            return
        random.shuffle(slots_ver)
        fails = 0
        rets = 0
        if slots_ver[0] == slot_trap or slots_ver[1] == slot_trap or slots_ver[2] == slot_trap:
            fails = 5
        else:
            if slots_ver[0] == slot_boom or slots_ver[0] == slot_melban:
                fails += 1
            if slots_ver[1] == slot_boom or slots_ver[1] == slot_melban:
                fails += 1
            if slots_ver[2] == slot_boom or slots_ver[2] == slot_melban:
                fails += 1
        if fails < 2:
            i = -1
            while i < 2:
                i += 1
                if slots_ver[i] == slot_kanna:
                    rets += summ * 3
                    continue
                if slots_ver[i] == slot_awoo:
                    rets += int(summ / 2)
                    continue
                if slots_ver[i] == slot_salt:
                    rets += int(summ / 3)
                    continue
                if slots_ver[i] == slot_doge:
                    rets += int(summ + summ / 3)
                    continue
                if slots_ver[i] == slot_pantsu2:
                    rets += summ * 1
                    continue
                if slots_ver[i] == slot_pantsu1:
                    rets += summ * 2
                    continue
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                cash=dat["cash"] + rets,
                stats_type=stats_type,
                id=message.author.id
            ))
            em.description = " {slot1} {slot2} {slot3}\n{response}".format(
                slot1=slots_ver[0],
                slot2=slots_ver[1],
                slot3=slots_ver[2],
                response=locale[lang]["economy_you_win"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), rets, const["server_money"])
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                cash=dat["cash"] - summ,
                stats_type=stats_type,
                id=message.author.id
            ))
            em.description = " {slot1} {slot2} {slot3}\n{response}".format(
                slot1=slots_ver[0],
                slot2=slots_ver[1],
                slot3=slots_ver[2],
                response=locale[lang]["economy_you_lose"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), summ, const["server_money"])
            )
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
    await client.send_message(message.channel, embed=em)
    return

async def e_buy(client, conn, context, value):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale, bank FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    role = discord.utils.get(message.server.roles, name=value)
    if not role:
        value = re.sub(r'[<@#&!>]+', '', value.lower())
        role = discord.utils.get(message.server.roles, id=value)
    if value.isdigit() and not value == "0":
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'shop' AND server_id = '{server_id}' ORDER BY condition::int DESC OFFSET {offset}".format(server_id=server_id, offset=int(value)-1))
        if dat:
            role = discord.utils.get(message.server.roles, id=dat["name"])
    if not role:
        em.description = locale[lang]["global_role_not_exists"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    if role in message.author.roles:
        em.description = locale[lang]["global_role_already_have"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            role=role.mention
        )
        await client.send_message(message.channel, embed=em)
        return
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'shop' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=role.id))
    if dat:
        user = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
        if user:
            if int(dat["condition"]) > user["cash"]:
                em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
                if not message.server.id in servers_without_follow_us:
                    em.add_field(
                        name=locale[lang]["global_follow_us"],
                        value=tomori_links,
                        inline=False
                    )
            else:
                try:
                    await client.add_roles(message.author, role)
                except:
                    em.description = locale[lang]["economy_role_not_permission"].format(
                        who=message.author.display_name+"#"+message.author.discriminator,
                        role=role.mention
                    )
                    await client.send_message(message.channel, embed=em)
                    return
                await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                    cash=user["cash"] - int(dat["condition"]),
                    stats_type=stats_type,
                    id=message.author.id
                ))
                if int(dat["condition"]) > 0:
                    await conn.execute("UPDATE settings SET bank = {bank} WHERE discord_id = '{id}'".format(bank=const["bank"] + int(dat["condition"]), id=message.server.id))
                em.description = locale[lang]["economy_role_response"].format(
                    who=message.author.mention,
                    role=role.mention
                )
        else:
            await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em.add_field(
                    name=locale[lang]["global_follow_us"],
                    value=tomori_links,
                    inline=False
                )
    else:
        em.description = locale[lang]["economy_role_not_in_shop"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            role=role.mention
        )
    await client.send_message(message.channel, embed=em)

async def e_shop(client, conn, context, page):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    dat = await conn.fetchrow("SELECT COUNT(name) FROM mods WHERE type = 'shop' AND server_id = '{server_id}'".format(server_id=server_id))
    all_count = dat[0]
    pages = (((all_count - 1) // 25) + 1)
    if not page:
        page = 1
    em.title = locale[lang]["economy_shop_title"]
    if all_count == 0:
        em.description = locale[lang]["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    if page > pages:
        em.description = locale[lang]["global_page_not_exists"].format(who=message.author.display_name+"#"+message.author.discriminator, number=page)
        await client.send_message(message.channel, embed=em)
        return
    dat = await conn.fetch("SELECT * FROM mods WHERE type = 'shop' AND server_id = '{server_id}' ORDER BY condition::int DESC LIMIT 25 OFFSET {offset}".format(server_id=server_id, offset=(page-1)*25))
    if dat:
        for index, role in enumerate(dat):
            _role = discord.utils.get(message.server.roles, id=role["name"])
            if _role:
                em.add_field(
                    name="󠂪",
                    #name="#{index} {name}".format(index=index+1+(page-1)*25, name=_role.name),
                    value="**#{index} {name}".format(index=index+1+(page-1)*25, name=_role.mention)+"**\n"+role["condition"]+" "+const["server_money"],
                    inline=True
                )
        em.set_footer(text=locale[lang]["other_footer_page"].format(number=page, length=pages)+" | "+locale[lang]["other_shop_how_to_buy"].format(prefix=const["prefix"]))
    else:
        em.description = locale[lang]["global_list_is_empty"]
    await client.send_message(message.channel, embed=em)
    return

async def e_pay(client, conn, context, count):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale, bank, server_money FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    count = count[:20].lower()
    if count == "all":
        count = const["bank"]
    else:
        if not count.isdigit():
            em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            await client.send_message(message.channel, embed=em)
            return
        count = int(count)
    if count == 0:
        em.description = locale[lang]["global_cant_select_zero"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if message.server.id in local_stats_servers:
        stats_type = message.server.id
    else:
        stats_type = "global"
    user = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if user:
        if count > const["bank"]:
            em.description = locale[lang]["other_pay_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em.add_field(
                    name=locale[lang]["global_follow_us"],
                    value=tomori_links,
                    inline=False
                )
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                cash=user["cash"] + count,
                stats_type=stats_type,
                id=message.author.id
            ))
            await conn.execute("UPDATE settings SET bank = {bank} WHERE discord_id = '{id}'".format(bank=const["bank"] - count, id=message.server.id))
            em.description = locale[lang]["economy_pay_response"].format(
                who=message.author.mention,
                count=count,
                money=const["server_money"]
            )
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
    await client.send_message(message.channel, embed=em)
    return
