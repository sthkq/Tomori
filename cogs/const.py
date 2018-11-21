import discord
import asyncio
import re
import logging
import json
import random
from PIL import Image, ImageChops, ImageFont, ImageDraw, ImageSequence, ImageFilter
from PIL.GifImagePlugin import getheader, getdata
from functools import partial
import aiohttp
from io import BytesIO
from typing import Union


moon_server = {
"злиться":{
    "response":"{author} злиться на {user}. Хм... что же он(а) такого сделал(а)?",
    "is_who": "True",
    "gifs":[
            "https://cdn.discordapp.com/attachments/504948339809320960/506771700759658516/baka2.gif",
            "https://cdn.discordapp.com/attachments/504948339809320960/506771698864095262/baka1.gif",
            "https://cdn.discordapp.com/attachments/504948339809320960/506771703129440256/baka3.gif"
    ]
},
"грустить":{
    "response":"Милый котик {author} грустит...",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506772539507212288/sad1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772544414547968/sad2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772566032121858/sad4.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772577834762250/sad5.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772582272335882/sad6.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772597401321472/sad7.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773144237768714/tumblr_ou87z3uTEv1wuhq9yo1_500.gif"
    ]
},
"секс":{
    "response":"{author} Хочет заняться сексом с {user}. Сейчас будет жарко",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506773551991488522/sex1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773548870926337/sex_1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773562288504833/sex2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773569892646912/sex3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773575135657984/sex4.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773585491394570/sex6.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773594529857537/sex7.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773599877726215/sex8.gif"
    ]
},
"суицид":{
    "response":"{author} ушёл(a) в мир иной... прощай, мы будем скучать",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506774310107611136/suicide1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774311743520776/suicide2.gif"
    ]
},
"гладить":{
    "response":"{author} гладит {user}. Это так мило ^^",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506774656842465300/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774662957498389/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774662231883787/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774668913541135/5.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506775581271261184/4.gif"
    ]
},
"смущаюсь":{
    "response":"{author} ooow, Меня засмущали :с",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506775708492890112/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506775700842348544/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506775695263924224/1.gif"
    ]
},
"кусь":{
    "response":"Кусь! {author} укусил(a) {user}",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506776383175786506/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506776387022225408/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506776393162686465/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506776398489190400/4.gif"
    ]
},
"обнять":{
    "response":"{author} обнял(а) {user}. Это так романтично",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506777002309582863/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777067539398656/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777070899298316/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777079975510016/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777090629304340/4.gif"
    ]
}
}



punch_list = ['https://media.giphy.com/media/1n753Z1ZeGdkwxtYHo/giphy.gif',
               'https://media.giphy.com/media/WgN70xgCycyg2ZC5G6/giphy.gif',
               'https://media.giphy.com/media/orU5Hg8KwR430W7GIs/giphy.gif',
               'https://media.giphy.com/media/PiieOBhf5ymvOVxnzm/giphy.gif',
               'https://media.giphy.com/media/Xpj8gSHOCxONPz19AV/giphy.gif',
               'https://media.giphy.com/media/YxwAwiJEqEoFi/giphy.gif']

drink_list = ['https://media.giphy.com/media/1xlqPePKvCM3xVkWet/giphy.gif',
              'https://media.giphy.com/media/9rlYebzurMAXNaBGUO/giphy.gif',
              'https://media.giphy.com/media/1zlE7BBo7BuwpKfA4Z/giphy.gif',
              'https://media.giphy.com/media/nKMYwijvNrRwQJtq6W/giphy.gif',
              'https://media.giphy.com/media/eeLJdyAGPjnChKSlhu/giphy.gif',
              'https://media.giphy.com/media/55ma8eHi4YPCz6IZZO/giphy.gif',
              'https://media.giphy.com/media/NSqNZRkKShyKtedi0c/giphy.gif',
              'https://media.giphy.com/media/1BfhcYJtmPsM81JaRR/giphy.gif']

hug_list = [
"https://media.giphy.com/media/EvYHHSntaIl5m/giphy.gif",
"https://media.giphy.com/media/lXiRKBj0SAA0EWvbG/giphy.gif",
"https://media.giphy.com/media/xT0Gqne4C3IxaBcOdy/giphy.gif",
#"https://media.giphy.com/media/gnXG2hODaCOru/giphy.gif",
"https://media.giphy.com/media/VGACXbkf0AeGs/giphy.gif",
"https://media.giphy.com/media/l378uBCYt1vfaj2aA/giphy.gif",
"https://media.giphy.com/media/26FeTvBUZErLbTonS/giphy.gif",
"https://media.giphy.com/media/l4FGy5UyZ1KnVZ7BC/giphy.gif",
"https://media.giphy.com/media/3oz8xt8ebVWCWujyZG/giphy.gif",
"https://media.giphy.com/media/l0HlOvJ7yaacpuSas/giphy.gif",
"https://media.giphy.com/media/3otPozEs14AOGrdcOI/giphy.gif",
#"https://media.giphy.com/media/DjoWze0Patl1m/giphy.gif",
"https://media.giphy.com/media/3o6Mb7KaEIURtCKAbS/giphy.gif",
"https://media.giphy.com/media/w09VX7IEsoX6w/giphy.gif",
"https://media.giphy.com/media/vL1meInBzYCgo/giphy.gif",
"https://media.giphy.com/media/oVr48mIz8l5XG/giphy.gif",
"https://media.giphy.com/media/mmPgxbuPiwCQg/giphy.gif",
"https://media.giphy.com/media/3EJsCqoEiq6n6/giphy.gif",
"https://media.giphy.com/media/Ilkurs1e3hP0c/giphy.gif",
"https://media.giphy.com/media/jOoxG4mWGuH9S/giphy.gif",
"https://media.giphy.com/media/3orif2vpZbXi8P0fPW/giphy.gif",
"https://media.giphy.com/media/l4KhMHSclwbAGzGeI/giphy.gif",
"https://media.giphy.com/media/13fQ3RrUjteykw/giphy.gif",
"https://media.giphy.com/media/3ornk7CaGmo2uuxiJW/giphy.gif",
"https://media.giphy.com/media/xT1XGNlkcBDSqkCRqg/giphy.gif",
"https://media.giphy.com/media/l2JJySFVazmR38Lks/giphy.gif",
"https://media.giphy.com/media/3o7WTDVMidWRDzP9ss/giphy.gif",
"https://media.giphy.com/media/mLYVrZR44EcU0/giphy.gif",
"https://media.giphy.com/media/13YrHUvPzUUmkM/giphy.gif",
"https://media.giphy.com/media/du8yT5dStTeMg/giphy.gif",
"https://media.giphy.com/media/BXrwTdoho6hkQ/giphy.gif",
"https://media.giphy.com/media/qscdhWs5o3yb6/giphy.gif",
"https://media.giphy.com/media/xJlOdEYy0r7ZS/giphy.gif",
"https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
"https://media.giphy.com/media/svXXBgduBsJ1u/giphy.gif",
"https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
"https://media.giphy.com/media/NZ8dp5kWRbM4g/giphy.gif",
"https://media.giphy.com/media/kFTKQfjK4ysZq/giphy.gif",
"https://media.giphy.com/media/49mdjsMrH7oze/giphy.gif",
"https://media.giphy.com/media/aD1fI3UUWC4/giphy.gif",
"https://media.giphy.com/media/5eyhBKLvYhafu/giphy.gif",
"https://media.giphy.com/media/ddGxYkb7Fp2QRuTTGO/giphy.gif",
"https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
"https://media.giphy.com/media/ZRI1k4BNvKX1S/giphy.gif",
"https://media.giphy.com/media/s31WaGPAmTP1e/giphy.gif",
"https://media.giphy.com/media/wSY4wcrHnB0CA/giphy.gif",
"https://media.giphy.com/media/C4gbG94zAjyYE/giphy.gif",
"https://media.giphy.com/media/kvKFM3UWg2P04/giphy.gif",
"https://media.giphy.com/media/rSNAVVANV5XhK/giphy.gif",
"https://media.giphy.com/media/HaC1WdpkL3W00/giphy.gif",
"https://media.giphy.com/media/eMpDBxxTzKety/giphy.gif",
"https://media.giphy.com/media/DjczAlIcyK1Co/giphy.gif",
"https://media.giphy.com/media/yziFo5qYAOgY8/giphy.gif",
"https://media.giphy.com/media/iMrHFdDEoxT5S/giphy.gif",
"https://media.giphy.com/media/NZ8dp5kWRbM4g/giphy.gif",
"https://media.giphy.com/media/fFC10O3zlGfe/giphy.gif",
"https://media.giphy.com/media/aD1fI3UUWC4/giphy.gif",
"https://media.giphy.com/media/ZQN9jsRWp1M76/giphy.gif",
"https://media.giphy.com/media/TdXxcoNvHDVu0/giphy.gif",
"https://media.giphy.com/media/oTiuuAuYb22KQ/giphy.gif",
"https://media.giphy.com/media/11WhdeCxSM5lyo/giphy.gif",
"https://media.giphy.com/media/DjczAlIcyK1Co/giphy.gif"
]

