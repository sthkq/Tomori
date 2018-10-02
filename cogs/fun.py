import os
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
import imghdr
from discord.ext import commands
from config.settings import settings
from PIL import Image, ImageChops, ImageFont, ImageDraw, ImageSequence, ImageFilter
from PIL.GifImagePlugin import getheader, getdata
from functools import partial
import aiohttp
from io import BytesIO
from typing import Union
from cogs.const import *
from cogs.locale import *


mask = Image.new('L', (364, 364), 0)
draws = ImageDraw.Draw(mask)
draws.ellipse((0, 0) + (40, 40), fill=255)
draws.ellipse((324, 0) + (364, 40), fill=255)
draws.ellipse((0, 324) + (40, 364), fill=255)
draws.ellipse((324, 324) + (364, 364), fill=255)
draws.rectangle(((0, 20), (364, 344)), fill=255)
draws.rectangle(((20, 0), (344, 364)), fill=255)
mask = mask.resize((364, 364), Image.ANTIALIAS)

mask_top = Image.new('L', (269, 269), 0)
draws_top = ImageDraw.Draw(mask_top)
draws_top.ellipse((0, 0) + (269, 269), fill=255)
mask_top = mask_top.resize((269, 269), Image.ANTIALIAS)

mask_top_back = Image.new('L', (549, 549), 0)
draws_top_back = ImageDraw.Draw(mask_top_back)
draws_top_back.rectangle((274, 0) + (474, 549), fill=255)
mask_top_back = mask_top_back.resize((549, 549), Image.ANTIALIAS)



