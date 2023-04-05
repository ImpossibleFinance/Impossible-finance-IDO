from scripts.Functions import *
import pathlib

def load_full_csv_data_ido():
    pool_addresses = []
    full_data = pd.DataFrame()
    desktop = pathlib.Path("data")

    f = open('config/IDO_pools.json')
    IDO_pools = json.load(f)
    f.close()

    for item in IDO_pools:
        pool_addresses.append(item['pool_address'].lower())

    for item in desktop.iterdir():
        if str(item) != 'data/.DS_Store' and str(item) != 'data/Prices.csv':
            file_path = str(item)
            if os.stat(file_path).st_size == 0 or os.stat(file_path).st_size == 1:
                print("Empty Data")
                return full_data
            df = read_data_from_csv(file_path)

            if str(item).split("_")[1] in ['BUSD', 'USDC']:
                df['USD_amount'] = df['amount']
            if str(item).split("_")[1] == 'IDIA':
                df['USD_amount'] = df['amount']*0.025/0.0136
            full_data = pd.concat([full_data, df])

    full_data = full_data.loc[(full_data['to']).isin(pool_addresses)]

    return full_data



########################################################
################## KPI calculation ##################
########################################################

def main_kpis(full_data):
    total_unique_users = full_data['from'].nunique()
    total_usd_purchased = full_data['USD_amount'].sum()
    total_unique_purchase_txs = len(full_data)
    unique_IDOS = full_data['launchpad'].nunique()

    #last_ido_data = full_data[full_data['launchpad'] == (full_data['launchpad'].unique())[len(full_data['launchpad'].unique()) - 1]]
    #last_ido_unique_users = last_ido_data['from'].nunique()
    #last_ido_usd_purchased = last_ido_data['USD_amount'].sum()
    #last_ido_name = last_ido_data['launchpad'].unique()

    return total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs#, last_ido_unique_users, last_ido_usd_purchased, last_ido_name