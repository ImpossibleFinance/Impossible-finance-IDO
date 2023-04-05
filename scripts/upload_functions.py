from requests import get
import pandas as pd
import json
from dotenv import load_dotenv
import os
import time


load_dotenv()
API_KEY_BNB = os.getenv('API_KEY_BNB')
API_KEY_ARB = os.getenv('API_KEY_ARB')


def make_api_url(blockchain, token_contract, address, **kwargs):
    if blockchain == 'bnb':
        BASE_URL = "https://api.bscscan.com/api"
        url = BASE_URL + f"?module=account&action=tokentx&contractaddress={token_contract}&address={address}&apikey={API_KEY_BNB}"

        for key, value in kwargs.items():
            url += f"&{key}={value}"
    
    if blockchain == 'arbitrum':
        BASE_URL = "https://api.arbiscan.io/api"
        url = BASE_URL + f"?module=account&action=tokentx&contractaddress={token_contract}&address={address}&apikey={API_KEY_ARB}"

        for key, value in kwargs.items():
            url += f"&{key}={value}"
    return url


def get_transactions(blockchain, token_contract, address):
    transactions_url = make_api_url(
        blockchain,
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


def transactions_to_csv(blockchain, token_contract ,address):


    f = open('config/IDO_pools.json')
    IDO_config = json.load(f)

    df = get_transactions(blockchain, token_contract, address)

    df = pd.DataFrame(df)

    if df.empty:
        return df
    else:
        df['date'] = pd.to_datetime(df['timeStamp'],unit = 's')
        df = df[df.value != '0']
        df['amount'] = df['value'].astype(float)/10**(df['tokenDecimal'].astype(int))

        df = df.drop(['blockNumber', 'timeStamp', 'nonce', 'blockHash', 'tokenName', 'transactionIndex', 'gas', 'gasPrice', 'gasUsed', 'cumulativeGasUsed', 'input', 'confirmations', 'value', 'tokenDecimal'], axis=1)
        df['launchpad'] = ((list(filter(lambda x:(x["pool_address"]).lower() == address and x["blockchain"] == blockchain, IDO_config)))[0]["launchpad"])
        df['sale_type'] = ((list(filter(lambda x:(x["pool_address"]).lower() == address and x["blockchain"] == blockchain, IDO_config)))[0]["sale_type"])
        print(df)
        print(df['launchpad'].unique(), '--', df['sale_type'].unique())

        return df


def transactions_to_pools(pool_addresses, token, blockchain):

    f = open('config/Currency_addresses.json')
    Currency_addresses = json.load(f)
    f.close()

    full_data = pd.DataFrame()

    for item in Currency_addresses:
        if item['name'] == token and item['blockchain'] == blockchain:
            token_contract = item['contract_address']

    for j in range(len(pool_addresses)):

        print(str(j) + '/' + str(len(pool_addresses)))

        address = pool_addresses[j]

        file_path = 'data/' + str(blockchain) + '_' + str(token) +'_to_pools_transactions.csv'
        if os.stat(file_path).st_size == 0 or os.stat(file_path).st_size == 1:
            csv_data = pd.DataFrame()
        else:
            csv_data = pd.read_csv(file_path)

        full_data = pd.concat([csv_data, transactions_to_csv(blockchain, token_contract, address)])

        full_data.to_csv('data/' + blockchain + '_' + token +'_to_pools_transactions.csv', index = False)

        time.sleep(0.4)