sex_list = [
'https://discord.band/gif/1.gif',
'https://discord.band/gif/2.gif',
'https://discord.band/gif/3.gif',
'https://discord.band/gif/5.gif',
'https://discord.band/gif/6.gif',
'https://discord.band/gif/7.gif',
'https://discord.band/gif/8.gif',
'https://discord.band/gif/9.gif',
'https://discord.band/gif/10.gif',
'https://discord.band/gif/11.gif',
'https://discord.band/gif/12.gif',
'https://discord.band/gif/13.gif',
'https://discord.band/gif/14.gif',
'https://discord.band/gif/15.gif',
'https://discord.band/gif/16.gif'
]

kiss_list = [
#"https://media.giphy.com/media/KMuPz4KDkJuBq/giphy.gif",
"https://media.giphy.com/media/PFjXmKuwQsS9q/giphy.gif",
"https://media.giphy.com/media/3o7qDVQ2GrFAf1MVgc/giphy.gif",
"https://media.giphy.com/media/bCY7hoYdXmD4c/giphy.gif",
"https://media.giphy.com/media/HKQZgx0FAipPO/giphy.gif",
"https://media.giphy.com/media/l2Je2M4Nfrit0L7sQ/giphy.gif",
"https://media.giphy.com/media/3o6ozHbQHZzDTxRjsA/giphy.gif",
"https://media.giphy.com/media/3og0IvIXD1UrcEvNmw/giphy.gif",
"https://media.giphy.com/media/l0HU2EeywKGaMJCY8/giphy.gif",
"https://media.giphy.com/media/HN4Om0tu8y7gk/giphy.gif",
"https://media.giphy.com/media/3o7TKzkCiuW3E0Gn4Y/giphy.gif",
#"https://media.giphy.com/media/l0MYLr8Qh3opXBSSI/giphy.gif",
"https://media.giphy.com/media/26ufmeUh9YOVS53Xi/giphy.gif",
"https://media.giphy.com/media/26tnbo7HDeYacLQK4/giphy.gif",
"https://media.giphy.com/media/l0MYEw4RMBirPQhHy/giphy.gif",
"https://media.giphy.com/media/xThtaig5DpJpA1wuOs/giphy.gif",
"https://media.giphy.com/media/4GLJbNy3DdXPi/giphy.gif",
"https://media.giphy.com/media/2stFpADPSpfQQ/giphy.gif",
"https://media.giphy.com/media/3oAt2gl4VpnHiDW7hC/giphy.gif",
"https://media.giphy.com/media/KH1CTZtw1iP3W/giphy.gif",
"https://media.giphy.com/media/l0ErEXpCoUcS15UNq/giphy.gif",
#"https://media.giphy.com/media/1041PhUHlC0tJC/giphy.gif",
"https://media.giphy.com/media/3o6ZsXco9ACON6dSjS/giphy.gif",
"https://media.giphy.com/media/3oz8xIZrAhijabg69a/giphy.gif",
"https://media.giphy.com/media/7JaFQzMXdw759xdvpk/giphy.gif",
"https://media.giphy.com/media/3o6gDXMurw9nM2vLR6/giphy.gif",
"https://media.giphy.com/media/CzCi6itPr3yBa/giphy.gif",
"https://media.giphy.com/media/mGAzm47irxEpG/giphy.gif",
"https://media.giphy.com/media/hnNyVPIXgLdle/giphy.gif",
"https://media.giphy.com/media/f5vXCvhSJsZxu/giphy.gif",
"https://media.giphy.com/media/ZRSGWtBJG4Tza/giphy.gif",
"https://media.giphy.com/media/11k3oaUjSlFR4I/giphy.gif",
"https://media.giphy.com/media/JynbO9pnGxPrO/giphy.gif",
"https://media.giphy.com/media/nyGFcsP0kAobm/giphy.gif",
"https://media.giphy.com/media/4MBsFo1nSCfOo/giphy.gif",
#"https://media.giphy.com/media/Ch5UXfXJ3xbNK/giphy.gif",
"https://media.giphy.com/media/BaEE3QOfm2rf2/giphy.gif",
"https://media.giphy.com/media/uSHX6qYv1M7pC/giphy.gif",
"https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
"https://media.giphy.com/media/EP9YxsbmbplIs/giphy.gif",
"https://media.giphy.com/media/OSq9souL3j5zW/giphy.gif",
"https://media.giphy.com/media/sS7Jac8n7L3Ve/giphy.gif",
"https://media.giphy.com/media/9P8t4wusRUdSE/giphy.gif",
"https://media.giphy.com/media/EVODaJHSXZGta/giphy.gif",
"https://media.giphy.com/media/wOtkVwroA6yzK/giphy.gif",
"https://media.giphy.com/media/fHtb1JPbfph72/giphy.gif",
#"https://media.giphy.com/media/A5FtN4L0Yp2dq/giphy.gif",
"https://media.giphy.com/media/pwZ2TLSTouCQw/giphy.gif",
"https://media.giphy.com/media/K4VEsbuHfcj6g/giphy.gif",
"https://media.giphy.com/media/HWIe1Vrs6QxFe/giphy.gif",
"https://media.giphy.com/media/tJmYMnwlvRxdK/giphy.gif",
"https://media.giphy.com/media/rSBJ7muTr25ry/giphy.gif",
"https://media.giphy.com/media/wHbQ7IMBrgTzq/giphy.gif",
"https://media.giphy.com/media/EPQDbdvqne1rM6hel8/giphy.gif",
"https://media.giphy.com/media/JFmIDQodMScJW/giphy.gif",
"https://media.giphy.com/media/ll5leTSPh4ocE/giphy.gif",
"https://media.giphy.com/media/Y9iiZdUaNRF2U/giphy.gif",
"https://media.giphy.com/media/jR22gdcPiOLaE/giphy.gif",
"https://media.giphy.com/media/CTo4IKRN4l4SA/giphy.gif",
"https://media.giphy.com/media/CRSuLR6rhDdT2/giphy.gif",
#"https://media.giphy.com/media/r1FBFMAOo8Mhy/giphy.gif",
"https://media.giphy.com/media/kU586ictpGb0Q/giphy.gif",
"https://media.giphy.com/media/bm2O3nXTcKJeU/giphy.gif",
"https://media.giphy.com/media/Ka2NAhphLdqXC/giphy.gif",
"https://media.giphy.com/media/dP8ONh1mN8YWQ/giphy.gif",
"https://media.giphy.com/media/L3rumss7XR4QM/giphy.gif",
"https://media.giphy.com/media/IdzovcoOUoUM0/giphy.gif",
"https://media.giphy.com/media/10r6oEoT6dk7E4/giphy.gif",
#"https://media.giphy.com/media/1VBRxFrg0hZ9C/giphy.gif",
#"https://media.giphy.com/media/Q1TXCgzvfLNbW/giphy.gif",
"https://media.giphy.com/media/8rE47U8UH1yEi9SI0o/giphy.gif",
#"https://media.giphy.com/media/nO8kxVKdXSaek/giphy.gif",
"https://media.giphy.com/media/s09VXOiOg79As/giphy.gif",
"https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
"https://media.giphy.com/media/7QkZap9kQ1iy4/giphy.gif"
]

