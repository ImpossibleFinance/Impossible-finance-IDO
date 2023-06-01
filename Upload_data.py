import json
import requests
import pathlib

from scripts.upload_functions import *
from scripts.Functions import *
from scripts.local_functions import *


class UploadPrices():

    def __init__(self):

        self.params = {
            'vs_currency': 'usd',
            'days': 'max',
            'interval': 'daily'
        }


        f = open('config/IDO_token_contracts.json')
        self.IDO_token_contracts = json.load(f)
        f.close()

        self.file_path = 'data/Prices.csv'


    def get_price(self, token):
        url = 'https://api.coingecko.com/api/v3/coins/'+ token +'/market_chart'

        response = requests.get(url, params = self.params)

        print(token)

        data = response.json()
        data = pd.DataFrame(data['prices'], columns=['Uni_time', 'Price'])
        data['date'] = pd.to_datetime(data['Uni_time']/1000, unit = 's')
        data = data.sort_values(by = ['date'], ascending = True)


        first_two_year_data = pd.DataFrame(data[:720]['Price'], columns=['Price'])
        first_two_year_data['Price'] = first_two_year_data['Price'].astype(float)
        first_two_year_data['days_from_ido'] = first_two_year_data.index
        first_two_year_data.round(3)

        return first_two_year_data

    def upload_prices(self):

        k = 0
        for item in self.IDO_token_contracts:

            print(str(k) + '/' + str(len(self.IDO_token_contracts)))

            token = str(item['api_token'])
            ido_price = float(item['ido_price'])

            csv_data = pd.DataFrame()

            if token != '-':
                price_data = self.get_price(token)
                price_data['roi'] = price_data['Price']/ido_price

                data = pd.concat([csv_data, price_data])

                data.to_csv('data/Prices.csv', index = False)

                time.sleep(0.5)

            k += 1


def unique_currency(item):
    if item['sale_type'] == 'Unlimited IDIA Sale' and item['launchpad'] == 'Ouro':
        return 'IDIA'
    if item['blockchain'] == 'arbitrum' and item['launchpad'] == 'Arken':
        return 'USDC'
    
    return 'BUSD'

def remove_IDO(name):
    desktop = pathlib.Path("data")

    for item in desktop.iterdir():
        if str(item) != 'data/.DS_Store' and str(item) != 'data/Prices.csv':
            file_path = str(item)
            if os.stat(file_path).st_size == 0 or os.stat(file_path).st_size == 1:
                csv_data = pd.DataFrame()
            else:
                csv_data = pd.read_csv(file_path)

                csv_data = csv_data[csv_data['launchpad'] != name]

                csv_data.to_csv(file_path, index = False)


def upload_transactions():
    pool_addresses = []
    accepted_currency = []
    launchpad = []
    blockchain = []

    f = open('config/IDO_pools.json')
    IDO_pools = json.load(f)

    csv_data = load_full_csv_data_ido()
    if csv_data.empty == False:
        all_uploaded_IDOs = csv_data['launchpad'].unique()
    else:
        all_uploaded_IDOs = []

    ##############################################################################
    ###################### Check upload option ###################################
    ##############################################################################

    print('----------------------------')
    print('Please select upload option:')
    print('(a) Upload new IDOs')
    print('(b) Upload specific IDO (Example, if you want to upload PINE IDO: "b PINE")')
    option = input('Type your option: ')

    for item in IDO_pools:
        if str(item['launchpad']) not in all_uploaded_IDOs and option == 'a':
            pool_addresses.append((item['pool_address']).lower())
            blockchain.append(item['blockchain'])
            launchpad.append(item['launchpad'])

            accepted_currency.append(unique_currency(item))

        if (option.split())[0] == 'b' and str(item['launchpad']) == (option.split())[1]:
            pool_addresses.append((item['pool_address']).lower())
            blockchain.append(item['blockchain'])
            launchpad.append(item['launchpad'])

            accepted_currency.append(unique_currency(item))

            remove_IDO((option.split())[1])

    pools_info = pd.DataFrame({'accepted_currency':accepted_currency, 'pool_addresses':pool_addresses, 'launchpad': launchpad, 'blockchain': blockchain})

    for blockchains in pools_info['blockchain'].unique():
        pools_array = (pools_info[pools_info["blockchain"] == blockchains])

        for token in pools_array['accepted_currency'].unique():
            pools_array = (pools_array[pools_array["accepted_currency"] == token])['pool_addresses'].to_numpy()

            transactions_to_pools(pools_array, token, blockchains)

    f.close()

print ('Option (1) - Upload Transactions Data' )
print ('Option (2) - Upload Prices Data' )
print ('Option (3) - Exit' )
opt = input('Your option: ')

prices = UploadPrices()

if opt == '1':
    upload_transactions()
if opt == '2':
    prices.upload_prices()