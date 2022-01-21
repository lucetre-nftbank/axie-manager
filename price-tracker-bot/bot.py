import discord
from discord.ext import commands
import axie
import asyncio
import os
import requests
from datetime import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs
import re
import utils

bot = commands.Bot(command_prefix='!')
reset_flag = False

@bot.event
async def on_ready():
    global reset_flag
    reset_flag = False
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def reset(ctx):
    global reset_flag
    reset_flag = True
    print('Reset tracker...')

@bot.command()
async def market(ctx, q1='https://marketplace.axieinfinity.com/axie/?class=Bird&part=mouth-doubletalk&part=horn-eggshell&part=back-pigeon-post&part=tail-post-fight&speed=61&speed=61&auctionTypes=Sale', q2='https://marketplace.axieinfinity.com/axie/?class=Aquatic&part=horn-anemone&part=back-anemone&part=tail-nimo&part=mouth-lam&speed=57&speed=61&auctionTypes=Sale', q3='https://marketplace.axieinfinity.com/axie/?class=Plant&part=back-bidens&part=horn-cactus&part=mouth-zigzag&part=tail-hot-butt&hp=61&hp=61&auctionTypes=Sale'):
    global reset_flag
    df = pd.DataFrame({'Timestamp': [], 'Axie1': [], 'Axie2': [], 'Axie3': []})
    reset_flag = False
    
    while True:
        if reset_flag == True:
            break
        try:
            print('Fetching market prices...')
            ethusd = utils.get_exchange_rate()
            content, prices = axie.message([q1, q2, q3], ethusd)
            
            df = df.append({'Timestamp': datetime.now(), 'Axie1': prices[0], 'Axie2': prices[1], 'Axie3': prices[2]}, ignore_index=True)
            utils.plot_fig(df)
            file = discord.File("market.png", filename='market.png')
            embed = discord.Embed(color=0xff0000)
            embed.description = content + f'Total Price: {sum(prices)} ETH'
            embed = embed.set_image(url="attachment://market.png")
            if reset_flag == True:
                break
            await ctx.send(file=file, embed=embed)
            if reset_flag == True:
                break
            await asyncio.sleep(60)

        except Exception as e:
            await ctx.send(f"An error occured: {e}")
    reset_flag = False
    

@bot.command()
async def leaderboard(ctx):
    print('Fetching leaderboard...')
    response = requests.request("GET", 'https://axie.zone/leaderboard')
    html = response.text
    trs = bs(html, features="html.parser").find_all('tr')
    leaderboard = []

    for tr in trs[1:5]:
        tds = tr.find_all('td')
        rank = int(tds[0].text[1:])
        ron_addr = tds[1].find("a")["href"].split('=')[-1]
        name = tds[1].text
        axie1, axie2, axie3 = utils.get_optimal_deck(ron_addr)[0]
        leaderboard.append([rank, ron_addr, name, axie1, axie2, axie3])
#         print(get_axie_for_sale(axie1))

    df = pd.DataFrame(leaderboard, columns=['rank', 'ron_addr', 'name', 'axie#1', 'axie#2', 'axie#3'])
    print(df)

with open("auth.json") as f:
    data = json.load(f)
    bot.run(data["private_key"])
