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


        #first_two_year_data = pd.DataFrame(data[:720]['Price'], columns=['Price'])
        data['Price'] = data['Price'].astype(float)
        data['days_from_ido'] = data.index
        data.round(3)

        return data

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
                price_data['token'] = token

                data = pd.concat([csv_data, price_data])

                data.to_csv('data/Prices.csv', index = False)

                time.sleep(1.5)

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
        if item['launch_order'] in ['18', '19']:
            return 'USDT'
            
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

        ########################################################
        ############ More than 10k txs optimizer ###############
        ########################################################


        _df = df.copy()

        if len(df) == 10000:
            while len(df) == 10000:

                max_blocknumber = df['blockNumber'][len(df)-1]

                df = pd.DataFrame(self.add_transactions_raw(blockchain, token_contract, address, max_blocknumber))

                _df = pd.concat([_df, df])

                time.sleep(0.2)

        df = _df.copy()
        df = df.drop_duplicates(subset = ['hash'])
        df = df.reset_index(drop = True)

        ########################################################
        ############## USDT on Arbitrum issues #################
        ########################################################

        if df.empty:
            df = self.get_transactions_raw_issue(blockchain, address)

            ########################################################
            ############ More than 10k txs optimizer ###############
            ########################################################


            _df = df.copy()

            if len(df) == 10000:
                while len(df) == 10000:

                    max_blocknumber = df['blockNumber'][len(df)-1]

                    df = pd.DataFrame(self.add_transactions_raw_issue(blockchain, address, max_blocknumber))

                    _df = pd.concat([_df, df])

                    time.sleep(0.2)

            df = _df.copy()
            df = df.drop_duplicates(subset = ['hash'])
            df = df.reset_index(drop = True)

            df = df[df['methodId'] == '0x01fc191c']
            df = df[df['txreceipt_status'] == '1']
            df = df.reset_index(drop = True)

            df['date'] = pd.to_datetime(df['timeStamp'],unit = 's')
            df['tokenSymbol'] = 'USDT'
            df['token_price'] = '1'
            
            df['launchpad'] = ((list(filter(lambda x:(x["pool_address"]).lower() == address and x["blockchain"] == blockchain, self.IDO_pools)))[0]["launchpad"])
            df['sale_type'] = ((list(filter(lambda x:(x["pool_address"]).lower() == address and x["blockchain"] == blockchain, self.IDO_pools)))[0]["sale_type"])

            df['blockchain'] = blockchain
            df['amount'] = ('0x' + df['input'].str[10:74]).apply(int, base = 16)/10**6

            df = df.drop([
                'blockNumber',
                'timeStamp', 
                'nonce', 
                'blockHash',
                'transactionIndex',
                'gas',
                'contractAddress',
                'cumulativeGasUsed',
                'gasUsed',
                'confirmations',
                'methodId',
                'functionName',
                'gasPrice',
                'isError',
                'txreceipt_status',
                'input',
                'value',
                'gasPriceBid'
            ], axis = 1)

            df = df.reindex(['hash','from','to','tokenSymbol','date','amount','token_price','launchpad','sale_type','blockchain'], axis=1)
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
    
    def add_transactions_raw(self, blockchain, token_contract, address, start_block):

        transactions_url = self.make_api_url(
            blockchain,
            token_contract,
            address, 
            startblock = start_block, 
            endblock = 99999999, 
            page = 1,
            sort = "asc"
        )

        response = requests.get(transactions_url)
        data = response.json()["result"]

        return pd.DataFrame(data)
    
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

        print(blockchain, token_contract, address, data)

        return pd.DataFrame(data)
    
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
    
    ########################################################
    ####################### IF ISSUE #######################
    ########################################################
    
    def add_transactions_raw_issue(self, blockchain, address, start_block):

        transactions_url = self.make_api_url_issue(
            blockchain,
            address, 
            startblock = start_block, 
            endblock = 99999999, 
            page = 1,
            sort = "asc"
        )

        response = requests.get(transactions_url)
        data = response.json()["result"]

        return pd.DataFrame(data)


    def get_transactions_raw_issue(self, blockchain, address):

        transactions_url = self.make_api_url_issue(
            blockchain,
            address, 
            startblock = 0, 
            endblock = 99999999, 
            page = 1,
            sort = "asc"
        )

        response = requests.get(transactions_url)
        data = response.json()["result"]

        print(blockchain, address, data)

        return pd.DataFrame(data)
    
    def make_api_url_issue(self, blockchain, address, **kwargs):
        if blockchain == 'bnb':
            BASE_URL = "https://api.bscscan.com/api"
            url = BASE_URL + f"?module=account&action=txlist&address={address}&apikey={self.API_KEY_BNB}"

            for key, value in kwargs.items():
                url += f"&{key}={value}"

        if blockchain == 'arbitrum':
            BASE_URL = "https://api.arbiscan.io/api"
            url = BASE_URL + f"?module=account&action=txlist&address={address}&apikey={self.API_KEY_ARB}"

            for key, value in kwargs.items():
                url += f"&{key}={value}"
        return url


