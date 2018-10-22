import discord
import asyncio
import requests
import time
from datetime import datetime, date
import string
import random
import copy
import os
import re
import json
import asyncpg
from discord.ext import commands
from cogs.const import *
from cogs.ids import *
from cogs.locale import *


async def c_createclan(client, conn, context):
    message = context.message
    server_id = message.server.id
    try:
        await client.delete_message(message)
    except:
        pass
