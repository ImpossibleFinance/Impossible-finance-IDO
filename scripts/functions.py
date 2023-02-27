import pandas as pd
import json
import os


def load_full_csv_data():
    pool_addresses = []
    full_data = pd.DataFrame()
    currency = ['BUSD', 'IDIA']

    f = open('config/IDO_pools.json')
    IDO_pools = json.load(f)


    for item in IDO_pools:
        pool_addresses.append(item['pool_address'].lower())

    f.close()

    for token in currency:
        file_path = 'data/' + str(token) +'_to_pools_transactions.csv'
        if os.stat(file_path).st_size == 0 or os.stat(file_path).st_size == 1:
            print("Empty Data")
            return full_data
        df = pd.read_csv(file_path)
        df['hash'] = df['hash'].str.lower()
        df['from'] = df['from'].str.lower()
        df['to'] = df['to'].str.lower()
        if token == 'BUSD':
            df['USD_amount'] = df['amount']
        if token == 'IDIA':
            df['USD_amount'] = df['amount']*0.025/0.0136
        full_data = pd.concat([full_data, df])

    full_data = full_data.loc[(full_data['to']).isin(pool_addresses)]

    return full_data