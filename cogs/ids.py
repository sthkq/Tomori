import discord
import asyncio
import re
import logging
import json


monitoring_channels = {
	"497104731223621643": {
			"latest": "Недавно лайкнутые сервера",
			"top": "Лучшие сервера",
            "locale": "russian"
		},
	"497103000028839956": {
			"latest": "Recently liked servers",
			"top": "The best servers",
            "locale": "english"
		}
}


report_channel_id = "497413275789688833"


local_stats_servers = [
"485400595235340303",
"448022642088476673",
"502913055559254036"
]

servers_without_more_info_in_help = [
"502913055559254036"
]

servers_without_follow_us = [
"502913055559254036"
]

not_monitoring_servers = [
"491961477926748162",
"502412345046466561"
]

travelling_servers = {
    "502411911392919563": "399321490006474752" # Бар Мартышлюшка
}

tomori_event_channel = "480857367165272064"