class UploadStaking():

    def __init__(self):
        
        load_dotenv()
        self.API_KEY_BNB = os.getenv('API_KEY_BNB')
        self.API_KEY_ARB = os.getenv('API_KEY_ARB')


        f = open('config/IDO_pools.json')
        self.IDO_pools = json.load(f)
        f.close()

        self.file_path = 'data/staking_transactions_data.csv'

    
    def make_api_url(self, blockchain, address, **kwargs):
        if blockchain == 'bnb':
            BASE_URL = "https://api.bscscan.com/api"
            url = BASE_URL + f"?module=account&action=txlist&address={address}&apikey={self.API_KEY_BNB}"

            for key, value in kwargs.items():
                url += f"&{key}={value}"

        if blockchain == 'arbitrum':
            BASE_URL = "https://api.arbiscan.io/api"
            url = BASE_URL + f"?module=account&action=txlist&address={address}&apikey={self.API_KEY_ARB}"

            for key, value in kwargs.items():
                url += f"&{key}={value}"
        return url
    
    def get_transactions_raw(self, blockchain, address):

        transactions_url = self.make_api_url(
            blockchain,
            address, 
            startblock = 0, 
            endblock = 99999999, 
            page = 1,
            sort = "asc"
        )

        response = requests.get(transactions_url)
        data = response.json()["result"]

        return data

    def add_transactions_raw(self, blockchain, address, start_block):

        transactions_url = self.make_api_url(
            blockchain,
            address, 
            startblock = start_block, 
            endblock = 99999999, 
            page = 1,
            sort = "asc"
        )

        response = requests.get(transactions_url)
        data = response.json()["result"]

        return data
    
    def get_unique_contracts(self, contracts, chains):

        _a = []

        for i in range(len(contracts)):
            _a.append(str(contracts[i]) + '/' + str(chains[i]))

        check_old = input('Would you like to remove Old contracts and dont load it?[y/n] ')
        print('*'*80)


        if check_old == 'y':
            with open('config/Old_staking_contracts.txt') as f_old:
                old_contracts = [line.rstrip('\n') for line in f_old]
        else:
            old_contracts = []

        if len(old_contracts) != 0:
            return list(set(_a).difference(old_contracts))
        else:
            return list(set(_a))

    def transactions_from_api(self, chain, wallet):

        df = pd.DataFrame(self.get_transactions_raw(chain, wallet))

        _df = df.copy()

        if len(df) == 10000:
            while len(df) == 10000:

                max_blocknumber = df['blockNumber'][len(df)-1]

                df = pd.DataFrame(self.add_transactions_raw(chain, wallet, max_blocknumber))

                _df = pd.concat([_df, df])

                time.sleep(0.1)

        _df['date'] = pd.to_datetime(_df['timeStamp'],unit = 's')
        df = _df.copy()
        df = df.drop_duplicates(subset = ['hash'])
        df = (df.loc[df['methodId'].isin(['0x770c5c12', '0xcbc50245'])])
        df = df[df['txreceipt_status'] == '1']
        df = df.reset_index(drop = True)

        df['chain'] = chain
        df['category'] = np.where(df['methodId'] == '0x770c5c12', 'Stake', np.where(df['methodId'] == '0xcbc50245', 'Unstake', 'Undefined'))
        df['user'] = df['from']
        df['value'] = ('0x' + df['input'].str[74:139]).apply(int, base = 16)
        df['trackID'] = ('0x' + df['input'].str[10:74]).apply(int, base = 16)
        df['contract'] = wallet.lower()
        df = df.drop([
            'blockNumber',
            'timeStamp', 
            'nonce', 
            'blockHash',
            'transactionIndex',
            'from',
            'to',
            'gas',
            'contractAddress',
            'cumulativeGasUsed',
            'gasUsed',
            'confirmations',
            'methodId',
            'functionName',
            'gasPrice',
            'isError',
            'txreceipt_status',
            'input'
        ], axis = 1)

        return df

    def upload_transactions(self):

        staking_contracts = []
        blockchains = []
        trackIds = []
        launchpad = []
        sale_type = []

        for item in self.IDO_pools:
            try:
                staking_contracts.append(item['staking_contract'].lower())
                blockchains.append(item['blockchain'])
                trackIds.append(int(item['trackId']))
                launchpad.append(item['launchpad'])
                sale_type.append(item['sale_type'])
            except:
                pass
            
        pools_info = pd.DataFrame({
            'contract': staking_contracts, 
            'chain': blockchains, 
            'trackID': trackIds,
            'launchpad': launchpad,
            'sale_type': sale_type
        })

        
        unique_contracts = self.get_unique_contracts(staking_contracts, blockchains)

        unique_contracts_addresses = []
        for address in unique_contracts:
            unique_contracts_addresses.append(address.split('/')[0])

        if os.stat(self.file_path).st_size == 0 or os.stat(self.file_path).st_size == 1:
            self.full_data = pd.DataFrame()
        else:
            self.full_data = pd.read_csv(self.file_path)

            self.full_data = self.full_data.loc[~self.full_data['contract'].isin(unique_contracts_addresses)]

        for contract in tqdm(unique_contracts):

            _chain = contract.split('/')[1]
            _contract = contract.split('/')[0]
            self.full_data = pd.concat([self.full_data, self.transactions_from_api(_chain, _contract)])

        self.full_data = self.full_data.merge(pools_info, on = ['chain', 'contract', 'trackID'], how = 'left', indicator = True)
        
        self.full_data = self.full_data[self.full_data['_merge'] == 'both']
        self.full_data = self.full_data.drop([
            'gasPriceBid',
            '_merge'
        ], axis = 1)

        if 'launchpad_x' in self.full_data:

            self.full_data = self.full_data.drop([
                'launchpad_x',
                'sale_type_x'
            ], axis = 1)

            self.full_data = self.full_data.rename(columns = {
                "launchpad_y": "launchpad", 
                "sale_type_y": "sale_type"
            })

        self.full_data.to_csv(self.file_path, index = False)



print ('Option (1) - Upload Transactions Data' )
print ('Option (2) - Upload Prices Data' )
print ('Option (3) - Upload Staking Data' )
print ('Option (4) - Exit' )
opt = input('Your option: ')
print("="*80)


if opt == '1':
    transactions = UploadTransactions()
    transactions.upload_transactions()
if opt == '2':
    prices = UploadPrices()
    prices.upload_prices()
if opt == '3':
    staking = UploadStaking()
    staking.upload_transactions()


print("="*80)
print("Upload is done")
print("="*80)