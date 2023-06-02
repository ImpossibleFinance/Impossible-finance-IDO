import json
import requests
import pandas as pd
import time
from dotenv import load_dotenv
import os
from tqdm import tqdm

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
        for item in tqdm(self.IDO_token_contracts):

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



class UploadTransactions():

    def __init__(self):

        load_dotenv()
        self.API_KEY_BNB = os.getenv('API_KEY_BNB')
        self.API_KEY_ARB = os.getenv('API_KEY_ARB')

        self.file_path = 'data/full_transactions_data.csv'

        self.pool_addresses = []
        self.accepted_currency = []
        self.launchpad = []
        self.blockchain = []

        f = open('config/IDO_pools.json')
        self.IDO_pools = json.load(f)
        f.close()

        f2 = open('config/Currency_addresses.json')
        self.Currency_addresses = json.load(f2)
        f2.close()

        csv_data = load_full_csv_data_ido()
        if csv_data.empty == False:
            self.all_uploaded_IDOs = csv_data['launchpad'].unique()
        else:
            self.all_uploaded_IDOs = []

        ##############################################################################
        ###################### Check upload option ###################################
        ##############################################################################

        print('----------------------------')
        print('Current uploaded IDOs: ', self.all_uploaded_IDOs)
        print('Please select upload option:')
        print('(a) Upload new IDOs')
        print('(b) Upload specific IDO')
        print('[Example: if you want to upload Pine IDO: "b Pine" or upload Pine and Arken IDO: "b Pine,Arken" - with no space!]')
        self.option = input('Type your option: ')

        self.get_launchpads = (self.option[2:]).split(',')

    def remove_IDO(self, name):
        if os.stat(self.file_path).st_size == 0 or os.stat(self.file_path).st_size == 1:
            csv_data = pd.DataFrame()
        else:
            csv_data = pd.read_csv(self.file_path)

            csv_data = csv_data[csv_data['launchpad'] != name]

            csv_data.to_csv(self.file_path, index = False)

        return True

    def unique_currency(self, item):
        if item['sale_type'] == 'Unlimited IDIA Sale' and item['launchpad'] == 'Ouro':
            return 'IDIA'
        if item['blockchain'] == 'arbitrum' and item['launchpad'] == 'Arken':
            return 'USDC'
            
        return 'BUSD'
    
    def upload_transactions(self):
        for item in self.IDO_pools:
            if str(item['launchpad']) not in self.all_uploaded_IDOs and self.option == 'a':
                self.pool_addresses.append((item['pool_address']).lower())
                self.blockchain.append(item['blockchain'])
                self.launchpad.append(item['launchpad'])

                self.accepted_currency.append(self.unique_currency(item))

            if (self.option.split())[0] == 'b' and str(item['launchpad']) in self.get_launchpads:
                self.pool_addresses.append((item['pool_address']).lower())
                self.blockchain.append(item['blockchain'])
                self.launchpad.append(item['launchpad'])

                self.accepted_currency.append(self.unique_currency(item))

                self.remove_IDO(item['launchpad'])

        self.pools_info = pd.DataFrame({
            'accepted_currency': self.accepted_currency, 
            'pool_addresses': self.pool_addresses, 
            'launchpad': self.launchpad, 
            'blockchain': self.blockchain
        })

        for blockchain in self.pools_info['blockchain'].unique():
            pools_array = (self.pools_info[self.pools_info["blockchain"] == blockchain])
            for token in pools_array['accepted_currency'].unique():
                _pools_array = (pools_array[pools_array["accepted_currency"] == token])['pool_addresses'].to_numpy()
                self.get_transactions(_pools_array, token, blockchain)

    def get_transactions(self, pool_addresses, token, blockchain):

        for item in self.Currency_addresses:
            if item['name'] == token and item['blockchain'] == blockchain:
                _token_contract = item['contract_address']

        for j in tqdm(range(len(pool_addresses))):
            
            _address = pool_addresses[j]

            if os.stat(self.file_path).st_size == 0 or os.stat(self.file_path).st_size == 1:
                _csv_data = pd.DataFrame()
            else:
                _csv_data = pd.read_csv(self.file_path)

            _full_data = pd.concat([_csv_data, self.transactions_to_csv(blockchain, _token_contract, _address)])

            _full_data.to_csv(self.file_path, index = False)

            time.sleep(0.3)

    def transactions_to_csv(self, blockchain, token_contract ,address):

        df = self.get_transactions_raw(blockchain, token_contract, address)
        df = pd.DataFrame(df)

        if df.empty:
            return df
        else:
            df['date'] = pd.to_datetime(df['timeStamp'],unit = 's')
            df = df[df.value != '0']
            df['amount'] = df['value'].astype(float)/10**(df['tokenDecimal'].astype(int))

            df = df[df['to'].str.lower() == address.lower()]

            if address.lower() == ('0x0c8dF3f968eC9F2bf182C41C9D42d79dF4a31857').lower():
                df['token_price'] = 1.838
            else:
                df['token_price'] = 1

            df = df.drop([
                'contractAddress',
                'blockNumber', 
                'timeStamp', 
                'nonce', 
                'blockHash', 
                'tokenName', 
                'transactionIndex', 
                'gas', 
                'gasPrice', 
                'gasUsed', 
                'cumulativeGasUsed', 
                'input', 
                'confirmations', 
                'value', 
                'tokenDecimal'
            ], axis=1)

            df['launchpad'] = ((list(filter(lambda x:(x["pool_address"]).lower() == address and x["blockchain"] == blockchain, self.IDO_pools)))[0]["launchpad"])
            df['sale_type'] = ((list(filter(lambda x:(x["pool_address"]).lower() == address and x["blockchain"] == blockchain, self.IDO_pools)))[0]["sale_type"])

            df['blockchain'] = blockchain

            return df
        
    
    def get_transactions_raw(self, blockchain, token_contract, address):

        transactions_url = self.make_api_url(
            blockchain,
            token_contract,
            address, 
            startblock = 0, 
            endblock = 99999999, 
            page = 1,
            sort = "asc"
        )

        response = requests.get(transactions_url)
        data = response.json()["result"]

        return data
    
    def make_api_url(self, blockchain, token_contract, address, **kwargs):
        if blockchain == 'bnb':
            BASE_URL = "https://api.bscscan.com/api"
            url = BASE_URL + f"?module=account&action=tokentx&contractaddress={token_contract}&address={address}&apikey={self.API_KEY_BNB}"

            for key, value in kwargs.items():
                url += f"&{key}={value}"
        
        if blockchain == 'arbitrum':
            BASE_URL = "https://api.arbiscan.io/api"
            url = BASE_URL + f"?module=account&action=tokentx&contractaddress={token_contract}&address={address}&apikey={self.API_KEY_ARB}"

            for key, value in kwargs.items():
                url += f"&{key}={value}"
        return url


print ('Option (1) - Upload Transactions Data' )
print ('Option (2) - Upload Prices Data' )
print ('Option (3) - Exit' )
opt = input('Your option: ')

prices = UploadPrices()
transactions = UploadTransactions()

if opt == '1':
    transactions.upload_transactions()
if opt == '2':
    prices.upload_prices()