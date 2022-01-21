import requests
import json
from datetime import datetime

class AxieCriterion:
    def __init__(self, query):
        url, params = query.split('?')
        classes = []
        parts = []
        speeds = []
        hps = []
        skills = []
        morales = []
        for param in params.split('&'):
            attr, val = param.split('=')
            if attr == 'class':
                classes.append(val)
            elif attr == 'part':
                parts.append(val)
            elif attr == 'speed':
                speeds.append(int(val))
            elif attr == 'hp':
                hps.append(int(val))
            elif attr == 'skill':
                skills.append(int(val))
            elif attr == 'morale':
                morales.append(int(val))
                
        speeds = sorted(speeds)
        hps = sorted(hps)
        skills = sorted(skills)
        morales = sorted(morales)
        
        self.body = {
            "operationName": "GetAxieBriefList",
            "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String, $filterStuckAuctions: Boolean) {\n  axies(\n    auctionType: $auctionType\n    criteria: $criteria\n    from: $from\n    sort: $sort\n    size: $size\n    owner: $owner\n    filterStuckAuctions: $filterStuckAuctions\n  ) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n",
            "variables": {
                "auctionType": "Sale",
                "criteria": {
                    "bodyShapes": None,
                    "breedable": None,
                    "breedCount": None,
                    "classes": classes,
                    "hp": [],
                    "morale": [],
                    "numJapan": None,
                    "numMystic": None,
                    "numXmas": None,
                    "parts": parts,
                    "pureness": None,
                    "purity": [],
                    "region": None,
                    "skill": [],
                    "speed": [],
                    "stages": None,
                    "title": None
                },
                "filterStuckAuctions": True,
                "from": 0,
                "owner": None,
                "size": 24,
                "sort": "PriceAsc"
            }
        }
        if len(speeds) == 2:
            self.body["variables"]["criteria"]["speed"] = speeds
        if len(hps) == 2:
            self.body["variables"]["criteria"]["hp"] = hps
        if len(skills) == 2:
            self.body["variables"]["criteria"]["skill"] = skills
        if len(morales) == 2:
            self.body["variables"]["criteria"]["morale"] = morales
        
    def marketplace(self):
        r = requests.post("https://graphql-gateway.axieinfinity.com/graphql", json=self.body)
        data = json.loads(r.text)['data']['axies']
        return data
    

def message(queries, ethusd):
    
    header = f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n\n'
    content = ''
    prices = []
    
    for i, query in enumerate(queries):
        ac = AxieCriterion(query)
        data = ac.marketplace()
        total = data['total']
        criteria = ac.body["variables"]["criteria"]

        content += f'[Axie {i+1} Marketplace]({query}) - Total {total}\n'
        content += f'```Class: {json.dumps(criteria["classes"])}\nPart: {json.dumps(criteria["parts"])}'
        if len(criteria["speed"]) == 2:
            content += f'\nSpeed: {json.dumps(criteria["speed"])}'
        if len(criteria["hp"]) == 2:
            content += f'\nHP: {json.dumps(criteria["hp"])}'
        if len(criteria["skill"]) == 2:
            content += f'\nSkill: {json.dumps(criteria["skill"])}'
        if len(criteria["morale"]) == 2:
            content += f'\nMorale: {json.dumps(criteria["morale"])}'
        content += '```'
        
        axie = data['results'][0]
        ethprice = round(float(axie["auction"]["currentPriceUSD"])/ethusd, 3)
        footer = f'{ethprice} ETH - [{axie["id"]}](https://marketplace.axieinfinity.com/axie/{axie["id"]}) ({axie["name"]})\n\n'
        prices.append(ethprice)
        
        content += footer
        
    
    return header+content, prices