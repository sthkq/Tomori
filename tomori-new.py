import discord
import asyncio
import requests
import logging
import time
from datetime import datetime, date
import string
import random
import copy
import json
import asyncpg
import copy
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
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
global client
client = None
async def get_prefixes():
    global client
    client = commands.Bot(command_prefix="!", shard_count=10)
    #bot = commands.Bot(command_prefix=prefix_list, shard_count=10)
    client.remove_command('help')

async def run_base():
    global conn
    try:
        conn = await asyncpg.create_pool(dsn="postgres://{user}:{password}@{host}:5432/{database}".format(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"]), command_timeout=60)
        logger.info('PostgreSQL was successfully loaded.')
    except:
        logger.error('PostgreSQL doesn\'t load.')
        exit(0)
    #await init_locale(conn, bot)


loop.run_until_complete(get_prefixes())
loop.run_until_complete(run_base())

@client.event
async def on_command_error(error, ctx):
    pass





class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        parsed_path = urlparse.urlparse(self.path)
        request_id = parsed_path.path
        response = subprocess.check_output(["python", request_id])
        logger.info(json.dumps(response))

    def do_POST(self):
        self._set_headers()
        parsed_path = urlparse.urlparse(self.path)
        request_id = parsed_path.path
        response = subprocess.check_output(["python", request_id])
        logger.info(json.dumps(response))

    def do_HEAD(self):
        self._set_headers()

def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('51.38.113.96', port)
    httpd = server_class(server_address, handler_class)
    logger.info('Starting httpd...')
    httpd.serve_forever()


@client.event
async def on_ready():
    logger.info("Logged in as | who - {} | id - {}\n".format(client.user.display_name, client.user.id))
    run()

client.run(settings["token"])
