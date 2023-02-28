import json
import requests


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


def upload_transactions():
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

    print('----------------------------')
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


def get_price(token):
    url = 'https://api.coingecko.com/api/v3/coins/'+ token +'/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': 'max'
    }

    response = requests.get(url, params=params)
    print(token)
    data = response.json()
    data = pd.DataFrame(data['prices'], columns=['Uni_time', 'Price'])
    data['date'] = pd.to_datetime(data['Uni_time']/1000, unit = 's')
    data = data.sort_values(by = ['date'], ascending = True)
    first_half_year_data = pd.DataFrame(data[:180]['Price'], columns=['Price'])
    first_half_year_data['Price'] = first_half_year_data['Price'].astype(float)
    first_half_year_data['token'] = token
    first_half_year_data['days_from_ido'] = first_half_year_data.index
    first_half_year_data.round(3)

    return first_half_year_data

def upload_prices():

    f = open('config/IDO_token_contracts.json')
    IDO_token_contracts = json.load(f)

    k = 0
    for item in IDO_token_contracts:

        print(str(k) + '/' + str(len(IDO_token_contracts)))

        token = str(item['api_token'])
        ido_price = float(item['ido_price'])

        price_data = get_price(token)
        price_data['roi'] = price_data['Price']/ido_price

        file_path = 'data/Prices.csv'
        if os.stat(file_path).st_size == 0 or os.stat(file_path).st_size == 1:
            csv_data = pd.DataFrame()
        else:
            csv_data = pd.read_csv(file_path)

        data = pd.concat([csv_data, price_data])

        data.to_csv('data/Prices.csv', index = False)

        time.sleep(0.4)

        k += 1


print ('Option (1) - Upload Transactions Data' )
print ('Option (2) - Upload Prices Data' )
print ('Option (3) - Exit' )
opt = input('Your option: ')

if opt == '1':
    upload_transactions()
if opt == '2':
    upload_prices()