wink_list = ['https://media.discordapp.net/attachments/436139161070731264/462679150163918849/orig.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679245945307146/giphy-1.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679323506245632/girls_winking_02.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679514330431488/girls_winking_16.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679850553966602/tenor.gif']

fuck_list = ['https://media.giphy.com/media/9DayfKDecuCwUMRs38/giphy.gif',
             'https://media.giphy.com/media/621mG5MkWcAX00a5J4/giphy.gif',
             'https://media.giphy.com/media/29MEDvCpkzMMCvuZB5/giphy.gif',
             'https://media.giphy.com/media/cUVsttxcdKJJVRiFAd/giphy.gif',
             'https://media.giphy.com/media/PQxjfWa751RVJTtkS5/giphy.gif',
             'https://media.giphy.com/media/9J6Rye3Fz0Dq0oHeVH/giphy.gif']

five_list = [
'https://media.giphy.com/media/4H70la8QkZfaUvV9G4/giphy.gif',
'https://media.giphy.com/media/DQbDgJn2P5Wy3S1zr5/giphy.gif',
'https://media.giphy.com/media/pG5zFVdVsrQVteCbVS/giphy.gif',
'https://media.giphy.com/media/cRMGrkAyMdyeASLKqK/giphy.gif',
'https://media.giphy.com/media/4ZkpV1LyG0dvxYW2Zd/giphy.gif',
'https://media.giphy.com/media/n5GussPCZuekOaqMW3/giphy.gif',
"https://media.giphy.com/media/wrzf9P70YWLJK/giphy.gif",
"https://media.giphy.com/media/l0MYClvw1RPj1cZeo/giphy.gif",
"https://media.giphy.com/media/l0HlD43ktQ5f8fuWk/giphy.gif",
"https://media.giphy.com/media/3o85xHXqvkattTod68/giphy.gif",
"https://media.giphy.com/media/1nPJ5XLyZWdd4xFGw5/giphy.gif",
"https://media.giphy.com/media/r2BtghAUTmpP2/giphy.gif",
"https://media.giphy.com/media/l2JhwnKUuohwKLDnG/giphy.gif",
"https://media.giphy.com/media/2AlVpRyjAAN2/giphy.gif",
"https://media.giphy.com/media/YfTPHZ85fGnle/giphy.gif",
"https://media.giphy.com/media/C4lSxWjqSJLfG/giphy.gif",
"https://media.giphy.com/media/3o7TKTeL57EJdYFKBW/giphy.gif",
"https://media.giphy.com/media/2O0vM7oQMp4A0/giphy.gif",
"https://media.giphy.com/media/9wZybot8h5Nte/giphy.gif",
"https://media.giphy.com/media/diKF8kxuomAxy/giphy.gif",
"https://media.giphy.com/media/100QWMdxQJzQC4/giphy.gif",
"https://media.giphy.com/media/fLK0eUlYZoB6E/giphy.gif",
"https://media.giphy.com/media/13wHPKuKou0ndu/giphy.gif",
"https://media.giphy.com/media/uIu5b0YYpTPR6/giphy.gif",
"https://media.giphy.com/media/3oEduV4SOS9mmmIOkw/giphy.gif",
"https://media.giphy.com/media/fm4WhPMzu9hRK/giphy.gif",
"https://media.giphy.com/media/26ufmAlKt4ne2JDnq/giphy.gif",
"https://media.giphy.com/media/jG7UpdWLjoYuY/giphy.gif",
"https://media.giphy.com/media/l46CcVsDKp97gSDhm/giphy.gif",
"https://media.giphy.com/media/sSzCDRnOMaq3K/giphy.gif",
"https://media.giphy.com/media/DohrJX1h2W5RC/giphy.gif",
"https://media.giphy.com/media/13zazU4zSlJCiA/giphy.gif",
"https://media.giphy.com/media/WrGiAHYhZZYZ2/giphy.gif",
"https://media.giphy.com/media/3oEdvaba4h0I536VYQ/giphy.gif",
"https://media.giphy.com/media/l0HlSYVgZLQ1Y4GdO/giphy.gif",
"https://media.giphy.com/media/353PfIYZWFHaM/giphy.gif",
"https://media.giphy.com/media/3DZzjf7xCgb7y/giphy.gif",
"https://media.giphy.com/media/3o6gEgwAO6ojq63sbu/giphy.gif",
"https://media.giphy.com/media/3o85xspHMaZxVGbzY4/giphy.gif",
"https://media.giphy.com/media/l46ClnO4XNwTCuXsY/giphy.gif",
"https://media.giphy.com/media/26BREWfA5cRZJbMd2/giphy.gif",
"https://media.giphy.com/media/3o6Zt7hngn9xwnN7lC/giphy.gif",
"https://media.giphy.com/media/xT0xeQbBYVUPiKkzQs/giphy.gif",
"https://media.giphy.com/media/S6l0TQr5lomVG/giphy.gif",
"https://media.giphy.com/media/3o7TKMYAveUIqs3ZUk/giphy.gif",
"https://media.giphy.com/media/3o7buds9QVy5nCVCLe/giphy.gif",
"https://media.giphy.com/media/l42Pnm9RVo0ZG4EmI/giphy.gif",
"https://media.giphy.com/media/TQHyiK771gQw0/giphy.gif",
"https://media.giphy.com/media/l2R020v6spGBpGHrG/giphy.gif",
"https://media.giphy.com/media/GzCp9sGvlWKOc/giphy.gif",
"https://media.giphy.com/media/cAiBXaCjbHTry/giphy.gif",
"https://media.giphy.com/media/yUcor4CrgbrUY/giphy.gif",
"https://media.giphy.com/media/mJ8Xr2xYruvyF0QtMK/giphy.gif",
"https://media.giphy.com/media/QtJZpBnBJJew/giphy.gif",
"https://media.giphy.com/media/l41JOPMjzNoMYl71e/giphy.gif",
"https://media.giphy.com/media/gQ8qWas3GxlPq/giphy.gif",
"https://media.giphy.com/media/l2R0f2obXKscBVE1q/giphy.gif",
"https://media.giphy.com/media/x58AS8I9DBRgA/giphy.gif"
]


