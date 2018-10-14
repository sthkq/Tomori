import discord
import asyncio
import requests
import time
from datetime import datetime, date
import string
import random
import copy
import re
import json
import asyncpg
from discord.ext import commands
from cogs.locale import *
from cogs.const import *
from cogs.help import *
from cogs.ids import *
from cogs.discord_hooks import Webhook

support_url = "https://discord.gg/tomori"
site_url = "http://discord.band"
site_commands_url = "https://discord.band/commands"
invite_url = "https://discordapp.com/api/oauth2/authorize?client_id=491605739635212298&permissions=536341719&redirect_uri=https%3A%2F%2Fdiscord.band&scope=bot"



async def o_webhook(client, conn, context, name, value):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=clear_name(name).lower()))
    if not dat:
        em.description = locale[lang]["other_webhook_not_exists"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            name=name
        )
        await client.send_message(message.channel, embed=em)
        return
    try:
        ret = json.loads(value)
        if ret and isinstance(ret, dict):
            msg = Webhook(web_url=dat["value"], **ret)
            msg.post()
        else:
            msg = Webhook(
                web_url=dat["value"],
                text=value
            )
            msg.post()
    except:
        msg = Webhook(
            web_url=dat["value"],
            text=value
        )
        msg.post()

async def o_about(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if const["locale"] == "english":
        em.description = "***Python-bot created by __Ананасовая Печенюха (Cookie)__\n\
supported by __Unknown__ and __Teris__.***\n\n\
**[Support server]({support_url})**\n\
**[Site]({site_url})**\n\n\
For any questions talk to <@316287332779163648>.".format(support_url=support_url, site_url=site_url)
    else:
        em.description = "***Python-bot написанный __Ананасовой Печенюхой__\n\
при поддержке __Unknown'a__ и __Teris'а__.***\n\n\
**[Ссылка на сервер поддержки]({support_url})**\n\
**[Ссылка на сайт]({site_url})**\n\n\
По всем вопросам обращайтесь к <@316287332779163648>.".format(support_url=support_url, site_url=site_url)
    em.add_field(
        name=locale[lang]["global_follow_us"],
        value=tomori_links,
        inline=False
    )
    await client.send_message(message.channel, embed=em)
    return

async def o_invite(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.title = locale[lang]["other_invite_title"]
    em.description = invite_url
    em.add_field(
        name=locale[lang]["global_follow_us"],
        value=tomori_links,
        inline=False
    )
    await client.send_message(message.author, embed=em)
    return

async def o_server(client, conn, context):
    message = context.message
    server_id = message.server.id
    server = message.server
    const = await conn.fetchrow("SELECT em_color, prefix, locale, bank, server_money FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.set_author(name=server.name, icon_url=server.icon_url)
    em.add_field(
        name=locale[lang]["other_server_owner"],
        value="{0.name}#{0.discriminator}".format(server.owner),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_prefix"],
        value=const["prefix"],
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_bank"],
        value=str(const["bank"]),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_channels"],
        value=str(len(server.channels)),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_members"],
        value=str(len(server.members)),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_lifetime"],
        value=locale[lang]["other_server_days"].format(int((datetime.utcnow() - server.created_at).days)),
        inline=True
    )
    em.add_field(
        name=":satellite:ID",
        value=server.id,
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_emojis"],
        value=str(len(server.emojis)),
        inline=True
    )
    em.set_thumbnail(url=message.server.icon_url)
    await client.send_message(message.channel, embed=em)
    return

async def o_avatar(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, is_avatar, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    if not who:
        who = message.author
    em.title = locale[lang]["other_avatar"].format(clear_name(who.display_name[:50]))
    em.set_image(url=who.avatar_url)
    await client.send_message(message.channel, embed=em)
    return

async def o_like(client, conn, context):
    message = context.message
    server_id = message.server.id
    if message.author.bot or message.channel.is_private:
        return
    const = await conn.fetchrow("SELECT em_color, locale, likes, like_one, like_time FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    now = int(time.time())
    if now - const["like_time"] > 14400:
        await conn.execute("UPDATE settings SET likes = {likes}, like_time = {like_time} WHERE discord_id = '{discord_id}'".format(
            likes=const["likes"] + const["like_one"],
            like_time=now,
            discord_id=server_id
        ))
        global top_servers
        top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
        em.description = locale[lang]["other_like_success"].format(who=message.author.display_name+"#"+message.author.discriminator)
    else:
        t=14400 - now + const["like_time"]
        h=str(t//3600)
        m=str((t//60)%60)
        s=str(t%60)
        em.description = locale[lang]["other_like_wait"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            hours=h,
            minutes=m,
            seconds=s
            )
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def o_list(client, conn, context, page):
    message = context.message
    server_id = message.server.id
    if message.author.bot or message.channel.is_private:
        return
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    _locale = locale[lang]
    em = discord.Embed(colour=0x87b5ff)
    if not const:
        em.description = _locale["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    dat = await conn.fetchrow("SELECT COUNT(name) FROM settings")
    all_count = dat[0]
    pages = (((all_count - 1) // 10) + 1)
    if not page:
        page = 1
    if page > pages:
        em.description = _locale["global_page_not_exists"].format(who=message.author.display_name+"#"+message.author.discriminator, number=page)
        await client.send_message(message.channel, embed=em)
        return
    em.title = _locale["other_top_of_servers"]
    if all_count == 0:
        em.description = _locale["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    dat = await conn.fetch("SELECT name, discord_id, likes, invite FROM settings ORDER BY likes DESC, like_time DESC LIMIT 10 OFFSET {offset}".format(offset=(page-1)*10))
    for index, server in enumerate(dat):
        member_count = 0
        serv = client.get_server(server["discord_id"])
        if serv:
            member_count = serv.member_count
        if not server["invite"] or not await u_check_invite(client, server["invite"]):
            link = await u_invite_to_server(client, server["discord_id"])
            if link:
                await conn.execute("UPDATE settings SET invite = '{link}' WHERE discord_id = '{id}'".format(
                    link=link,
                    id=server["discord_id"]
                ))
            else:
                link = "https://discord-server.com/"+server["discord_id"]
        else:
            link = server["invite"]
        em.add_field(
            name="#{index} {name}".format(
                index=(page-1)*10+index+1,
                name=server["name"]
            ),
            value="<:likes:493040819402702869>\xa0{likes}\xa0\xa0<:users:492827033026560020>\xa0{member_count}\xa0\xa0[<:server:492861835087708162>](https://discord-server.com/{id} \"{link_message}\")".format(
                likes=server["likes"],
                member_count=member_count,
                id=server["discord_id"],
                link_message=_locale["other_list_link_message"]
            ),
            inline=True
        )
    em.set_footer(text=_locale["other_footer_page"].format(number=page, length=pages))
    await client.send_message(message.channel, embed=em)
    return

async def o_report(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale, prefix, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    eD = discord.Embed(color = 0xC5934B, title = "Report from user:", description = message.content)
    eD.add_field(name = "Server", value = "Name: " + message.server.name + "\n" + "Id: `" + message.server.id + "`")
    eD.add_field(name = "Settings", value = "Locale: \"" + const["locale"] + "\"\n" + "Prefix: `" + const["prefix"] + "`")
    eD.add_field(name = "Chat", value = "Name: " + message.channel.name + "\n" + "Id: `" + message.channel.id + "`")
    eD.add_field(name = "User", value = "Name: " + message.author.name + "\n" + "Id: `" + message.author.id + "`\n" + "Display Name: " + message.author.display_name)
    eD.set_author(name = message.author.name, icon_url= message.author.avatar_url)
    await client.send_message(client.get_channel(report_channel_id), embed=eD)

    em.title = locale[lang]["other_report_sent_success"].format(who=message.author.display_name+"#"+message.author.discriminator)
    em.set_image(url='https://media.giphy.com/media/xTkcESPybY7bmlKL7O/giphy.gif')
    await client.send_message(message.channel, embed=em)
    return

async def o_ping(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    now = datetime.utcnow()
    delta = now - message.timestamp
    latency = delta.microseconds / 1000
    em.description=locale[lang]["other_ping"].format(
        who=message.author.display_name+"#"+message.author.discriminator,
        latency=int(latency)
        )
    await client.send_message(message.channel, embed=em)
    return

async def o_help(client, conn, context):
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
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    if message.content.startswith(const["prefix"]+"help ") or message.content.startswith(const["prefix"]+"h "):
        await h_check_help(client, conn, message)
        return
    if not message.content == const["prefix"]+"help":
        return
    em.title = locale[lang]["other_help_title"]
    em.description = locale[lang]["other_help_desc"].format(const["name"], const["prefix"])
    com_adm = ""
    com_econ = ""
    com_fun = ""
    com_stat = ""
    com_other = ""
    com_mon = ""
    if const["is_say"]:
        com_adm += "``say``, "
    if const["is_clear"]:
        com_adm += "``clear``, "
    if const["is_sex"]:
        com_fun += "``sex``, "
    if const["is_kick"]:
        com_adm += "``kick``, "
    if const["is_ban"]:
        com_adm += "``ban``, ``unban``, "
    if const["is_timely"]:
        com_econ += "``timely``, "
    if const["is_work"]:
        com_econ += "``work``, "
    if const["is_br"]:
        com_econ += "``br``, "
    if const["is_slots"]:
        com_econ += "``slots``, "
    if const["is_give"]:
        com_econ += "``give``, "
    if const["is_kiss"]:
        com_fun += "``kiss``, "
    if const["is_hug"]:
        com_fun += "``hug``, "
    if const["is_punch"]:
        com_fun += "``punch``, "
    if const["is_five"]:
        com_fun += "``five``, "
    if const["is_wink"]:
        com_fun += "``wink``, "
    if const["is_fuck"]:
        com_fun += "``fuck``, "
    if const["is_drink"]:
        com_fun += "``drink``, "
    if const["is_rep"]:
        com_fun += "``rep``, "
    if const["is_cash"]:
        com_stat += "``$``, "
    if const["is_top"]:
        com_stat += "``top``, "
    if const["is_me"]:
        com_stat += "``me``, "
    com_other = "``help``, ``ping``, "
    if const["is_avatar"]:
        com_other += "``avatar``, "
    com_other += "``report``, ``server``, ``invite``, ``about``, "
    com_adm += "``send``, ``start``, ``stop``, ``pay``, "
    com_mon += "``like``, ``list``, "
    if com_adm != "":
        em.add_field(name="Admin", value=com_adm[:-2], inline=False)
    if com_econ != "":
        em.add_field(name="Economics", value=com_econ[:-2], inline=False)
    if com_fun != "":
        em.add_field(name="Fun", value=com_fun[:-2], inline=False)
    if com_stat != "":
        em.add_field(name="Stats", value=com_stat[:-2], inline=False)
    if com_mon != "":
        em.add_field(name="Monitoring", value=com_mon[:-2], inline=False)
    if com_other != "":
        em.add_field(name="Other", value=com_other[:-2], inline=False)
    em.add_field(name=locale[lang]["help_more_info"], value=site_commands_url, inline=False)
    em.set_footer(text=locale[lang]["help_help_by_command"].format(prefix=const["prefix"]))
    await client.send_message(message.channel, embed=em)
    return

async def o_backgrounds(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    em.title = locale[lang]["other_backgrounds_title"]
    if len(background_list) == 0:
        em.description = locale[lang]["other_backgrounds_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    for i, back in enumerate(background_name_list):
        em.add_field(
            name=locale[lang]["other_backgrounds_element"].format(
                position=i+1,
                name=back
            ),
            value="-------------------------",
            inline=True
        )
    await client.send_message(message.channel, embed=em)
    return

async def o_set(client, conn, context, arg1, arg2, args):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale, server_money FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass

    if arg1 == "background" or arg1 == "back":
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        if arg2.isdigit() and int(arg2) <= len(background_list) and int(arg2) > 0:
            arg2 = background_list[int(arg2)-1]
        else:
            arg2 = arg2.lower().replace(" ", "_") + ".jpg"
        if not arg2 in background_list:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if message.server.id in local_stats_servers:
            stats_type = message.server.id
        else:
            stats_type = "global"
        dat = await conn.fetchrow("SELECT cash, background FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            stats_type=stats_type,
            id=message.author.id
        ))
        if dat:
            if dat["cash"] < background_change_price:
                em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
                await client.send_message(message.channel, embed=em)
                return
            if dat["background"] == arg2:
                em.description = locale[lang]["other_backgrounds_already_has"].format(who=message.author.display_name+"#"+message.author.discriminator)
                await client.send_message(message.channel, embed=em)
                return
            await conn.execute("UPDATE users SET cash = {cash}, background = '{back}' WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                cash=dat[0] - background_change_price,
                back=arg2,
                stats_type=stats_type,
                id=message.author.id
            ))
            em.description = locale[lang]["other_backgrounds_success_response"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
        else:
            await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[1])
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "prefix":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="prefix"
            )
            em.description += "\n"+locale[lang]["other_set_prefix_you_can_try"]+" `%s`" % "`, `".join(prefix_list)
            await client.send_message(message.channel, embed=em)
            return
        if arg2 in prefix_list:
            await conn.execute("UPDATE settings SET prefix = '{}' WHERE discord_id = '{}'".format(arg2,server_id))
            em.description = locale[lang]["other_set_prefix_success"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                prefix=arg2
            )
            await client.send_message(message.channel, embed=em)
            return
        elif arg2 == "default":
            await conn.execute("UPDATE settings SET prefix = '{}' WHERE discord_id = '{}'".format('!',server_id))
            em.description = locale[lang]["other_set_prefix_success"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                prefix='!'
            )
            em.description += "\n" + locale[lang]["other_set_prefix_you_can_try"] + " `%s`" % "`, `".join(prefix_list)
        else:
            em.description = locale[lang]["other_set_prefix_you_can_try"] + " `%s`" % "`, `".join(prefix_list)
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "autorole":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        role = discord.utils.get(message.server.roles, name=arg2)
        if not role:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            role = discord.utils.get(message.server.roles, id=arg2)
        if not role:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT prefix FROM settings WHERE discord_id = '{}'".format(message.server.id))
        if dat:
            await conn.execute("UPDATE settings SET autorole_id = '{role_id}' WHERE discord_id = '{server_id}'".format(
                role_id=role.id,
                server_id=message.server.id
            ))
        else:
            await conn.execute("INSERT INTO settings(name, discord_id, autorole_id) VALUES('{name}', '{id}', '{role}')".format(
                name=clear_name(message.server.name[:50]),
                id=message.server.id,
                role=role.id
            ))
        em.description = locale[lang]["other_autorole_success_response"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            role_id=role.id
        )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "shop":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="cost"
            )
            await client.send_message(message.channel, embed=em)
            return
        args = args.rsplit(" ", 1)
        if len(args) == 2:
            arg2 = arg2 + " " + args[0]
            args = args[1]
            arg2 = arg2.rstrip()
        else:
            args = args[0]
        role = discord.utils.get(message.server.roles, name=arg2)
        if not role:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            role = discord.utils.get(message.server.roles, id=arg2)
        if not role:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args.isdigit():
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="cost"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'shop' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=role.id))
        if dat:
            em.description = locale[lang]["other_set_shop_exists"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                role_id=role.id
            )
        else:
            await conn.execute("INSERT INTO mods(name, server_id, type, condition) VALUES('{name}', '{id}', '{type}', '{cond}')".format(
                name=role.id,
                id=message.server.id,
                type="shop",
                cond=args
            ))
            em.description = locale[lang]["other_shop_success_response"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                role_id=role.id,
                cost=args
            )
        await client.send_message(message.channel, embed=em)
        return



    if arg1 == "language" or arg1 == "lang":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            em.description += "\n" + locale[lang]["other_you_can_try"] + " `%s`" % "`, `".join(short_locales.keys())
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        arg2 = arg2.lower()
        arg2 = short_locales.get(arg2, arg2)
        if not arg2 in locale.keys():
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT prefix FROM settings WHERE discord_id = '{}'".format(message.server.id))
        if dat:
            await conn.execute("UPDATE settings SET locale = '{lang}' WHERE discord_id = '{server_id}'".format(
                lang=arg2,
                server_id=message.server.id
            ))
        else:
            await conn.execute("INSERT INTO settings(name, discord_id, locale) VALUES('{name}', '{id}', '{lang}')".format(
                name=clear_name(message.server.name[:50]),
                id=message.server.id,
                lang=arg2
            ))
        em.description = locale[arg2]["other_lang_success_response"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            lang=arg2
        )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "webhook" or arg1 == "wh":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="value"
            )
            await client.send_message(message.channel, embed=em)
            return

        arg2 = clear_name(arg2).lower()
        args = clear_name(args)
        if not arg2:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=arg2))
        if dat:
            em.description = locale[lang]["other_set_webhook_exists"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                name=arg2
            )
        else:
            await conn.execute("INSERT INTO mods(name, server_id, type, value) VALUES('{name}', '{id}', '{type}', '{value}')".format(
                name=arg2,
                id=message.server.id,
                type="webhook",
                value=args
            ))
            em.description = locale[lang]["other_webhook_success_response"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                name=arg2
            )
        await client.send_message(message.channel, embed=em)
        return


    if not arg1:
        em.description = locale[lang]["other_missed_argument"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            arg="category"
        )
        await client.send_message(message.channel, embed=em)
        return

    em.description = locale[lang]["other_incorrect_argument"].format(
        who=message.author.display_name+"#"+message.author.discriminator,
        arg="category"
    )
    await client.send_message(message.channel, embed=em)
    return



























async def o_remove(client, conn, context, arg1, arg2, args):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale, server_money FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass


    if arg1 == "autorole":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.execute("UPDATE settings SET autorole_id = NULL WHERE discord_id = '{}'".format(message.server.id))
        em.description = locale[lang]["other_autorole_success_delete"].format(
            who=message.author.display_name+"#"+message.author.discriminator
        )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "webhook" or arg1 == "wh":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return

        arg2 = clear_name(arg2).lower()
        if not arg2:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=arg2))
        if not dat:
            em.description = locale[lang]["other_webhook_not_exists"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                name=arg2
            )
        else:
            await conn.execute("DELETE FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=arg2))
            em.description = locale[lang]["other_webhook_success_delete"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                name=arg2
            )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "shop":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        logg.info("remove arg2 = {arg2}".format(arg2=arg2))
        role = discord.utils.get(message.server.roles, name=arg2)
        if not role:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            role = discord.utils.get(message.server.roles, id=arg2)
        if not role:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'shop' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=role.id))
        if not dat:
            em.description = locale[lang]["other_shop_not_exists"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                role_id=role.id
            )
        else:
            await conn.execute("DELETE FROM mods WHERE type = 'shop' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=role.id))
            em.description = locale[lang]["other_shop_success_delete"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                role_id=role.id
            )
        await client.send_message(message.channel, embed=em)
        return


    if not arg1:
        em.description = locale[lang]["other_missed_argument"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            arg="category"
        )
        await client.send_message(message.channel, embed=em)
        return

    em.description = locale[lang]["other_incorrect_argument"].format(
        who=message.author.display_name+"#"+message.author.discriminator,
        arg="category"
    )
    await client.send_message(message.channel, embed=em)
    return
