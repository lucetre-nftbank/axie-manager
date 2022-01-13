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
import seaborn as sns

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
    print('Market Reset')
    
def get_exchange_rate():
    payload = {
    "operationName": "NewEthExchangeRate",
    "query": "query NewEthExchangeRate {\n  exchangeRate {\n    eth {\n      usd\n      __typename\n    }\n    __typename\n  }\n}\n",
    "variables": {}
}
    r = requests.post("https://graphql-gateway.axieinfinity.com/graphql", json=payload)
    ethusd = json.loads(r.text)['data']['exchangeRate']['eth']['usd']
    return ethusd
    
def plot_fig(df):
    sns.set_style("darkgrid")
    sns.lineplot(x="Timestamp", y="Axie1", data=df[-100:], marker='.')
    sns.lineplot(x="Timestamp", y="Axie2", data=df[-100:], marker='.')
    sns.lineplot(x="Timestamp", y="Axie3", data=df[-100:], marker='.')
    plt.ylabel("ETH Price")
    plt.legend(labels=["Axie1", "Axie2", "Axie3"])
    plt.tight_layout()
    plt.savefig("market.png")
    plt.close()

@bot.command()
async def market(ctx, q1='https://marketplace.axieinfinity.com/axie/?class=Bird&part=mouth-doubletalk&part=horn-eggshell&part=back-pigeon-post&part=tail-post-fight&speed=61&speed=61&auctionTypes=Sale', q2='https://marketplace.axieinfinity.com/axie/?class=Aquatic&part=horn-anemone&part=back-anemone&part=tail-nimo&part=mouth-lam&speed=57&speed=61&auctionTypes=Sale', q3='https://marketplace.axieinfinity.com/axie/?class=Plant&part=back-bidens&part=horn-cactus&part=mouth-zigzag&part=tail-hot-butt&hp=61&hp=61&auctionTypes=Sale'):
    global reset_flag
    df = pd.DataFrame({'Timestamp': [], 'Axie1': [], 'Axie2': [], 'Axie3': []})
    
    while True:
        if reset_flag == True:
            break
        try:
            ethusd = get_exchange_rate()
            content, prices = axie.message([q1, q2, q3], ethusd)
            
            df = df.append({'Timestamp': datetime.now(), 'Axie1': prices[0], 'Axie2': prices[1], 'Axie3': prices[2]}, ignore_index=True)
            plot_fig(df)
            file = discord.File("market.png", filename='market.png')
            embed = discord.Embed(color=0xff0000)
            embed.description = content
            embed = embed.set_image(url="attachment://market.png")
            await ctx.send(file=file, embed=embed)
            await asyncio.sleep(10)

        except Exception as e:
            await ctx.send(f"An error occured: {e}")
    reset_flag = False

with open("auth.json") as f:
    data = json.load(f)
    bot.run(data["private_key"])