xp_lvlup_list = {
"10":1,
"30":2,
"60":3,
"100":4,
"150":5,
"210":6,
"280":7,
"360":8,
"450":9,
"550":10,
"660":11,
"780":12,
"910":13,
"1050":14,
"1200":15,
"1360":16,
"1530":17,
"1710":18,
"1900":19,
"2100":20,
"2310":21,
"2530":22,
"2760":23,
"3000":24,
"3250":25,
"3510":26,
"3780":27,
"4060":28,
"4350":29,
"4650":30,
"4960":31,
"5280":32,
"5610":33,
"5950":34,
"6300":35,
"6660":36,
"7030":37,
"7410":38,
"7800":39,
"8200":40,
"8610":41,
"9030":42,
"9460":43,
"9900":44,
"10350":45,
"10810":46,
"11280":47,
"11760":48,
"12250":49,
"12750":50
}

lvlup_image_url = "https://discord.band/images/lvlup.png"
lvlup_image_konoha_url = "https://discord.band/images/lvlupkonoha.png"


background_change_price = 1000

background_list = [
'neko.jpg',
'miku.jpg',
'stare.jpg',
'magic.jpg',
'night.jpg',
'autumn.jpg',
'kanade.jpg',
'forest.jpg',
'railway.jpg',
'adventure.jpg',
'mountains.jpg',
'schoolgirl.jpg',
'fairy_tale.jpg',
'nao_tomori.jpg',
'anime_girl.jpg',
'angel_beats.jpg',
'guilty_crown.jpg',
'yukari_yakumo.jpg',
'girl_with_wings.jpg',
'your_lie_in_april.jpg'
]

background_name_list = [
'Neko',
'Miku',
'Stare',
'Magic',
'Night',
'Autumn',
'Kanade',
'Forest',
'Railway',
'Adventure',
'Mountains',
'Schoolgirl',
'Fairy_Tale',
'Nao Tomori',
'Anime Girl',
'Angel Beats',
'Guilty Crown',
'Yukari Yakumo',
'Girl With Wings',
'Your Lie In April'
]

konoha_background_list = [
'konoha_primary.jpg'
]

konoha_background_name_list = [
'Konoha'
]


lang_filter = {
    "475425777215864833": {
        "filter": "1234567890\\`~!@#$%^&*()_+—-=|'’\"•√π÷×¶∆£€₽¢^°∆%©®™✓;:][\{\}/?.«»₽> 〖〗,<–⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾”“₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ№ї₴єіqwertyuiopasdfghjklzxcvbnmйцукенгшщзхъфывапролджэячсмитьбюё",
        "report_channel": "484805775034810378"
    }
}

async def check_words(client, message):
    serv = lang_filter.get(message.server.id)
    if not serv:
        return
    filter = serv.get("filter")
    emojis = client.get_all_emojis()
    for symbol in message.content:
        if not symbol.lower() in filter:
            if symbol in emojis_compact:
                continue
            em = discord.Embed(color=0xF44268)
            em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            em.description = message.content
            em.add_field(
                name="Channel",
                value=message.channel.mention,
                inline=True
            )
            em.add_field(
                name="Symbol",
                value=symbol,
                inline=True
            )
            await client.send_message(client.get_channel(serv.get("report_channel")), embed=em)
            await client.delete_message(message)
            return

# achievements = [
#
# ]



badges_obj = {
"staff": Image.open("cogs/stat/badges/staff.png"),
"partner": Image.open("cogs/stat/badges/partner.png"),
"hypesquad": Image.open("cogs/stat/badges/hypesquad.png"),
"bug_hunter": Image.open("cogs/stat/badges/bug_hunter.png"),
"nitro": Image.open("cogs/stat/badges/nitro.png"),
"early": Image.open("cogs/stat/badges/early.png"),
"verified": Image.open("cogs/stat/badges/verified.png")
}

badges_list = [
"staff",
"partner",
"hypesquad",
"bug_hunter",
"nitro",
"early",
"verified"
]

global cached_servers
cached_servers = {}

async def clear_cache():
    global cached_servers
    cached_servers = {}
    await asyncio.sleep(600)


async def get_cached_server(conn, id):
    global cached_servers
    if not id in cached_servers.keys():
        cached_servers[id] = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=id))
    return cached_servers.get(id)

def pop_cached_server(id):
    global cached_servers
    return cached_servers.pop(id, None)


async def check_badges(conn, id, badges):
    dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'badges' AND name = '{id}'".format(id=id))
    ret = []
    if not dat:
        return ret
    for badge in badges:
        if badge in dat["arguments"]:
            ret.append(badge)
    return ret



prefix_list = [
    '!',
    '?',
    '$',
    't!',
    't?',
    't$',
    '.',
    '-',
    '+',
    '\\',
    ';',
    '>',
    '<',
    '~',
    '^',
    '=',
    '_'
]


short_locales = {
"en": "english",
"ru": "russian",
"ua": "ukrainian"
}


black_filename_list = [
"2018-03-15_10.26.23_1",
"2018-03-16_01.41.19_1",
"2018-03-16_12.07.43_1",
"2018-03-16_12.12.56_1",
"2018-04-14_04.00.21_1",
"2018-04-14_04.00.35_1"
]

ddos_name_list = [
"FeijhV",
"t.me",
"jsop",
"ᴊsᴏᴘ",
"traff",
"ᴛ.ᴍᴇ",
"discord.gg"
]


ururu_responses = [
"Уруру",
"Урурушеньки",
"Урурушечки",
"Уруру))",
"Урурушеньки))",
"Урурушечки))"
]


slot_kanna = '<:kanna:491965559907418112>'
slot_pantsu1 = '<:pantsu:491967185254613023>'
slot_pantsu2 = '<:pantsu2:491965559387455506>'
slot_doge = '<:doge:491965559529930753>'
slot_trap = '<:trap:491965559806754847>'
slot_salt = '<:salt:491965559613947904>'
slot_awoo = '<:awoo:491965559748165633>'
slot_boom = '<:booom:491965559496376330>'
slot_melban = '<:banned:491965559659954201>'
slots_ver = []