async def f_me(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, is_me, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const or not const["is_me"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    await client.send_typing(message.channel)
    if not who:
        who = message.author
    dat = await conn.fetchrow("SELECT * FROM users WHERE discord_id = '{}'".format(who.id))
    if not dat:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
        dat = await conn.fetchrow("SELECT * FROM users WHERE discord_id = '{}'".format(who.id))
    background = dat["background"]
    if not background:
        background = random.choice(background_list)
        await conn.execute("UPDATE users SET background = '{back}' WHERE discord_id = '{id}'".format(back=random.choice(background_list), id=who.id))
    cash_rank = await conn.fetchrow("SELECT COUNT(DISTINCT cash) AS qty FROM users WHERE cash > {}".format(dat["cash"]))
    rep_rank = await conn.fetchrow("SELECT COUNT(DISTINCT reputation) AS qty FROM users WHERE reputation > {}".format(dat["reputation"]))
    xp_rank = await conn.fetchrow("SELECT COUNT(DISTINCT xp_count) AS qty FROM users WHERE xp_count > {}".format(dat["xp_count"]))
#================================================== stats 1
    xp_lvl = 0
    i = 1
    if dat["xp_count"] > 0:
        while dat["xp_count"] >= (i * (i + 1) * 5):
            xp_lvl = xp_lvl + 1
            i = i + 1
    xp_count = "{}/{}".format(dat["xp_count"], ((xp_lvl + 1) * (xp_lvl + 2) * 5))
    xp_lvl = str(xp_lvl)
#==================================================
    back = Image.open("cogs/stat/backgrounds/{}".format(background))
    draw_b = ImageDraw.Draw(back)
    under = Image.open("cogs/stat/backgrounds/under.png")

    font_right = ImageFont.truetype("cogs/stat/Lato.ttf", 16)
    font_xp_count = ImageFont.truetype("cogs/stat/WhitneyBold.ttf", 37)

    ava_url = who.avatar_url
    if not ava_url:
        ava_url = who.default_avatar_url
    response = requests.get(ava_url)
    avatar = Image.open(BytesIO(response.content))
    avatar = avatar.resize((364, 364))
    avatar.putalpha(mask)
    avatar = avatar.resize((91, 91))
    back = back.filter(ImageFilter.GaussianBlur(1))
    back.paste(under, (0, 0), under)
    back.paste(avatar, (355, 151), avatar)



    halo = Image.new('RGBA', back.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).text(
        (400-font_xp_count.getsize(xp_count)[0]/2, 335-font_xp_count.getsize(xp_count)[1]/2),
        xp_count,
        (0, 0, 0),
        font=font_xp_count
    )
    kernel = [
        0, 1, 2, 1, 0,
        1, 2, 4, 2, 1,
        2, 4, 8, 4, 1,
        1, 2, 4, 2, 1,
        0, 1, 2, 1, 0
    ]
    kernelsum = sum(kernel)
    myfilter = ImageFilter.Kernel((5, 5), kernel, scale = 0.5 * kernelsum)
    blurred_halo = halo.filter(myfilter)
    ImageDraw.Draw(blurred_halo).text(
        (400-font_xp_count.getsize(xp_count)[0]/2, 335-font_xp_count.getsize(xp_count)[1]/2),
        xp_count,
        (255, 255, 255),
        font=font_xp_count
    )
    back = Image.composite(back, blurred_halo, ImageChops.invert(blurred_halo))
    draw = ImageDraw.Draw(back)

    draw.text(
        (703-font_right.getsize(xp_lvl)[0]/2, 71-font_right.getsize(xp_lvl)[1]/2),
        xp_lvl,
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (703-font_right.getsize(str(dat["reputation"]))[0]/2, 118-font_right.getsize(str(dat["reputation"]))[1]/2),
        str(dat["reputation"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (703-font_right.getsize(str(dat["cash"]))[0]/2, 353-font_right.getsize(str(dat["cash"]))[1]/2),
        str(dat["cash"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (140-font_right.getsize(str(dat["drink_count"]))[0], 353-font_right.getsize(str(dat["drink_count"]))[1]/2),
        str(dat["drink_count"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (140-font_right.getsize(str(dat["fuck_count"]))[0], 306-font_right.getsize(str(dat["fuck_count"]))[1]/2),
        str(dat["fuck_count"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (140-font_right.getsize(str(dat["wink_count"]))[0], 259-font_right.getsize(str(dat["wink_count"]))[1]/2),
        str(dat["wink_count"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (140-font_right.getsize(str(dat["five_count"]))[0], 212-font_right.getsize(str(dat["five_count"]))[1]/2),
        str(dat["five_count"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (140-font_right.getsize(str(dat["punch_count"]))[0], 165-font_right.getsize(str(dat["punch_count"]))[1]/2),
        str(dat["punch_count"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (140-font_right.getsize(str(dat["hug_count"]))[0], 118-font_right.getsize(str(dat["hug_count"]))[1]/2),
        str(dat["hug_count"]),
        (0, 0, 0),
        font=font_right
    )
    draw.text(
        (140-font_right.getsize(str(dat["kiss_count"]))[0], 71-font_right.getsize(str(dat["kiss_count"]))[1]/2),
        str(dat["kiss_count"]),
        (0, 0, 0),
        font=font_right
    )
    name = u"{}".format(who.display_name)
    name_size = 1
    font_name = ImageFont.truetype("cogs/stat/Lato.ttf", name_size)
    while font_name.getsize(name)[0] < 150:
        name_size += 1
        font_name = ImageFont.truetype("cogs/stat/Lato.ttf", name_size)
        if name_size == 18:
            break
    name_size -= 1
    font_name = ImageFont.truetype("cogs/stat/Lato.ttf", name_size)
    draw.text(
        (400-font_name.getsize(name)[0]/2, 255-font_name.getsize(name)[1]/2),
        name,
        (0, 0, 0),
        font=font_name
    )

    back.save('cogs/stat/return/{}.png'.format(message.author.id))
    await client.upload("cogs/stat/return/{}.png".format(message.author.id))
    os.remove("cogs/stat/return/{}.png".format(message.author.id))
    return

async def f_hug(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, hug_price, is_hug, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_hug"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(message.author.id))
    dates = await conn.fetchrow("SELECT hug_count FROM users WHERE discord_id = '{}'".format(who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
        dates = await conn.fetchrow("SELECT hug_count FROM users WHERE discord_id = '{}'".format(who.id))
    if dat:
        if (const["hug_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE discord_id = '{id}'".format(cash=dat["cash"] - const["hug_price"], id=message.author.id))
            await conn.execute("UPDATE users SET hug_count = {count} WHERE discord_id = '{id}'".format(count=dates["hug_count"] + 1, id=who.id))
            em.description =  locale[lang]["fun_hug"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(hug_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def f_kiss(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, kiss_price, is_kiss, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_kiss"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(message.author.id))
    dates = await conn.fetchrow("SELECT kiss_count FROM users WHERE discord_id = '{}'".format(who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
        dates = await conn.fetchrow("SELECT kiss_count FROM users WHERE discord_id = '{}'".format(who.id))
    if dat:
        if (const["kiss_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE discord_id = '{id}'".format(cash=dat["cash"] - const["kiss_price"], id=message.author.id))
            await conn.execute("UPDATE users SET kiss_count = {count} WHERE discord_id = '{id}'".format(count=dates["kiss_count"] + 1, id=who.id))
            em.description =  locale[lang]["fun_kiss"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(kiss_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def f_five(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, five_price, is_five, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_five"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT cash, five_count FROM users WHERE discord_id = '{}'".format(message.author.id))
    if dat:
        if (const["five_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash}, five_count = {count} WHERE discord_id = '{id}'".format(cash=dat["cash"] - const["five_price"], count=dat["five_count"]+1, id=message.author.id))
            em.description =  locale[lang]["fun_five"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(five_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def f_punch(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, punch_price, is_punch, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const[3]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(message.author.id))
    dates = await conn.fetchrow("SELECT punch_count FROM users WHERE discord_id = '{}'".format(who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
        dates = await conn.fetchrow("SELECT punch_count FROM users WHERE discord_id = '{}'".format(who.id))
    if dat:
        if (const["punch_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE discord_id = '{id}'".format(cash=dat["cash"] - const["punch_price"], id=message.author.id))
            await conn.execute("UPDATE users SET punch_count = {count} WHERE discord_id = '{id}'".format(count=dates["punch_count"] + 1, id=who.id))
            em.description =  locale[lang]["fun_punch"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(punch_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def f_fuck(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, fuck_price, is_fuck, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const[3]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT cash, fuck_count FROM users WHERE discord_id = '{}'".format(message.author.id))
    if dat:
        if (const["fuck_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash}, fuck_count = {count} WHERE discord_id = '{id}'".format(cash=dat["cash"] - const["fuck_price"], count=dat["fuck_count"]+1, id=message.author.id))
            em.description =  locale[lang]["fun_fuck"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(fuck_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def f_wink(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, wink_price, is_wink, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const[3]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT cash, wink_count FROM users WHERE discord_id = '{}'".format(message.author.id))
    if dat:
        if (const["wink_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash}, wink_count = {count} WHERE discord_id = '{id}'".format(cash=dat["cash"] - const["wink_price"], count=dat["wink_count"]+1, id=message.author.id))
            em.description =  locale[lang]["fun_wink"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(wink_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def f_drink(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, drink_price, is_drink, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const[3]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    dat = await conn.fetchrow("SELECT cash, drink_count FROM users WHERE discord_id = '{}'".format(message.author.id))
    if dat:
        if (const["drink_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["cash"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {cash}, drink_count = {count} WHERE discord_id = '{id}'".format(cash=dat["cash"] - const["drink_price"], count=dat["drink_count"]+1, id=message.author.id))
            em.description =  locale[lang]["fun_drink"].format(message.author.mention)
            em.set_image(url=random.choice(drink_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def f_rep(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT rep_cooldown, em_color, is_rep, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + int("0x200", 16))
    if not const or not const["is_rep"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT rep_time FROM users WHERE discord_id = '{}'".format(message.author.id))
    dates = await conn.fetchrow("SELECT reputation FROM users WHERE discord_id = '{}'".format(who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
        dates = await conn.fetchrow("SELECT reputation FROM users WHERE discord_id = '{}'".format(who.id))
    if not dat:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        dat = await conn.fetchrow("SELECT rep_time FROM users WHERE discord_id = '{}'".format(message.author.id))
    tim = int(time.time()) - dat["rep_time"]
    if tim < const["rep_cooldown"]:
        t=const["rep_cooldown"] - tim
        h=str(t//3600)
        m=str((t//60)%60)
        s=str(t%60)
        em.description = "{later1}\n{later2}".format(
        later1=locale[lang]["rep_try_again_later1"].format(
            who=clear_name(message.author.display_name+"#"+message.author.discriminator)
            ),
        later2=locale[lang]["rep_try_again_later2"].format(
            hours=h,
            minutes=m,
            seconds=s
            )
        )
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    else:
        await conn.execute("UPDATE users SET rep_time = {} WHERE discord_id = '{}'".format(int(time.time()), message.author.id))
        await conn.execute("UPDATE users SET reputation = {} WHERE discord_id = '{}'".format(dates["reputation"] + 3, who.id))
        em.description =  locale[lang]["fun_rep_success"].format(message.author.mention, who.mention)
    await client.send_message(message.channel, embed=em)
    return

async def f_sex(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, sex_price, is_sex, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const[3]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    dat = await conn.fetchrow("SELECT cash, sex_count FROM users WHERE discord_id = '{}'".format(message.author.id))
    dates = await conn.fetchrow("SELECT sex_count FROM users WHERE discord_id = '{}'".format(who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
        dates = await conn.fetchrow("SELECT sex_count FROM users WHERE discord_id = '{}'".format(who.id))
    if dat:
        if (const[2] > dat[0]):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            em.add_field(
                name=locale[lang]["global_follow_us"],
                value=tomori_links,
                inline=False
            )
        else:
            await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(dat[0] - const[2], message.author.id))
            await conn.execute("UPDATE users SET sex_count = {} WHERE discord_id = '{}'".format(dates[0] + 1, who.id))
            em.description =  "{} трахнул {}".format(message.author.display_name+"#"+message.author.discriminator, who.display_name+"#"+who.discriminator)
            em.set_image(url=random.choice(sex_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def are_you_nitty(client, lang, who, message):
    em = discord.Embed(colour=0xC5934B)
    if not who:
        em.description = locale[lang]["global_not_display_name_on_user"].format(message.author.display_name+"#"+message.author.discriminator)
    elif who.bot:
        em.description = locale[lang]["global_bot_display_nameed"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            bot=who.display_name[:50]
        )
    elif message.author == who:
        em.description = locale[lang]["global_choose_someone_else"].format(message.author.display_name+"#"+message.author.discriminator)
    else:
        return False
    await client.send_message(message.channel, embed=em)
    return True


async def f_top(client, conn, context, page):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, is_me, locale, em_color FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_me"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    await client.send_typing(message.channel)
    dat = await conn.fetchrow("SELECT COUNT(name) FROM users")
    all_count = dat[0]
    pages = (((all_count - 1) // 5) + 1)
    if not page:
        page = 1
    if all_count == 0:
        em.description = locale[lang]["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    if page > pages:
        em.description = locale[lang]["global_page_not_exists"].format(who=message.author.display_name+"#"+message.author.discriminator, number=page)
        await client.send_message(message.channel, embed=em)
        return
    dat = await conn.fetch("SELECT name, discord_id, avatar_url, xp_count FROM users ORDER BY xp_count DESC LIMIT 5 OFFSET {offset}".format(offset=(page-1)*5))
#==================================================
    img = Image.open("cogs/stat/top5.png")
    back = Image.open("cogs/stat/top5.png")
    draw = ImageDraw.Draw(img)
    draws = ImageDraw.Draw(back)

    font_position = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", 24)
    font_xp_count = ImageFont.truetype("cogs/stat/Roboto-Regular.ttf", 16)

    for i, user in enumerate(dat):
        name = user["name"]
        name = u"{}".format(name)
        name_size = 1
        font_name = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", name_size)
        while font_name.getsize(name)[0] < 180:
            name_size += 1
            font_name = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", name_size)
            if name_size == 31:
                break
        name_size -= 1
        font_name = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", name_size)
        if not name:
            name = " "
        ava_url = user["avatar_url"]
        if not ava_url:
            ava_url = client.user.default_avatar_url
            for server in client.servers:
                member = server.get_member(user["discord_id"])
                if member and member.avatar_url:
                    ava_url = member.avatar_url
                    await conn.execute("UPDATE users SET avatar_url = '{url}' WHERE discord_id = '{id}'".format(
                        url=ava_url,
                        id=user["discord_id"]
                    ))
                    break
        response = requests.get(ava_url)
        avatar = Image.open(BytesIO(response.content))
        avatar_circle = avatar.resize((549, 549))
        avatar_circle.putalpha(mask_top_back)
        avatar_circle = avatar_circle.crop((274, 0, 474, 549))
        back.paste(avatar_circle, (i*200, 0), avatar_circle)
        avatar_circle = avatar.resize((269, 269))
        bigsize = (avatar_circle.size[0] * 3, avatar_circle.size[1] * 3)
        avatar_circle.putalpha(mask_top)
        avatar_circle = avatar_circle.crop((0, 0, 134, 269))
        img.paste(avatar_circle, (66+i*200, 125), avatar_circle)
        position = "#{}".format(i+1+(page-1)*5)
        draw.text(
            (
                100-font_position.getsize(position)[0]/2+i*200,
                440-font_position.getsize(position)[1]/2
            ),
            position,
            (255, 255, 255),
            font=font_position
        )
        draw.text((100-font_name.getsize(name)[0]/2+i*200, 50-font_name.getsize(name)[1]/2), name, (255, 255, 255), font=font_name)
        xp_count = locale[lang]["fun_top5_xp_count"].format((user["xp_count"]))
        draw.text(
            (
                100-font_xp_count.getsize(xp_count)[0]/2+i*200,
                475-font_xp_count.getsize(xp_count)[1]/2
            ),
            xp_count,
            (255, 255, 255),
            font=font_xp_count
        )

    back.paste(img, (0, 0), img)

    back.save('cogs/stat/return/top/{}.png'.format(message.author.id))
    await client.send_file(message.channel, "cogs/stat/return/top/{}.png".format(message.author.id), content=locale[lang]["fun_top5_response"])
    os.remove("cogs/stat/return/top/{}.png".format(message.author.id))
    return
