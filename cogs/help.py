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

help_responses = {
    "english" : {
        "command" : "Command `{command}`",
        "usage" : "**Usage:**\n",
        "rights" : "**Rights:**\nНеобходимы права __**Администратора**__",
        "command_not_found" : "Command not found!",
        "help" : {
            "description" : "Show command list",
            "usage" : "`{prefix}help` - command list\n`{prefix}help [command]` - show info about __command__",
            "rights" : False
        },
        "set" : {
            "description" : "Change server settings",
            "usage" : "`{prefix}set [category]]`\n" + \
                "Also you can write `{prefix}set list` for a list of settings" + \
                    "All possible settings you can see on the [website](https://discord.band/commands#/ADMIN)",
            "list_desctiption" : "List of settings",
            "rights" : True
        },
        "timely" : {
            "description" : "Cобрать печенюхи",
            "usage" : "`{prefix}timely` - получить ежедневную выплату",
            "rights" : False
        },
        "work" : {
            "description" : "Выйти на работу",
            "usage" : "`{prefix}work`",
            "rights" : False
        },
        "server" : {
            "description" : "Показать информацию о сервере",
            "usage" : "`{prefix}server`",
            "rights" : False
        },
        "ping" : {
            "description" : "Проверить задержку соединения",
            "usage" : "`{prefix}ping`",
            "rights" : False
        },
        "createvoice" : {
            "description" : "Создать приватный голосовой канал",
            "usage" : "`{prefix}createvoice`",
            "rights" : False
        },
        "setvoice" : {
            "description" : "Установить голосовой канал",
            "usage" : "`{prefix}setvoice`",
            "rights" : False
        },
        "setlobby" : {
            "description" : "Установить голосовой для ожидания",
            "usage" : "`{prefix}setlobby`",
            "rights" : False
        },
        "buy" : {
            "description" : "Купить роль",
            "usage" : "`{prefix}buy [название роли]`",
            "rights" : False
        },
        "shop" : {
            "description" : "Показать магазин ролей",
            "usage" : "`{prefix}shop`\n`{prefix}shop [страница]`",
            "rights" : False
        },
        "pay" : {
            "description" : "Получить __печенюхи__ из банка сервера",
            "usage" : "`{prefix}pay [кол-во]`",
            "rights" : True
        },
        "send" : {
            "description" : "Переслать __файл__ от имени бота",
            "usage" : "Отправить `{prefix}send` вместе с файлом",
            "rights" : True
        },
        "say" : {
            "description" : "Напишет __текст__ от имени бота",
            "usage" : "`{prefix}say [текст]`",
            "rights" : True
        },
        "песель" : {
            "description" : "песель песель песель песель песель",
            "usage" : "`{prefix}песель [песель]`",
            "rights" : False
        },
        "report" : {
            "description" : "Отправить репорт",
            "usage" : "`{prefix}report [текст]`",
            "rights" : False
        },
        "give" : {
            "description" : "Передать свои печенюхи",
            "usage" : "`{prefix}give [кому] [кол-во]`",
            "rights" : False
        },
        "top" : {
            "description" : "Показать топ юзеров",
            "usage" : "`{prefix}report`\n`{prefix}report [страница]`",
            "rights" : False
        },
        "remove" : {
            "description" : "Сбросить настройку",
            "usage" : "`{prefix}remove [параметр]`\n`{prefix}rm [параметр]`\n`{prefix}remove [параметр]`\n`{prefix}remove [параметр] [параметр]`\n`{prefix}remove [параметр] [параметр] [параметр]`",
            "rights" : True
        },
        "backgrounds" : {
            "description" : "Показать список фонов",
            "usage" : "`{prefix}backgrounds`\n`{prefix}backs`\n`{prefix}backgrounds [страница]`",
            "rights" : False
        },
        "$" : {
            "description" : "Посмотреть свой баланс",
            "usage" : "`{prefix}$`",
            "rights" : False
        },
        "sex" : {
            "description" : "Трахнуть",
            "usage" : "`{prefix}sex [кто]`",
            "rights" : False
        },
        "hug" : {
            "description" : "Обнять",
            "usage" : "`{prefix}hug [кто]`",
            "rights" : False
        },
        "wink" : {
            "description" : "Подмигнуть",
            "usage" : "`{prefix}wink [кто]`",
            "rights" : False
        },
        "five" : {
            "description" : "Дать пять",
            "usage" : "`{prefix}five [кто]`",
            "rights" : False
        },
        "fuck" : {
            "description" : "Показать фак",
            "usage" : "`{prefix}fuck [кто]`",
            "rights" : False
        },
        "punch" : {
            "description" : "Дать леща",
            "usage" : "`{prefix}punch [кто]`",
            "rights" : False
        },
        "kiss" : {
            "description" : "Поцеловать",
            "usage" : "`{prefix}kiss [кто]`",
            "rights" : False
        },
        "drink" : {
            "description" : "Уйти в запой",
            "usage" : "`{prefix}drink [кто]`",
            "rights" : False
        },
        "shiki" : {
            "description" : "Найти аниме на Shikimori",
            "usage" : "`{prefix}shiki [название]`",
            "rights" : False
        },
        "google" : {
            "description" : "Найти что-то в гугле",
            "usage" : "`{prefix}google [запрос]`",
            "rights" : False
        },
        "br" : {
            "description" : "Поставить деньги на рулетке",
            "usage" : "`{prefix}br [кол-во]`\n`{prefix}roll [кол-во]`",
            "rights" : False
        },
        "slots" : {
            "description" : "Поставить деньги на рулетке",
            "usage" : "`{prefix}slots [кол-во]`\n`{prefix}slot [кол-во]`",
            "rights" : False
        },
        "rep" : {
            "description" : "Выразить свое почтение",
            "usage" : "`{prefix}rep [кто]`",
            "rights" : False
        },
        "avatar" : {
            "description" : "Показать аватар пользователя",
            "usage" : "`{prefix}avatar [кто]`",
            "rights" : False
        },
        "me" : {
            "description" : "Вывести статистику пользователя картинкой",
            "usage" : "`{prefix}me [кто]`",
            "rights" : False
        },
        "about" : {
            "description" : "Показать информацию о боте",
            "usage" : "`{prefix}about`",
            "rights" : False
        },
        "invite" : {
            "description" : "Получить ссылку на добавление бота себе на сервер",
            "usage" : "`{prefix}invite`",
            "rights" : False
        },
    },
    "russian" : {
        "command" : "Команда `{command}`",
        "usage" : "**Пример:**\n",
        "rights" : "**Права:**\nНеобходимы права __**Администратора**__",
        "command_not_found" : "Команда не найдена!",
        "help" : {
            "description" : "Показать список команд",
            "usage" : "`{prefix}help` - список команд\n`{prefix}help [команда]` - выводит информацию о __команде__",
            "rights" : False
        },
        "set" : {
            "description" : "Изменить параметры сервера",
            "usage" : "`{prefix}set [category]]`\n" + \
                "Также вы можете получить весь список настроек с помощью команды `{prefix}help set list`",
            "list_desctiption" : "Список всех настроек",
            "rights" : True
        },
        "timely" : {
            "description" : "Cобрать печенюхи",
            "usage" : "`{prefix}timely` - получить ежедневную выплату",
            "rights" : False
        },
        "work" : {
            "description" : "Выйти на работу",
            "usage" : "`{prefix}work`",
            "rights" : False
        },
        "server" : {
            "description" : "Показать информацию о сервере",
            "usage" : "`{prefix}server`",
            "rights" : False
        },
        "ping" : {
            "description" : "Проверить задержку соединения",
            "usage" : "`{prefix}ping`",
            "rights" : False
        },
        "createvoice" : {
            "description" : "Создать приватный голосовой канал",
            "usage" : "`{prefix}createvoice`",
            "rights" : False
        },
        "setvoice" : {
            "description" : "Установить голосовой канал",
            "usage" : "`{prefix}setvoice`",
            "rights" : False
        },
        "setlobby" : {
            "description" : "Установить голосовой для ожидания",
            "usage" : "`{prefix}setlobby`",
            "rights" : False
        },
        "buy" : {
            "description" : "Купить роль",
            "usage" : "`{prefix}buy [название роли]`",
            "rights" : False
        },
        "shop" : {
            "description" : "Показать магазин ролей",
            "usage" : "`{prefix}shop`\n`{prefix}shop [страница]`",
            "rights" : False
        },
        "pay" : {
            "description" : "Получить __печенюхи__ из банка сервера",
            "usage" : "`{prefix}pay [кол-во]`",
            "rights" : True
        },
        "send" : {
            "description" : "Переслать __файл__ от имени бота",
            "usage" : "Отправить `{prefix}send` вместе с файлом",
            "rights" : True
        },
        "say" : {
            "description" : "Напишет __текст__ от имени бота",
            "usage" : "`{prefix}say [текст]`",
            "rights" : True
        },
        "песель" : {
            "description" : "песель песель песель песель песель",
            "usage" : "`{prefix}песель [песель]`",
            "rights" : False
        },
        "report" : {
            "description" : "Отправить репорт",
            "usage" : "`{prefix}report [текст]`",
            "rights" : False
        },
        "give" : {
            "description" : "Передать свои печенюхи",
            "usage" : "`{prefix}give [кому] [кол-во]`",
            "rights" : False
        },
        "top" : {
            "description" : "Показать топ юзеров",
            "usage" : "`{prefix}report`\n`{prefix}report [страница]`",
            "rights" : False
        },
        "remove" : {
            "description" : "Сбросить настройку",
            "usage" : "`{prefix}remove [параметр]`\n`{prefix}rm [параметр]`\n`{prefix}remove [параметр]`\n`{prefix}remove [параметр] [параметр]`\n`{prefix}remove [параметр] [параметр] [параметр]`",
            "rights" : True
        },
        "backgrounds" : {
            "description" : "Показать список фонов",
            "usage" : "`{prefix}backgrounds`\n`{prefix}backs`\n`{prefix}backgrounds [страница]`",
            "rights" : False
        },
        "$" : {
            "description" : "Посмотреть свой баланс",
            "usage" : "`{prefix}$`",
            "rights" : False
        },
        "sex" : {
            "description" : "Трахнуть",
            "usage" : "`{prefix}sex [кто]`",
            "rights" : False
        },
        "hug" : {
            "description" : "Обнять",
            "usage" : "`{prefix}hug [кто]`",
            "rights" : False
        },
        "wink" : {
            "description" : "Подмигнуть",
            "usage" : "`{prefix}wink [кто]`",
            "rights" : False
        },
        "five" : {
            "description" : "Дать пять",
            "usage" : "`{prefix}five [кто]`",
            "rights" : False
        },
        "fuck" : {
            "description" : "Показать фак",
            "usage" : "`{prefix}fuck [кто]`",
            "rights" : False
        },
        "punch" : {
            "description" : "Дать леща",
            "usage" : "`{prefix}punch [кто]`",
            "rights" : False
        },
        "kiss" : {
            "description" : "Поцеловать",
            "usage" : "`{prefix}kiss [кто]`",
            "rights" : False
        },
        "drink" : {
            "description" : "Уйти в запой",
            "usage" : "`{prefix}drink [кто]`",
            "rights" : False
        },
        "shiki" : {
            "description" : "Найти аниме на Shikimori",
            "usage" : "`{prefix}shiki [название]`",
            "rights" : False
        },
        "google" : {
            "description" : "Найти что-то в гугле",
            "usage" : "`{prefix}google [запрос]`",
            "rights" : False
        },
        "br" : {
            "description" : "Поставить деньги на рулетке",
            "usage" : "`{prefix}br [кол-во]`\n`{prefix}roll [кол-во]`",
            "rights" : False
        },
        "slots" : {
            "description" : "Поставить деньги на рулетке",
            "usage" : "`{prefix}slots [кол-во]`\n`{prefix}slot [кол-во]`",
            "rights" : False
        },
        "rep" : {
            "description" : "Выразить свое почтение",
            "usage" : "`{prefix}rep [кто]`",
            "rights" : False
        },
        "avatar" : {
            "description" : "Показать аватар пользователя",
            "usage" : "`{prefix}avatar [кто]`",
            "rights" : False
        },
        "me" : {
            "description" : "Вывести статистику пользователя картинкой",
            "usage" : "`{prefix}me [кто]`",
            "rights" : False
        },
        "about" : {
            "description" : "Показать информацию о боте",
            "usage" : "`{prefix}about`",
            "rights" : False
        },
        "invite" : {
            "description" : "Получить ссылку на добавление бота себе на сервер",
            "usage" : "`{prefix}invite`",
            "rights" : False
        }
    }
}