i = 0
while i < 3:
    i += 1
    slots_ver.append(slot_kanna)
i = 0
while i < 40:
    i += 1
    slots_ver.append(slot_melban)
i = 0
while i < 40:
    i += 1
    slots_ver.append(slot_boom)
i = 0
while i < 5:
    i += 1
    slots_ver.append(slot_pantsu1)
i = 0
while i < 10:
    i += 1
    slots_ver.append(slot_pantsu2)
i = 0
while i < 15:
    i += 1
    slots_ver.append(slot_doge)
i = 0
while i < 20:
    i += 1
    slots_ver.append(slot_salt)
i = 0
while i < 25:
    i += 1
    slots_ver.append(slot_awoo)
i = 0
while i < 30:
    i += 1
    slots_ver.append(slot_trap)

default_message = discord.Embed(color=0xC5934B)
success_message = discord.Embed(color=0x00ff08)
error_message = discord.Embed(color=0xff3838)

default_color = 0xC5934B
success_color = 0x00ff08
error_color = 0xff3838


BR_MAX_BET = 10000
SLOTS_MAX_BET = 5000


not_log_servers = [
"264445053596991498",
"110373943822540800",
"401422952639496213",
"435863655314227211",
"450100127256936458"
]

log_join_leave_server_channel_id = "493196075352457247"
log_join_leave_server_id = "480689184814792704"
admin_server_id = "327029562535968768"

#             Ананасовая Печенюха         Unknown                Teris                Oddy38
admin_list = ['501869445531041792', '499937748862500864', '281037696225247233', '496569904527441921', '500943025640439819']
#               Ананасовая Печенюха         Unknown                Teris                Oddy38              mankidelufi              _Nier                RusTNT
support_list = ['501869445531041792', '499937748862500864', '281037696225247233', '496569904527441921', '342557917121347585', '236426208315834369', '258156175730802688', '500943025640439819']

nazarik_id = "465616048050143232"
nazarik_log_id = "480692089332695040"

tester_role_id = "477738087212908544"

uptimes = 0


global muted_users
muted_users = {}

global top_servers
top_servers = []

tomori_links = '[Vote](https://discordbots.org/bot/491605739635212298/vote "for Tomori") \
[Patreon](https://www.patreon.com/tomori_discord "Donate") \
[YouTube](https://www.youtube.com/channel/UCxqg3WZws6KxftnC-MdrIpw "Tomori Project\'s channel") \
[Telegram](https://t.me/TomoriDiscord "Our telegram channel") \
[Website](https://discord.band "Our website") \
[VK](https://vk.com/tomori_discord "Our group on vk.com")'
# tomori_links = '[Join Konoha](https://discord.gg/PErt9KY "Join anime Naruto")'

def clear_name(name):
    return re.sub(r'[\';"\\]+', '', name)



logg = logging.getLogger('tomori-debug')
logg.setLevel(logging.DEBUG)
logname = 'logs/debug.log'
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
logg.addHandler(handler)


async def get_embed(value):
    try:
        ret = json.loads(value)
        if ret and isinstance(ret, dict):
            em = discord.Embed(**ret)
            if "author" in ret.keys():
                em.set_author(
                    name=ret["author"].get("name"),
                    url=ret["author"].get("url", discord.Embed.Empty),
                    icon_url=ret["author"].get("icon_url", discord.Embed.Empty)
                )
            if "footer" in ret.keys():
                em.set_footer(
                    text=ret["footer"].get("text", discord.Embed.Empty),
                    icon_url=ret["footer"].get("icon_url", discord.Embed.Empty)
                )
            if "image" in ret.keys():
                em.set_image(
                    url=ret["image"]
                )
            if "thumbnail" in ret.keys():
                em.set_thumbnail(
                    url=ret["thumbnail"]
                )
            if "fields" in ret.keys():
                for field in ret["fields"]:
                    try:
                        em.add_field(
                            name=field.get("name"),
                            value=field.get("value"),
                            inline=field.get("inline", False)
                        )
                    except:
                        pass
        if "text" in ret.keys():
            text = ret["text"]
        else:
            text = None
    except:
        text = value
        em = None
    return text, em


async def dict_to_embed(ret):
    try:
        if ret:
            em = discord.Embed(**ret)
            if "author" in ret.keys():
                em.set_author(
                    name=ret["author"].get("name"),
                    url=ret["author"].get("url", discord.Embed.Empty),
                    icon_url=ret["author"].get("icon_url", discord.Embed.Empty)
                )
            if "footer" in ret.keys():
                em.set_footer(
                    text=ret["footer"].get("text", discord.Embed.Empty),
                    icon_url=ret["footer"].get("icon_url", discord.Embed.Empty)
                )
            if "image" in ret.keys():
                em.set_image(
                    url=ret["image"]
                )
            if "thumbnail" in ret.keys():
                em.set_thumbnail(
                    url=ret["thumbnail"]
                )
            if "fields" in ret.keys():
                for field in ret["fields"]:
                    try:
                        em.add_field(
                            name=field.get("name"),
                            value=field.get("value"),
                            inline=field.get("inline", False)
                        )
                    except:
                        pass
        if "text" in ret.keys():
            text = ret["text"]
        else:
            text = None
    except:
        text = str(ret)
        em = None
    return text, em






errors = {
    "user_in_not_exists_guild": "Guild Error 404",
    "guild_remove_not_exists": "Guild Error 500",
    "guild_info_not_exists": "Guild Error 403",
    "guild_join_member_not_exists": "Guild Error 99",
    "guild_accept_bad_response": "Guild Error 69"
}




captcha_list = {
    "ȚÖMÖŖÏ": "tomori",
    "•´¯`•. t๏๓๏гเ .•´¯`•": "tomori",
    "ŤỖϻỖŘĮ": "tomori",
    "ČỖỖЌĮẸ": "cookie",
    "cooĸιe": "cookie",
    "ȼ๏๏Ќɨ€": "cookie",
    "𝕿𝖔𝖒𝖔𝖗𝖎": "tomori",
    "🌴⚽〽️⚽🌱🎐": "tomori",
    "🆃🅾🅼🅾🆁🅸": "tomori",
    "ᗫᓿSᑤᓎᖇᗫ": "discord",
    "ÐɪらㄈØ尺Ð": "discord",
    "ⓓⓘⓢⓒⓞⓡⓓ": "discord",
    "𝓭𝓲𝓼𝓬𝓸𝓻𝓭": "discord",
    "𝖓𝖎𝖈𝖊 𝖈𝖆𝖕𝖙𝖈𝖍𝖆": "nice captcha",
    "ᑎIᑕE ᑕᗩᑭTᑕᕼᗩ": "nice captcha",
    "ɴɪᴄᴇ ᴄᴀᴘᴛᴄʜᴀ": "nice captcha",
    "𝕀 𝕙𝕒𝕥𝕖 𝕪𝕠𝕦": "i hate you",
    "𝕴 𝖍𝖆𝖙𝖊 𝖞𝖔𝖚": "i hate you",
    "𝓘 𝓱𝓪𝓽𝓮 𝔂𝓸𝓾": "i hate you",
    "𝙄 𝙝𝙖𝙩𝙚 𝙮𝙤𝙪": "i hate you"
}

