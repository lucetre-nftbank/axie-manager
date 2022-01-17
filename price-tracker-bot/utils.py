import seaborn as sns
import matplotlib.pyplot as plt
import json
import requests

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

def get_optimal_deck(addr):
    url = f"https://tracking.skymavis.com/battle-history?type=pvp&player_id={addr}"
    response = requests.request("GET", url)
    battles = json.loads(response.text)["battles"]

    deck_dict = {}
    most_freq = 0
    for battle in battles:
        team1 = tuple(sorted(battle['first_team_fighters']))
        if team1 in deck_dict:
            deck_dict[team1] += 1
        else:
            deck_dict[team1] = 1

        if most_freq < deck_dict[team1]:
            most_freq = deck_dict[team1]
            opt_deck = team1

        team2 = tuple(sorted(battle['second_team_fighters']))
        if team2 in deck_dict:
            deck_dict[team2] += 1
        else:
            deck_dict[team2] = 1

        if most_freq < deck_dict[team2]:
            most_freq = deck_dict[team2]
            opt_deck = team2
    return opt_deck, most_freq
