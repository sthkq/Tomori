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
