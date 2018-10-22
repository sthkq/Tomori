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
import imghdr
import os
from PIL import Image, ImageChops, ImageFont, ImageDraw, ImageSequence, ImageFilter
from PIL.GifImagePlugin import getheader, getdata
from functools import partial
import aiohttp
from io import BytesIO
from typing import Union
from discord.ext import commands
from config.settings import settings
from cogs.locale import *
from cogs.const import *
from cogs.ids import *



mask = Image.new('L', (1002, 1002), 0)
draws = ImageDraw.Draw(mask)
draws.ellipse((471, 5) + (531, 35), fill=255)
draws.ellipse((471, 967) + (531, 997), fill=255)
draws.ellipse((5, 471) + (35, 531), fill=255)
draws.ellipse((967, 471) + (997, 531), fill=255)
draws.polygon([(531, 15), (471, 15), (15, 471), (15, 531), (471, 987), (531, 987), (987, 531), (987, 471)], fill=255)
mask = mask.resize((343, 343), Image.ANTIALIAS)


global voice_clients
voice_clients = []


async def u_voice_state_update(client, conn, logger, before, after):
    ret = '---------[voice_state_update]:{0.server.name} | {0.server.id}\n'.format(before)
    if before.voice.voice_channel:
        ret += 'before - {0.name} | {0.id} -> {0.voice.voice_channel.name} | {0.voice.voice_channel.id}\n'.format(before)
    if after.voice.voice_channel:
        ret += 'after - {0.name} | {0.id} -> {0.voice.voice_channel.name} | {0.voice.voice_channel.id}\n'.format(after)
    logger.info(ret)
    if before.bot:
        return
    const = await conn.fetchrow("SELECT create_lobby_id, em_color FROM settings WHERE discord_id = '{}'".format(before.server.id))
    if not const:
        logger.error('Сервер {0.name} | {0.id} отсутствует в базе! User - {1.name} | {1.id}\n'.format(before.server, before))
        return
    if not const[0]:
        return
    em = discord.Embed(colour=int(const[1], 16) + int("0x200", 16))
    global voice_clients
    if before.voice.voice_channel and before.voice.voice_channel != after.voice.voice_channel:
        if before.id in voice_clients:
            voice_clients.pop(voice_clients.index(before.id))
        dat = await conn.fetchrow("SELECT voice_channel_id FROM users WHERE discord_id = '{0.id}'".format(before))
        if dat:
            if before.voice.voice_channel.id == dat[0]:
                await conn.execute("UPDATE users SET voice_channel_id = Null WHERE discord_id = '{0.id}'".format(before))
                try:
                    await client.delete_channel(before.voice.voice_channel)
                except:
                    logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал пользователя. User - {1.name} | {1.id}\n'.format(before.server, before))
                    em.description = '{}, не удалось удалить канал пользователя. Свяжитесь с администратором сервера.'.format(clear_name(before.display_name[:50]))
                    await client.send_message(before, embed=em)
    if after.voice.voice_channel and after.voice.voice_channel.id == const[0]:
        if before.id in voice_clients:
            return
        voice_clients.append(before.id)
        try:
            for_everyone = discord.ChannelPermissions(target=after.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=True))
            for_after = discord.ChannelPermissions(target=after, overwrite=discord.PermissionOverwrite(create_instant_invite=True, manage_roles=False, read_messages=True, manage_channels=True, connect=True, speak=True, mute_members=False, deafen_members=False, use_voice_activation=True, move_members=False))
            private = await client.create_channel(after.server, "{name}".format(name=clear_name(after.display_name[:50])), for_everyone, for_after, type=discord.ChannelType.voice)
            await client.edit_channel(private, user_limit=2)
            await client.move_channel(private,  0)
            dat = await conn.fetchrow("SELECT name FROM users WHERE discord_id = '{0.id}'".format(before))
            if dat:
                await conn.execute("UPDATE users SET voice_channel_id = '{0}' WHERE discord_id = '{1.id}'".format(private.id, before))
            else:
                await conn.execute("INSERT INTO users(name, discord_id, discriminator, voice_channel_id, background) VALUES('{}', '{}', '{}', '{}')".format(before.name, before.id, before.discriminator, private.id, random.choice(background_list)))
        except:
            logger.error('Сервер {0.name} | {0.id}. Не удалось создать канал. User - {1.name} | {1.id}\n'.format(before.server, before))
            em.description = '{}, не удалось создать канал. Свяжитесь с администратором сервера.'.format(clear_name(before.display_name[:50]))
            await client.send_message(before, embed=em)
            return
        try:
            await client.move_member(after, private)
        except:
            try:
                await client.delete_channel(private)
            except:
                logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал {1.name} | {1.id}. User - {2.name} | {1.id}\n'.format(before.server, private, before))
            logger.error('Сервер {0.name} | {0.id}. Не удалось переместить пользователя. User - {1.name} | {1.id}\n'.format(before.server, before))
            em.description = '{}, не удалось переместить Вас в Ваш канал. Свяжитесь с администратором сервера.'.format(clear_name(before.display_name[:50]))
            await client.send_message(before, embed=em)
            return

