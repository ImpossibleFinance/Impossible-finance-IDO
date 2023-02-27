import json

from scripts.upload_functions import *
from scripts.functions import *



def remove_IDO(name):
    for token in ['BUSD', 'IDIA']:
        file_path = 'data/' + str(token) +'_to_pools_transactions.csv'
        if os.stat(file_path).st_size == 0 or os.stat(file_path).st_size == 1:
            csv_data = pd.DataFrame()
        else:
            csv_data = pd.read_csv(file_path)

            csv_data = csv_data[csv_data['launchpad'] != name]

            csv_data.to_csv('data/' + token +'_to_pools_transactions.csv', index = False)

pool_addresses = []
accepted_currency = []
launchpad = []

f = open('config/IDO_pools.json')
IDO_pools = json.load(f)

csv_data = load_full_csv_data()
if csv_data.empty == False:
    all_uploaded_IDOs = csv_data['launchpad'].unique()
else:
    all_uploaded_IDOs = []

##############################################################################
###################### Check upload option ###################################
##############################################################################

print('Please select upload option:')
print('(a) Upload new IDOs')
print('(b) Upload specific IDO (Example, if you want to upload PINE IDO: "b PINE")')
option = input('Type your option: ')

for item in IDO_pools:
    if str(item['launchpad']) not in all_uploaded_IDOs and option == 'a':
        pool_addresses.append((item['pool_address']).lower())
        launchpad.append(item['launchpad'])

        if item['sale_type'] != 'Unlimited IDIA Sale':
            accepted_currency.append('BUSD')
        else:
            accepted_currency.append('IDIA')
    if (option.split())[0] == 'b' and str(item['launchpad']) == (option.split())[1]:
        pool_addresses.append((item['pool_address']).lower())
        launchpad.append(item['launchpad'])

        if item['sale_type'] != 'Unlimited IDIA Sale':
            accepted_currency.append('BUSD')
        else:
            accepted_currency.append('IDIA')

        remove_IDO((option.split())[1])

pools_info = pd.DataFrame({'accepted_currency':accepted_currency, 'pool_addresses':pool_addresses, 'launchpad': launchpad})

for token in ['BUSD', 'IDIA']:
    if token == 'BUSD':
        pools_array = (pools_info[pools_info["accepted_currency"] == 'BUSD'])['pool_addresses'].to_numpy()

    if token == 'IDIA':
        pools_array = (pools_info[pools_info["accepted_currency"] == 'IDIA'])['pool_addresses'].to_numpy()
    
    
    transactions_to_pools(pools_array, token)

f.close()