supported_prefixes = ('`!','?','$','t!','t?','t$','.','-','+','\\',';','>','<','~','^','=','_`')
sup_comma = "` `"
prep = sup_comma.join(supported_prefixes)

help_set_list = {
    "english" : {
        "Background" : "Change background\n\n**Usage:**\n`{prefix}set background [number/name]`",
        "Autorole" : "Set autorole when logging in to the server\n\n**Usage:**\n`{prefix}set autorole [id]`",
        "Launguage" : "Set language\nSupported Languages: `russian`, `english`, `ukrainian`\n\n**Usage:**\n `{prefix}set language [lang]`",
        "Prefix" : "Set Prefix\nSupported Prefixes: "+prep+"\n\n**Usage:**\n`{prefix}set prefix [prefix]`"
    },
    "russian" : {
        "Background" : "Change background\n\n**Usage:**\n`{prefix}set background [number/name]`",
        "Autorole" : "Set autorole when logging in to the server\n\n**Usage:**\n`{prefix}set autorole [id]`\n",
        "Launguage" : "Set language\nSupported Languages: `russian, english, ukrainian`\n\n**Usage:**\n `{prefix}set language [lang]`",
        "Prefix" : "Set Prefix\nSupported Prefixes:  "+prep+"\n\n**Usage:**\n`{prefix}set prefix [prefix]`"
    }
}