async def u_createvoice(client, conn, logger, context):
    message = context.message
    server_id = message.server.id
    who = message.author
    const = await conn.fetchrow("SELECT em_color, is_createvoice, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not const or not const[1]:
        await send_command_error(message, lang)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    try:
        await client.delete_message(message)
    except:
        pass
    if not who.voice.voice_channel:
        logger.error('Сервер {0.name} | {0.id}. Пользователь не в войсе. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, для начала зайдите в голосовой канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(who, embed=em)
        return
    try:
        private = await client.create_channel(who.server, "private - {}".format(clear_name(who.display_name[:50])), type=discord.ChannelType.voice)
        await client.edit_channel_permissions(private, target=who.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False))
        await client.edit_channel_permissions(private, target=who, overwrite=discord.PermissionOverwrite(create_instant_invite=True, manage_roles=True, read_messages=True, manage_channels=True, connect=True, speak=True, mute_members=True, deafen_members=True, use_voice_activation=True, move_members=True))
        dat = await conn.fetchrow("SELECT name FROM users WHERE discord_id = '{0.id}'".format(who))
        if dat:
            await conn.execute("UPDATE users SET voice_channel_id = '{0}' WHERE discord_id = '{1.id}'".format(private.id, who))
        else:
            await conn.execute("INSERT INTO users(name, discord_id, discriminator, voice_channel_id, background) VALUES('{}', '{}', '{}', '{}')".format(who.name, who.id, who.discriminator, private.id, random.choice(background_list)))
    except:
        logger.error('Сервер {0.name} | {0.id}. Не удалось создать канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось создать канал. Свяжитесь с администратором сервера.'.format(clear_name(who.display_name[:50]))
        await client.send_message(who, embed=em)
        return
    try:
        await client.move_member(who, private)
    except:
        try:
            await client.delete_channel(private)
        except:
            logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал {1.name} | {1.id}. User - {2.name} | {1.id}\n'.format(who.server, private, who))
        logger.error('Сервер {0.name} | {0.id}. Не удалось переместить пользователя. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось переместить Вас в Ваш канал. Свяжитесь с администратором сервера.'.format(clear_name(who.display_name[:50]))
        await client.send_message(who, embed=em)
        return

async def u_setvoice(client, conn, logger, context):
    message = context.message
    server_id = message.server.id
    who = message.author
    const = await conn.fetchrow("SELECT em_color, is_createvoice, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not const or not const[1]:
        await send_command_error(message, lang)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    try:
        await client.delete_message(message)
    except:
        pass
    if not who.voice.voice_channel:
        logger.error('Сервер {0.name} | {0.id}. Пользователь не в войсе. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, для начала зайдите в голосовой канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await conn.execute("UPDATE settings SET create_lobby_id = '{}' WHERE discord_id = '{}'".format(who.voice.voice_channel.id, server_id))
        logger.error('Сервер {0.name} | {0.id}. Установлен войс канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, войс для лобби установлен.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    except:
        logger.error('Сервер {0.name} | {0.id}. Не удалось установить канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось установить канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return

async def u_setlobby(client, conn, logger, context):
    message = context.message
    server_id = message.server.id
    who = message.author
    const = await conn.fetchrow("SELECT em_color, is_createvoice, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not const or not const[1]:
        await send_command_error(message, lang)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    try:
        await client.delete_message(message)
    except:
        pass
    if not who.voice.voice_channel:
        logger.error('Сервер {0.name} | {0.id}. Пользователь не в войсе. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, для начала зайдите в голосовой канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.edit_channel_permissions(who.voice.voice_channel, target=who.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=True, move_members=True))
        logger.error('Сервер {0.name} | {0.id}. Установлен войс лобби. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, войс для ожидания лобби установлен.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    except:
        logger.error('Сервер {0.name} | {0.id}. Не удалось установить канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось установить канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return

async def u_news(client, conn, context, message_id):
    server_count = 0
    message = context.message
    channel_from = message.channel
    em = discord.Embed(colour=0xC5934B)
    try:
        await client.delete_message(message)
    except:
        pass
    try:
        message_from = await client.get_message(channel_from, message_id)
        content = message_from.content
        if not content:
            em.description = "Некорректное сообщение."
            em.set_footer(text="Время ответа - {}ms".format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
            await client.send_message(channel_from, embed=em)
            return
        servers_ids = await conn.fetch("SELECT discord_id FROM settings WHERE is_news = True")
        if servers_ids:
            for server_id in servers_ids:
                server = client.get_server(server_id)
                for channel in server.channels:
                    if channel.name.lower() == "tomori news":
                        await client.send_message(channel, content)
                        server_count += 1
                        break
                else:
                    channel = await client.create_channel(server, "Tomori News")
                    await client.send_message(channel, content)
                    server_count += 1
    except:
        em.description = "Некорректный id."
        em.set_footer(text="Время ответа - {}ms".format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
        await client.send_message(channel_from, embed=em)
    em.description = "Успешно отправлено на {} серверов!".format(server_count)
    em.set_footer(text="Время ответа - {}ms".format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
    await client.send_message(channel_from, embed=em)
    await client.send_message(channel_from, "Успешно отправлено на {} серверов!".format(server_count))

async def u_reaction_add(client, conn, logger, data):
    emoji = data.get("emoji")
    user_id = data.get("user_id")
    message_id = data.get("message_id")
    server_id = data.get("guild_id")
    server = client.get_server(server_id)
    user = server.get_member(user_id)
    data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'reaction' AND name = '{name}'".format(
        server_id=server.id,
        name=message_id
    ))
    roles = []
    for role in user.roles:
        if not any(role.id==dat["value"] for dat in data):
            roles.append(role)
    for react in data:
        if not react["condition"] == emoji['name']:
            continue
        role = discord.utils.get(server.roles, id=react["value"])
        if role and not role in roles:
            roles.append(role)
    await client.replace_roles(user, *roles)

async def u_reaction_remove(client, conn, logger, data):
    emoji = data.get("emoji")
    user_id = data.get("user_id")
    message_id = data.get("message_id")
    server_id = data.get("guild_id")
    server = client.get_server(server_id)
    user = server.get_member(user_id)
    data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'reaction' AND name = '{name}'".format(
        server_id=server.id,
        name=message_id,
        condition=emoji["name"]
    ))
    roles = []
    for react in data:
        if not react["condition"] == emoji['name']:
            continue
        role = discord.utils.get(server.roles, id=react["value"])
        if not role:
            logger.error("doesn't exists role id - {id}".format(id=react["value"]))
        else:
            roles.append(role)
    if roles:
        await client.remove_roles(user, *roles)

async def u_check_message(client, conn, logger, message):
    for file in black_filename_list:
        if file.lower() in str(message.attachments).lower() or file.lower() in message.content.lower():
            logger.error("file detected (suck my dick enot) - ({})  <-> {}\n".format(file, message.attachments))
            try:
                dat = await conn.fetchrow("SELECT name FROM black_list WHERE server_id = '{}' AND discord_id = '{}'".format(message.server, message.author.id))
                if dat:
                    if not dat[0]:
                        await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(message.author))
                else:
                    await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(message.author))
                    pass
                await client.delete_message(message)
                return True
            except:
                pass
    return False
    await u_check_ddos(client, conn, logger, member)

async def u_check_ddos(client, conn, logger, member):
    dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    if dat:
        try:
            #logger.error("================================================================================\n**{2}**\n({0.name} | {0.mention}) -> [{1.name} | {1.id}]\n".format(member, member.server, time.ctime(time.time())))
            try:
                await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) -> [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
                await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
                await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
            except:
                pass
            if not dat[0]:
                await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
            await client.ban(member)
            return True
        except:
            pass
            await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) != [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
            # await client.send_message(member.server.owner, "**{1}**\n``Не удалось кикнуть ({0.name} | {0.mention}) с твоего сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori((``".format(member, time.ctime(time.time())))
        return True
    # if (datetime.utcnow() - member.created_at).days == 0:
    #     dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    #     if dat:
    #         if not dat[0]:
    #             await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
    #     else:
    #         await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(member))
    #     try:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) кикнут потому что сегодня создан акк [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #         await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
    #         await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
    #         await client.kick(member)
    #     except:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) не кикнут [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #     return True
    # if len(member.game.name.lower()) >= 30:# or (datetime.utcnow() - member.created_at).days == 0:
    #     dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    #     if dat:
    #         if not dat[0]:
    #             await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
    #     else:
    #         await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(member))
    #     try:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) status> [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #         await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
    #         #await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
    #         await client.kick(member)
    #     except:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) !status [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #     return True
    # for compare in ddos_name_list:
    #     if compare.lower() in member.name.lower():# or (datetime.utcnow() - member.created_at).days == 0:
    #         dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    #         if dat:
    #             if not dat[0]:
    #                 await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
    #         else:
    #             await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(member))
    #         try:
    #             await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) +> [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #             await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
    #             #await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
    #             await client.ban(member)
    #         except:
    #             await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) !- [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #         return True
    return False


async def u_check_travelling(client, member):
    server_id = travelling_servers.get(member.server.id)
    if not server_id:
        return
    server = client.get_server(server_id)
    if not server:
        return
    user = server.get_member(member.id)
    if not user:
        return
    roles = user.roles
    _roles = member.server.roles
    added_roles = []
    for role in roles:
        _role = discord.utils.get(
            _roles,
            name=role.name,
            permissions=role.permissions,
            colour=role.colour,
            hoist=role.hoist,
            mentionable=role.mentionable
        )
        if _role:
            added_roles.append(_role)
    if added_roles:
        await client.add_roles(member, *added_roles)
    #await client.kick(user)

async def u_clone_roles(client, conn, context, server_id):
    message = context.message
    server = client.get_server(server_id)
    if not server:
        return
    try:
        await client.delete_message(message)
    except:
        pass
    roles = message.server.roles
    roles = sorted(roles,key=lambda role: role.position, reverse=True)
    for role in roles:
        try:
            await client.create_role(
                server,
                name=role.name,
                permissions=role.permissions,
                colour=role.colour,
                hoist=role.hoist,
                mentionable=role.mentionable
            )
        except:
            pass



async def u_invite_to_server(client, server_id):
    server = client.get_server(server_id)
    if not server:
        return None
    try:
        invites = await client.invites_from(server)
        for invite in invites:
            if invite.max_age == 0 and invite.max_uses == 0:
                return invite.url
        return invites[0].url
    except:
        pass
    try:
        invite = await client.create_invite(server, max_age=0, max_uses=0)
        return invite.url
    except:
        pass
    for channel in server.channels:
        try:
            invite = await client.create_invite(channel, max_age=0, max_uses=0)
            if not invite.url:
                continue
            return invite.url
        except:
            pass
    else:
        return None

async def u_check_invite(client, url):
    try:
        invite = await client.get_invite(url)
        return True
    except:
        return False

async def u_invite_server(client, conn, context, server_id):
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    server = client.get_server(server_id)
    if not server:
        em.description = "Сервер (ID:{id}) - не существует.".format(id=server_id)
        await client.send_message(message.channel, embed=em)
        return
    try:
        invites = await client.invites_from(server)
        for invite in invites:
            if invite.max_age == 0 and invite.max_uses == 0:
                em.description = "Сервер (ID:{id}) one of invites:\n{invite}".format(id=server_id, invite=invite.url)
                await client.send_message(message.channel, embed=em)
                return
        em.description = "Сервер (ID:{id}) first of invites:\n{invite}".format(id=server_id, invite=invites[0].url)
        await client.send_message(message.channel, embed=em)
        return
    except:
        pass
    try:
        invite = await client.create_invite(server, max_age=0, max_uses=1)
        em.description = "Сервер (ID:{id}) invite created:\n{invite}".format(id=server_id, invite=invite.url)
        await client.send_message(message.channel, embed=em)
        return
    except:
        pass
    for channel in server.channels:
        try:
            invite = await client.create_invite(channel, max_age=0, max_uses=1)
            if not invite.url:
                continue
            em.description = "Сервер (ID:{id}) invite to channel {channel_name}:\n{invite}".format(id=server_id, invite=invite.url, channel_name=channel.name)
            await client.send_message(message.channel, embed=em)
            return
        except:
            pass
    else:
        em.description = "Сервер (ID:{id}) - не удалось создать инвайт ни в один канал.".format(id=server_id)
        await client.send_message(message.channel, embed=em)
        return

async def u_invite_channel(client, conn, context, channel_id):
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    channel = client.get_channel(channel_id)
    if not channel:
        em.description = "Channel (ID:{id}) - не существует.".format(id=channel_id)
        await client.send_message(message.channel, embed=em)
        return
    try:
        invite = await client.create_invite(channel, max_age=0, max_uses=0)
        em.description = "Channel (ID:{id}) invite to channel {channel_name}:\n{invite}".format(id=channel_id, invite=invite.url, channel_name=channel.name)
        await client.send_message(message.channel, embed=em)
        return
    except:
        em.description = "Channel (ID:{id}) - не удалось создать инвайт в канал.".format(id=channel_id)
        await client.send_message(message.channel, embed=em)
        return

def u_get_channel(client, channel_id):
    channel = client.get_channel(channel_id)
    if not channel:
        for server in client.servers:
            channel = server.get_member(channel_id)
            if channel:
                break
    return channel

async def u_check_support(client, conn, logger, message):
    channel = message.channel
    if channel.is_private:
        chan_id = channel.user.id
    else:
        chan_id = channel.id

    travel_to = travelling_message_servers.get(message.server.id)
    if travel_to and message.author.id != client.user.id and not message.author.bot:
        travel_server_to = client.get_server(travel_to)
        if travel_server_to:
            travel_channel_to = discord.utils.get(
                travel_server_to.channels,
                name=channel.name,
                type=channel.type
                # topic=channel.topic
            )
            if travel_channel_to:
                em = discord.Embed(colour=0xC5934B)
                em.description = message.content
                icon_url = message.author.avatar_url
                if not icon_url:
                    icon_url = message.author.default_avatar_url
                em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=icon_url)
                em.set_footer(text="Отправлено с сервера "+message.server.name)
                await client.send_message(travel_channel_to, embed=em)

    dat = await conn.fetchrow("SELECT * FROM tickets WHERE request_id = '{request_id}' OR response_id = '{response_id}'".format(request_id=chan_id, response_id=chan_id))
    if not dat:
        if channel.is_private and message.content:
            content = message.content
            dialogflow = apiai.ApiAI(settings["dialogflow_token"]).text_request()
            dialogflow.lang = 'ru'
            dialogflow.session_id = 'BatlabAIBot'
            dialogflow.query = content # Посылаем запрос к ИИ с сообщением от юзера
            responseJson = json.loads(dialogflow.getresponse().read().decode('utf-8'))
            response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
            # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
            try:
                if response:
                    # if message.server.id == '475425777215864833':
                    #     response = "<@!480694830721269761> " + response
                    await client.send_message(message.author, response)
                else:
                    await client.send_message(message.author, locale[lang]["support_idu"].format(mention=message.author.mention))
            except:
                pass
        return

    request_channel = u_get_channel(client, dat["request_id"])
    response_channel_id = dat["response_id"]
    if not message.author.bot and request_channel and not message.content == "" and not message.content == "!stop":
        em = discord.Embed(colour=0xC5934B)
        em.description = message.content
        if not channel.is_private:
            if channel.id == response_channel_id:
                index = 0
                name = None
                for s in support_list:
                    index += 1
                    if s == message.author.id:
                        name = "Tomori Support#000{tag} ✔".format(tag=index)
                        icon_url = client.user.avatar_url
                        break
                if dat["name"]:
                    name = "{name}#{tag}".format(name=dat["name"], tag=message.author.discriminator)
                    icon_url = message.server.icon_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                if not name:
                    name = "{name}#{tag}".format(name=message.author.name, tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                em.set_author(name=name, icon_url=icon_url)
                await client.send_message(request_channel, embed=em)
            elif channel.id == request_channel.id:
                em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                em.set_footer(text="ID: {id} • Mention: {mention}".format(
                    id=message.author.id,
                    mention=message.author.mention
                ))
                await client.send_message(u_get_channel(client, response_channel_id), embed=em)
        else:
            if channel.user.id == request_channel.id:
                em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                em.set_footer(text="ID: {id} • Mention: {mention}".format(
                    id=message.author.id,
                    mention=message.author.mention
                ))
                await client.send_message(u_get_channel(client, response_channel_id), embed=em)
            elif channel.user.id == response_channel_id:
                index = 0
                name = None
                for s in support_list:
                    index += 1
                    if s == message.author.id:
                        name = "Tomori Support#000{tag} ✔".format(tag=index)
                        icon_url = client.user.avatar_url
                        if not icon_url:
                            icon_url = message.author.default_avatar_url
                        break
                if dat["name"]:
                    name = "{name}#{tag}".format(name=dat["name"], tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                if not name:
                    name = "{name}#{tag}".format(name=message.author.name, tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                em.set_author(name=name, icon_url=icon_url)
                await client.send_message(request_channel, embed=em)




async def u_check_lvlup(client, conn, channel, who, const, xp):
    lang = const["locale"]
    if not lang in locale.keys():
        return
    lvl = xp_lvlup_list[xp]
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.description = locale[lang]["lvlup"].format(
        who=who.mention,
        lvl=lvl
    )
    data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'lvlup'".format(
        server_id=who.server.id
    ))
    roles = []
    is_new_role = False
    roles_mention = ""
    for role in who.roles:
        if not any(role.id==dat["value"] for dat in data):
            roles.append(role)
    for dat in data:
        if not dat["condition"] == str(lvl):
            continue
        role = discord.utils.get(who.server.roles, id=dat["value"])
        if role and not role in roles:
            is_new_role = True
            roles_mention += role.mention+", "
            roles.append(role)
    if is_new_role:
        em.description += locale[lang]["lvlup_continue"].format(role=roles_mention[:-2])
        await client.replace_roles(who, *roles)
    if not who.server.id in konoha_servers:
        em.set_image(url=lvlup_image_url)
    else:
        em.set_image(url=lvlup_image_konoha_url)
    try:
        msg = await client.send_message(channel, embed=em)
        await asyncio.sleep(25)
        await client.delete_message(msg)
    except:
        pass


def welcomer_format(text, member):
    server = member.server
    return text.format(
        name=member.name,
        mention=member.mention,
        server=server.name,
        count=server.member_count
    )[:2000]

async def send_welcome_pic(client, channel, user, const):
    await client.send_typing(channel)

    color = json.loads(const["welcome_text_color"])

    back = Image.open("cogs/stat/backgrounds/welcome/{}.png".format(const["welcome_back"]))
    draw = ImageDraw.Draw(back)
    under = Image.open("cogs/stat/backgrounds/welcome/under_{}.png".format(const["welcome_under"]))

    text_welcome = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", 50)
    text_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", 50)

    text_welcome = u"{}".format("WELCOME")
    welcome_size = 1
    font_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", welcome_size)
    while font_name.getsize(text_welcome)[0] < 500:
        welcome_size += 1
        font_welcome = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", welcome_size)
        if welcome_size == 71:
            break
    welcome_size -= 1
    font_welcome = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", welcome_size)

    text_name = u"{}".format(user.display_name+"#"+user.discriminator)
    name_size = 1
    font_name = ImageFont.truetype("cogs/stat/ProximaNova-Regular.otf", name_size)
    while font_name.getsize(text_name)[0] < 500:
        name_size += 1
        font_name = ImageFont.truetype("cogs/stat/ProximaNova-Regular.otf", name_size)
        if name_size == 36:
            break
    name_size -= 1
    font_name = ImageFont.truetype("cogs/stat/ProximaNova-Regular.otf", name_size)

    ava_url = user.avatar_url
    if not ava_url:
        ava_url = user.default_avatar_url
    response = requests.get(ava_url)
    avatar = Image.open(BytesIO(response.content))
    avatar = avatar.resize((343, 343))
    avatar.putalpha(mask)
    back.paste(under, (0, 0), under)
    back.paste(avatar, (29, 29), avatar)

    draw.text(
        (435, 120),
        text_welcome,
        (color[0], color[1], color[2]),
        font=font_welcome
    )
    draw.text(
        (435, 230),
        text_name,
        (color[0], color[1], color[2]),
        font=font_name
    )

    filename = 'cogs/stat/return/welcome/{}.png'.format(user.server.id+'_'+user.id)
    back.save(filename)
    content=None
    if const["welcome_text"]:
        content = welcomer_format(const["welcome_text"], user)
    await client.send_file(channel, filename, content=content)
    os.remove(filename)
    return

async def tomori_log_ban(client, member):
    c_ban = discord.Embed(colour=0xF10118)
    c_ban.set_author(name="Ban user", icon_url=member.server.icon_url)
    c_ban.add_field(
        name="User",
        value=member.display_name+"#"+member.discriminator,
        inline=True
    )
    c_ban.add_field(
        name="Mention",
        value=member.mention,
        inline=True
    )
    c_ban.add_field(
        name="Server",
        value=member.server.name+"\n"+member.server.id,
        inline=True
    )
    c_ban.add_field(
        name="Reason",
        value="'Event references'",
        inline=True
    )
    ava_url = member.avatar_url
    if not ava_url:
        ava_url = member.default_avatar_url
    c_ban.set_thumbnail(url=ava_url)
    c_ban.set_footer(text="ID: {0.id} • {1}".format(member, time.ctime(time.time())))
    await client.send_message(client.get_channel(tomori_event_channel), embed=c_ban)

async def tomori_log_unban(client, server, member):
    c_ban = discord.Embed(colour=0xF10118)
    c_ban.set_author(name="Unban user", icon_url=server.icon_url)
    c_ban.add_field(
        name="User",
        value=member.name+"#"+member.discriminator,
        inline=True
    )
    c_ban.add_field(
        name="Mention",
        value=member.mention,
        inline=True
    )
    c_ban.add_field(
        name="Server",
        value=server.name+"\n"+server.id,
        inline=True
    )
    c_ban.add_field(
        name="Reason",
        value="'Event references'",
        inline=True
    )
    ava_url = member.avatar_url
    if not ava_url:
        ava_url = member.default_avatar_url
    c_ban.set_thumbnail(url=ava_url)
    c_ban.set_footer(text="ID: {0.id} • {1}".format(member, time.ctime(time.time())))
    await client.send_message(client.get_channel(tomori_event_channel), embed=c_ban)

# async def u_check_achievements(client, conn, const, message, key):
#     lang = const["locale"]
#     if not lang in locale.keys():
#         return
#     em = discord.Embed(colour=int(const["em_color"], 16) + 512)
#     em.description = locale[lang]["lvlup"].format(
#         who=who.mention,
#         lvl=xp_lvlup_list[xp]
#     )
#     em.set_image(url=lvlup_image_url)
#     try:
#         msg = await client.send_message(channel, embed=em)
#         await asyncio.sleep(25)
#         await client.delete_message(msg)
#     except:
#         pass
