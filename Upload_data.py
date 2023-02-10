import json

from Upload_functions import *


pool_addresses = []
accepted_currency = []

f = open('IDO_pools.json')
IDO_pools = json.load(f)


for item in IDO_pools:
    pool_addresses.append(item['pool_address'])

    if item['sale_type'] != 'Unlimited IDIA Sale':
        accepted_currency.append('BUSD')
    else:
        accepted_currency.append('IDIA')

pools_info = pd.DataFrame({'accepted_currency':accepted_currency, 'pool_addresses':pool_addresses})

for token in ['BUSD', 'IDIA']:
    if token == 'BUSD':
        pools_array = (pools_info[pools_info["accepted_currency"] == 'BUSD'])['pool_addresses'].to_numpy()

    if token == 'IDIA':
        pools_array = (pools_info[pools_info["accepted_currency"] == 'IDIA'])['pool_addresses'].to_numpy()
    
    
    transactions_to_pools(pools_array, token)

f.close()