async def h_check_help(client, conn, message):
    
    server_id = message.server.id

    formatted_message = message.content.split(" ")
    command = formatted_message[1]

    const = await conn.fetchrow("SELECT locale, prefix FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[0] if const[0] in help_responses.keys() else "english" #Проверка на наличие языка в словаре, иначе Английский
    prefix = const[1]

    em = discord.Embed(color = 0xC5934B)
    em.title = help_responses[lang]["command"].format(command=command)
    em.set_footer(text="{name}#{discriminator}".format(
        name=message.author.name,
        discriminator=message.author.discriminator
    ))

    if command == "set_list":
        em.description = help_responses[lang]["set"]["list_desctiption"]
        if lang in help_set_list.keys():
            for c, d in help_set_list[lang].items():       
                em.add_field(name=c, value=d.format(prefix = prefix), inline=False)
        else:
            em.description = help_responses["english"]["command_not_found"]
        await client.send_message(message.channel, embed=em)
        return
       
    if command in help_responses[lang].keys():
        em.description = "{desc}\n\n{usage}{rights}".format(
            desc=help_responses[lang][command]["description"],
            usage=help_responses[lang]["usage"] + \
                help_responses[lang][command]["usage"].format(prefix=prefix),
            #Складываем "Usage:" и примеры использования
            rights="" if not help_responses[lang][command]["rights"] else "\n\n" + help_responses[lang]["rights"]
            #Если "rights" = True, то мы сообщаем что только администраторы могут использовать эту команду
            )
    else:
        em.description = help_responses[lang]["command_not_found"]

    await client.send_message(message.channel, embed=em)
    return