captcha_symbols = [
    "EYUIOA",
    "QWRTPSDFGHJKLZXCVBNM"
]




welcome_responses_dm = {
# ОКД (чета с ссср)
"485447833932005379": {
      "text": "Здесь описание интересностей сервера - <#490177759507775489>",
      "description": "**А правила очень просты: **\n- Нельзя нарушать законы РФ\n- Нельзя переходить на личности в оскорблениях\n- Нельзя рекламировать сервера дискорда.\n\nРады видеть вас на нашем сервере! Всего доброго!",
      "color": 12948299
    },
# КАКТАМНОВОСТИ
"496507405732020224": {
      "description": "**Добро пожаловать на новостной сервер КАКТАМНОВОСТИ.**\n\nПрежде чем ты начнешь знакомиться с остальными участниками, пожалуйста,  ознакомься с полезной информацией на канале <#496697194649223175>\n\n*Тут могут быть БУФЕРА, ТРЕШ и НЕ БУДЕТ НАСТЫРНЫХ ПРАВЕДНИКОВ, (возможно).\nНадеюсь тебе у нас понравится!\nЖелаем приятного время КАКТАМпровождения.*\n\nЧто ж, веселись и приглашай друзей! :blush:\nПокедова, увидимся на сервере :heart: ",
      "author": {
        "name": "КАКТАМНОВОСТИ",
        "icon_url": "https://images-ext-2.discordapp.net/external/Nne3hrU-e2gDmobjirCrOJO3dVfeTSiYx6Y2l4cf1EE/https/cdn.discordapp.com/icons/496507405732020224/5c81c2acec3621896e4a7f1a15947975.jpg"
      },
      "color": 3553599
    }
}


