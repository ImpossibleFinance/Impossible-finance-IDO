from requests import get
import pandas as pd
import json
from dotenv import load_dotenv
import os
import time


BASE_URL = "https://api.bscscan.com/api"
load_dotenv()
API_KEY = os.getenv('API_KEY')


def make_api_url(token_contract, address, **kwargs):
	url = BASE_URL + f"?module=account&action=tokentx&contractaddress={token_contract}&address={address}&apikey={API_KEY}"

	for key, value in kwargs.items():
		url += f"&{key}={value}"

	return url


def get_transactions(token_contract, address):
    transactions_url = make_api_url(
        token_contract,
        address, 
        startblock = 0, 
        endblock = 99999999, 
        page = 1,
        sort = "asc"
    )
    response = get(transactions_url)
    data = response.json()["result"]

    return data


def transactions_to_csv(token_contract ,address):


    f = open('IDO_pools.json')
    IDO_config = json.load(f)


    df = get_transactions(token_contract, address)

    df = pd.DataFrame(df)

    if df.empty:
        return df
    else:
        df['date'] = pd.to_datetime(df['timeStamp'],unit = 's')
        df = df[df.value != '0']
        df['amount'] = df['value'].astype(float)/10**(df['tokenDecimal'].astype(int))

        df = df.drop(['blockNumber', 'timeStamp', 'nonce', 'blockHash', 'tokenName', 'transactionIndex', 'gas', 'gasPrice', 'gasUsed', 'cumulativeGasUsed', 'input', 'confirmations', 'value', 'tokenDecimal'], axis=1)
        df['launchpad'] = ((list(filter(lambda x:x["pool_address"] == address, IDO_config)))[0]["launchpad"])
        df['sale_type'] = ((list(filter(lambda x:x["pool_address"] == address, IDO_config)))[0]["sale_type"])
        print(df)
        print((list(filter(lambda x:x["pool_address"] == address, IDO_config)))[0]["sale_type"])
        print((list(filter(lambda x:x["pool_address"] == address, IDO_config)))[0]["launchpad"])

        return df


def transactions_to_pools(pool_addresses, token):
    full_data = pd.DataFrame()

    if token == 'BUSD':
        token_contract = '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56'
    if token == 'IDIA':
        token_contract = '0x0b15Ddf19D47E6a86A56148fb4aFFFc6929BcB89'

    for j in range(len(pool_addresses)):
        time.sleep(0.2)

        print(str(j) + '/' + str(len(pool_addresses)))

        address = pool_addresses[j]

        full_data = pd.concat([full_data, transactions_to_csv(token_contract, address)])

    full_data.to_csv('transactions_data/' + token +'_to_pools_transactions.csv', index = False)