emojis_compact = ["👩‍👩‍👦","👩","😀","😁","😂","🤣","😃","😄","😅","😆","😉","😊","😋","😎","😍","😘","🥰","😗","😙","😚","☺","🙂","🤗","🤩","🤔","🤨","😐","😑","😶","🙄","😏","😣","😥","😮","🤐","😯","😪","😫","😴","😌","😛","😜","😝","🤤","😒","😓","😔","😕","🙃","🤑","😲","☹","🙁","😖","😞","😟","😤","😢","😭","😦","😧","😨","😩","🤯","😬","😰","😱","🥵","🥶","😳","🤪","😵","😡","😠","🤬","😷","🤒","🤕","🤢","🤮","🤧","😇","🤠","🥳","🥴","🥺","🤥","🤫","🤭","🧐","🤓","😈","👿","🤡","👹","👺","💀","☠","👻","👽","👾","🤖","💩","😺","😸","😹","😻","😼","😽","🙀","😿","😾","🙈","🙉","🙊","👶","🧒","👦","👧","🧑","👨","👩","🧓","👴","👵","👨‍⚕️","👩‍⚕️","👨‍🎓","👩‍🎓","👨‍🏫","👩‍🏫","👨‍⚖️","👩‍⚖️","👨‍🌾","👩‍🌾","👨‍🍳","👩‍🍳","👨‍🔧","👩‍🔧","👨‍🏭","👩‍🏭","👨‍💼","👩‍💼","👨‍🔬","👩‍🔬","👨‍💻","👩‍💻","👨‍🎤","👩‍🎤","👨‍🎨","👩‍🎨","👨‍✈️","👩‍✈️","👨‍🚀","👩‍🚀","👨‍🚒","👩‍🚒","👮","👮‍♂️","👮‍♀️","🕵","🕵️‍♂️","🕵️‍♀️","💂","💂‍♂️","💂‍♀️","👷","👷‍♂️","👷‍♀️","🤴","👸","👳","👳‍♂️","👳‍♀️","👲","🧕","🧔","👱","👱‍♂️","👱‍♀️","👨‍🦰","👩‍🦰","👨‍🦱","👩‍🦱","👨‍🦲","👩‍🦲","👨‍🦳","👩‍🦳","🤵","👰","🤰","🤱","👼","🎅","🤶","🦸","🦸‍♀️","🦸‍♂️","🦹","🦹‍♀️","🦹‍♂️","🧙","🧙‍♀️","🧙‍♂️","🧚","🧚‍♀️","🧚‍♂️","🧛","🧛‍♀️","🧛‍♂️","🧜","🧜‍♀️","🧜‍♂️","🧝","🧝‍♀️","🧝‍♂️","🧞","🧞‍♀️","🧞‍♂️","🧟","🧟‍♀️","🧟‍♂️","🙍","🙍‍♂️","🙍‍♀️","🙎","🙎‍♂️","🙎‍♀️","🙅","🙅‍♂️","🙅‍♀️","🙆","🙆‍♂️","🙆‍♀️","💁","💁‍♂️","💁‍♀️","🙋","🙋‍♂️","🙋‍♀️","🙇","🙇‍♂️","🙇‍♀️","🤦","🤦‍♂️","🤦‍♀️","🤷","🤷‍♂️","🤷‍♀️","💆","💆‍♂️","💆‍♀️","💇","💇‍♂️","💇‍♀️","🚶","🚶‍♂️","🚶‍♀️","🏃","🏃‍♂️","🏃‍♀️","💃","🕺","👯","👯‍♂️","👯‍♀️","🧖","🧖‍♀️","🧖‍♂️","🧗","🧗‍♀️","🧗‍♂️","🧘","🧘‍♀️","🧘‍♂️","🛀","🛌","🕴","🗣","👤","👥","🤺","🏇","⛷","🏂","🏌","🏌️‍♂️","🏌️‍♀️","🏄","🏄‍♂️","🏄‍♀️","🚣","🚣‍♂️","🚣‍♀️","🏊","🏊‍♂️","🏊‍♀️","⛹","⛹️‍♂️","⛹️‍♀️","🏋","🏋️‍♂️","🏋️‍♀️","🚴","🚴‍♂️","🚴‍♀️","🚵","🚵‍♂️","🚵‍♀️","🏎","🏍","🤸","🤸‍♂️","🤸‍♀️","🤼","🤼‍♂️","🤼‍♀️","🤽","🤽‍♂️","🤽‍♀️","🤾","🤾‍♂️","🤾‍♀️","🤹","🤹‍♂️","🤹‍♀️","👫","👬","👭","💏","👩‍❤️‍💋‍👨","👨‍❤️‍💋‍👨","👩‍❤️‍💋‍👩","💑","👩‍❤️‍👨","👨‍❤️‍👨","👩‍❤️‍👩","👪","👨‍👩‍👦","👨‍👩‍👧","👨‍👩‍👧‍👦","👨‍👩‍👦‍👦","👨‍👩‍👧‍👧","👨‍👨‍👦","👨‍👨‍👧","👨‍👨‍👧‍👦","👨‍👨‍👦‍👦","👨‍👨‍👧‍👧","👩‍👩‍👦","👩‍👩‍👧","👩‍👩‍👧‍👦","👩‍👩‍👦‍👦","👩‍👩‍👧‍👧","👨‍👦","👨‍👦‍👦","👨‍👧","👨‍👧‍👦","👨‍👧‍👧","👩‍👦","👩‍👦‍👦","👩‍👧","👩‍👧‍👦","👩‍👧‍👧","🤳","💪","🦵","🦶","👈","👉","☝","👆","🖕","👇","✌","🤞","🖖","🤘","🤙","🖐","✋","👌","👍","👎","✊","👊","🤛","🤜","🤚","👋","🤟","✍","👏","👐","🙌","🤲","🙏","🤝","💅","👂","👃","🦰","🦱","🦲","🦳","👣","👀","👁","👁️‍🗨️","🧠","🦴","🦷","👅","👄","💋","💘","❤","💓","💔","💕","💖","💗","💙","💚","💛","🧡","💜","🖤","💝","💞","💟","❣","💌","💤","💢","💣","💥","💦","💨","💫","💬","🗨","🗯","💭","🕳","👓","🕶","🥽","🥼","👔","👕","👖","🧣","🧤","🧥","🧦","👗","👘","👙","👚","👛","👜","👝","🛍","🎒","👞","👟","🥾","🥿","👠","👡","👢","👑","👒","🎩","🎓","🧢","⛑","📿","💄","💍","💎","🐵","🐒","🦍","🐶","🐕","🐩","🐺","🦊","🦝","🐱","🐈","🦁","🐯","🐅","🐆","🐴","🐎","🦄","🦓","🦌","🐮","🐂","🐃","🐄","🐷","🐖","🐗","🐽","🐏","🐑","🐐","🐪","🐫","🦙","🦒","🐘","🦏","🦛","🐭","🐁","🐀","🐹","🐰","🐇","🐿","🦔","🦇","🐻","🐨","🐼","🦘","🦡","🐾","🦃","🐔","🐓","🐣","🐤","🐥","🐦","🐧","🕊","🦅","🦆","🦢","🦉","🦚","🦜","🐸","🐊","🐢","🦎","🐍","🐲","🐉","🦕","🦖","🐳","🐋","🐬","🐟","🐠","🐡","🦈","🐙","🐚","🦀","🦞","🦐","🦑","🐌","🦋","🐛","🐜","🐝","🐞","🦗","🕷","🕸","🦂","🦟","🦠","💐","🌸","💮","🏵","🌹","🥀","🌺","🌻","🌼","🌷","🌱","🌲","🌳","🌴","🌵","🌾","🌿","☘","🍀","🍁","🍂","🍃","🍇","🍈","🍉","🍊","🍋","🍌","🍍","🥭","🍎","🍏","🍐","🍑","🍒","🍓","🥝","🍅","🥥","🥑","🍆","🥔","🥕","🌽","🌶","🥒","🥬","🥦","🍄","🥜","🌰","🍞","🥐","🥖","🥨","🥯","🥞","🧀","🍖","🍗","🥩","🥓","🍔","🍟","🍕","🌭","🥪","🌮","🌯","🥙","🥚","🍳","🥘","🍲","🥣","🥗","🍿","🧂","🥫","🍱","🍘","🍙","🍚","🍛","🍜","🍝","🍠","🍢","🍣","🍤","🍥","🥮","🍡","🥟","🥠","🥡","🍦","🍧","🍨","🍩","🍪","🎂","🍰","🧁","🥧","🍫","🍬","🍭","🍮","🍯","🍼","🥛","☕","🍵","🍶","🍾","🍷","🍸","🍹","🍺","🍻","🥂","🥃","🥤","🥢","🍽","🍴","🥄","🔪","🏺","🌍","🌎","🌏","🌐","🗺","🗾","🧭","🏔","⛰","🌋","🗻","🏕","🏖","🏜","🏝","🏞","🏟","🏛","🏗","🧱","🏘","🏚","🏠","🏡","🏢","🏣","🏤","🏥","🏦","🏨","🏩","🏪","🏫","🏬","🏭","🏯","🏰","💒","🗼","🗽","⛪","🕌","🕍","⛩","🕋","⛲","⛺","🌁","🌃","🏙","🌄","🌅","🌆","🌇","🌉","♨","🌌","🎠","🎡","🎢","💈","🎪","🚂","🚃","🚄","🚅","🚆","🚇","🚈","🚉","🚊","🚝","🚞","🚋","🚌","🚍","🚎","🚐","🚑","🚒","🚓","🚔","🚕","🚖","🚗","🚘","🚙","🚚","🚛","🚜","🚲","🛴","🛹","🛵","🚏","🛣","🛤","🛢","⛽","🚨","🚥","🚦","🛑","🚧","⚓","⛵","🛶","🚤","🛳","⛴","🛥","🚢","✈","🛩","🛫","🛬","💺","🚁","🚟","🚠","🚡","🛰","🚀","🛸","🛎","🧳","⌛","⏳","⌚","⏰","⏱","⏲","🕰","🕛","🕧","🕐","🕜","🕑","🕝","🕒","🕞","🕓","🕟","🕔","🕠","🕕","🕡","🕖","🕢","🕗","🕣","🕘","🕤","🕙","🕥","🕚","🕦","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘","🌙","🌚","🌛","🌜","🌡","☀","🌝","🌞","⭐","🌟","🌠","☁","⛅","⛈","🌤","🌥","🌦","🌧","🌨","🌩","🌪","🌫","🌬","🌀","🌈","🌂","☂","☔","⛱","⚡","❄","☃","⛄","☄","🔥","💧","🌊","🎃","🎄","🎆","🎇","🧨","✨","🎈","🎉","🎊","🎋","🎍","🎎","🎏","🎐","🎑","🧧","🎀","🎁","🎗","🎟","🎫","🎖","🏆","🏅","🥇","🥈","🥉","⚽","⚾","🥎","🏀","🏐","🏈","🏉","🎾","🥏","🎳","🏏","🏑","🏒","🥍","🏓","🏸","🥊","🥋","🥅","⛳","⛸","🎣","🎽","🎿","🛷","🥌","🎯","🎱","🔮","🧿","🎮","🕹","🎰","🎲","🧩","🧸","♠","♥","♦","♣","♟","🃏","🀄","🎴","🎭","🖼","🎨","🧵","🧶","🔇","🔈","🔉","🔊","📢","📣","📯","🔔","🔕","🎼","🎵","🎶","🎙","🎚","🎛","🎤","🎧","📻","🎷","🎸","🎹","🎺","🎻","🥁","📱","📲","☎","📞","📟","📠","🔋","🔌","💻","🖥","🖨","⌨","🖱","🖲","💽","💾","💿","📀","🧮","🎥","🎞","📽","🎬","📺","📷","📸","📹","📼","🔍","🔎","🕯","💡","🔦","🏮","📔","📕","📖","📗","📘","📙","📚","📓","📒","📃","📜","📄","📰","🗞","📑","🔖","🏷","💰","💴","💵","💶","💷","💸","💳","🧾","💹","💱","💲","✉","📧","📨","📩","📤","📥","📦","📫","📪","📬","📭","📮","🗳","✏","✒","🖋","🖊","🖌","🖍","📝","💼","📁","📂","🗂","📅","📆","🗒","🗓","📇","📈","📉","📊","📋","📌","📍","📎","🖇","📏","📐","✂","🗃","🗄","🗑","🔒","🔓","🔏","🔐","🔑","🗝","🔨","⛏","⚒","🛠","🗡","⚔","🔫","🏹","🛡","🔧","🔩","⚙","🗜","⚖","🔗","⛓","🧰","🧲","⚗","🧪","🧫","🧬","🔬","🔭","📡","💉","💊","🚪","🛏","🛋","🚽","🚿","🛁","🧴","🧷","🧹","🧺","🧻","🧼","🧽","🧯","🛒","🚬","⚰","⚱","🗿","🏧","🚮","🚰","♿","🚹","🚺","🚻","🚼","🚾","🛂","🛃","🛄","🛅","⚠","🚸","⛔","🚫","🚳","🚭","🚯","🚱","🚷","📵","🔞","☢","☣","⬆","↗","➡","↘","⬇","↙","⬅","↖","↕","↔","↩","↪","⤴","⤵","🔃","🔄","🔙","🔚","🔛","🔜","🔝","🛐","⚛","🕉","✡","☸","☯","✝","☦","☪","☮","🕎","🔯","♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓","⛎","🔀","🔁","🔂","▶","⏩","⏭","⏯","◀","⏪","⏮","🔼","⏫","🔽","⏬","⏸","⏹","⏺","⏏","🎦","🔅","🔆","📶","📳","📴","♀","♂","⚕","♾","♻","⚜","🔱","📛","🔰","⭕","✅","☑","✔","✖","❌","❎","➕","➖","➗","➰","➿","〽","✳","✴","❇","‼","⁉","❓","❔","❕","❗","〰","©","®","™","#️⃣","*️⃣","0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","💯","🔠","🔡","🔢","🔣","🔤","🅰","🆎","🅱","🆑","🆒","🆓","ℹ","🆔","Ⓜ","🆕","🆖","🅾","🆗","🅿","🆘","🆙","🆚","🈁","🈂","🈷","🈶","🈯","🉐","🈹","🈚","🈲","🉑","🈸","🈴","🈳","㊗","㊙","🈺","🈵","▪","▫","◻","◼","◽","◾","⬛","⬜","🔶","🔷","🔸","🔹","🔺","🔻","💠","🔘","🔲","🔳","⚪","⚫","🔴","🔵","🏁","🚩","🎌","🏴","🏳","🏳️‍🌈","🏴‍☠️","🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇦🇽","🇦🇿","🇧🇦","🇧🇧","🇧🇩","🇧🇪","🇧🇫","🇧🇬","🇧🇭","🇧🇮","🇧🇯","🇧🇱","🇧🇲","🇧🇳","🇧🇴","🇧🇶","🇧🇷","🇧🇸","🇧🇹","🇧🇻","🇧🇼","🇧🇾","🇧🇿","🇨🇦","🇨🇨","🇨🇩","🇨🇫","🇨🇬","🇨🇭","🇨🇮","🇨🇰","🇨🇱","🇨🇲","🇨🇳","🇨🇴","🇨🇵","🇨🇷","🇨🇺","🇨🇻","🇨🇼","🇨🇽","🇨🇾","🇨🇿","🇩🇪","🇩🇬","🇩🇯","🇩🇰","🇩🇲","🇩🇴","🇩🇿","🇪🇦","🇪🇨","🇪🇪","🇪🇬","🇪🇭","🇪🇷","🇪🇸","🇪🇹","🇪🇺","🇫🇮","🇫🇯","🇫🇰","🇫🇲","🇫🇴","🇫🇷","🇬🇦","🇬🇧","🇬🇩","🇬🇪","🇬🇫","🇬🇬","🇬🇭","🇬🇮","🇬🇱","🇬🇲","🇬🇳","🇬🇵","🇬🇶","🇬🇷","🇬🇸","🇬🇹","🇬🇺","🇬🇼","🇬🇾","🇭🇰","🇭🇲","🇭🇳","🇭🇷","🇭🇹","🇭🇺","🇮🇨","🇮🇩","🇮🇪","🇮🇱","🇮🇲","🇮🇳","🇮🇴","🇮🇶","🇮🇷","🇮🇸","🇮🇹","🇯🇪","🇯🇲","🇯🇴","🇯🇵","🇰🇪","🇰🇬","🇰🇭","🇰🇮","🇰🇲","🇰🇳","🇰🇵","🇰🇷","🇰🇼","🇰🇾","🇰🇿","🇱🇦","🇱🇧","🇱🇨","🇱🇮","🇱🇰","🇱🇷","🇱🇸","🇱🇹","🇱🇺","🇱🇻","🇱🇾","🇲🇦","🇲🇨","🇲🇩","🇲🇪","🇲🇫","🇲🇬","🇲🇭","🇲🇰","🇲🇱","🇲🇲","🇲🇳","🇲🇴","🇲🇵","🇲🇶","🇲🇷","🇲🇸","🇲🇹","🇲🇺","🇲🇻","🇲🇼","🇲🇽","🇲🇾","🇲🇿","🇳🇦","🇳🇨","🇳🇪","🇳🇫","🇳🇬","🇳🇮","🇳🇱","🇳🇴","🇳🇵","🇳🇷","🇳🇺","🇳🇿","🇴🇲","🇵🇦","🇵🇪","🇵🇫","🇵🇬","🇵🇭","🇵🇰","🇵🇱","🇵🇲","🇵🇳","🇵🇷","🇵🇸","🇵🇹","🇵🇼","🇵🇾","🇶🇦","🇷🇪","🇷🇴","🇷🇸","🇷🇺","🇷🇼","🇸🇦","🇸🇧","🇸🇨","🇸🇩","🇸🇪","🇸🇬","🇸🇭","🇸🇮","🇸🇯","🇸🇰","🇸🇱","🇸🇲","🇸🇳","🇸🇴","🇸🇷","🇸🇸","🇸🇹","🇸🇻","🇸🇽","🇸🇾","🇸🇿","🇹🇦","🇹🇨","🇹🇩","🇹🇫","🇹🇬","🇹🇭","🇹🇯","🇹🇰","🇹🇱","🇹🇲","🇹🇳","🇹🇴","🇹🇷","🇹🇹","🇹🇻","🇹🇼","🇹🇿","🇺🇦","🇺🇬","🇺🇲","🇺🇳","🇺🇸","🇺🇾","🇺🇿","🇻🇦","🇻🇨","🇻🇪","🇻🇬","🇻🇮","🇻🇳","🇻🇺","🇼🇫","🇼🇸","🇽🇰","🇾🇪","🇾🇹","🇿🇦","🇿🇲","🇿🇼","🏴󠁧󠁢󠁥󠁮󠁧󠁿","🏴󠁧󠁢󠁳󠁣󠁴󠁿","🏴󠁧󠁢󠁷󠁬󠁳󠁿","🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯","🇰","🇱","🇲","🇳","🇴","🇵","🇶","🇷","🇸","🇹","🇺","🇻","🇼","🇽","🇾","🇿"]
