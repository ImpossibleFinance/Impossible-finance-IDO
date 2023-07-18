from scripts.Functions import *

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
        if str(item) == 'data/full_transactions_data.csv':
            file_path = str(item)
            if os.stat(file_path).st_size == 0 or os.stat(file_path).st_size == 1:
                print("Empty Data")
                return full_data
            df = read_data_from_csv(file_path)

            df['USD_amount'] = df['amount']*df['token_price']

            full_data = pd.concat([full_data, df])

    return full_data

def load_prices_csv_data():
    path = 'data/Prices.csv'

    prices_data = read_data_from_csv(path)

    prices_data = prices_data.rename(columns = {
        "days_from_ido": "Days after IDO", 
        "roi": "ROI",
        "token": "Token"
    })

    return prices_data

def load_staking_csv_data():

    path = 'data/staking_transactions_data.csv'

    staking_data = read_data_from_csv(path)
    staking_data = staking_data.sort_values(by = ['date'], ascending = True)
    staking_data = staking_data.reset_index(drop = True)
    staking_data['value'] = staking_data['value'].astype(float)
    staking_data['net_amt'] = np.where(staking_data['category'] == 'Stake', +1*staking_data['value']/10**18, -1*staking_data['value']/10**18)
    staking_data['token'] = np.where(staking_data['sale_type'].str.contains('vIDIA'), 'vIDIA', 'IDIA')


    return staking_data


########################################################
################## KPI calculation #####################
########################################################

def main_kpis(full_data):
    total_unique_users = full_data['from'].nunique()
    total_usd_purchased = full_data['USD_amount'].sum()
    total_unique_purchase_txs = len(full_data)
    unique_IDOS = int(full_data['launchpad'].nunique())

    #last_ido_data = full_data[full_data['launchpad'] == (full_data['launchpad'].unique())[len(full_data['launchpad'].unique()) - 1]]
    #last_ido_unique_users = last_ido_data['from'].nunique()
    #last_ido_usd_purchased = last_ido_data['USD amount'].sum()
    #last_ido_name = last_ido_data['launchpad'].unique()

    return total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs#, last_ido_unique_users, last_ido_usd_purchased, last_ido_name

########################################################
############### PIE/BARS FIRST PART CHARTS #############
########################################################

class Main_Purchased_Info():
    def __init__(self, full_data):

        self.data = full_data

        #print(full_data['launchpad'][1])
        #print(full_data['launchpad'][72243])
        
        self.data = self.data.rename(
            columns = {
                "USD_amount": "USD amount", 
                "from": "Buyer", 
                "sale_type": "Sale type"
            })
        
        f = open('config/IDO_pools.json')
        self.sales_config = json.load(f)
        f.close()

        # MAIN

        _df_USD_by_launchpad = pd.DataFrame(self.data.groupby('launchpad')['USD amount'].sum())
        _df_USD_by_launchpad['Launchpad (IDO)'] = _df_USD_by_launchpad.index.get_level_values(0)
        _df_USD_by_launchpad = _df_USD_by_launchpad.reset_index(drop = True)

        _df_Participants_by_launchpad = pd.DataFrame(self.data.groupby('launchpad')['Buyer'].nunique())
        _df_Participants_by_launchpad['Launchpad (IDO)'] = _df_Participants_by_launchpad.index.get_level_values(0)
        _df_Participants_by_launchpad = _df_Participants_by_launchpad.reset_index(drop = True)


        self.df_USD_and_Participants = _df_USD_by_launchpad.merge(_df_Participants_by_launchpad, on = 'Launchpad (IDO)', how = 'left')
        #print(self.df_USD_and_Participants)
        self.df_USD_and_Participants['order'] = [(list(filter(lambda x:x["launchpad"] == y, self.sales_config)))[0]['launch_order'] for y in self.df_USD_and_Participants['Launchpad (IDO)']]
        self.df_USD_and_Participants['order'] = self.df_USD_and_Participants['order'].astype('int')
        self.df_USD_and_Participants = self.df_USD_and_Participants.sort_values(by = ['order'], ascending = True)


        # BY SALE TYPE

        self.df_USD_by_sale_type = pd.DataFrame(self.data.groupby(['launchpad', 'Sale type'])['USD amount'].sum())
        self.df_USD_by_sale_type['Launchpad (IDO)'] = self.df_USD_by_sale_type.index.get_level_values(0)
        self.df_USD_by_sale_type['Sale type'] = self.df_USD_by_sale_type.index.get_level_values(1)
        self.df_USD_by_sale_type = self.df_USD_by_sale_type.reset_index(drop = True)

        self.df_Participants_by_sale_type = pd.DataFrame(self.data.groupby(['launchpad', 'Sale type'])['Buyer'].nunique())
        self.df_Participants_by_sale_type['Launchpad (IDO)'] = self.df_Participants_by_sale_type.index.get_level_values(0)
        self.df_Participants_by_sale_type['Sale type'] = self.df_Participants_by_sale_type.index.get_level_values(1)
        self.df_Participants_by_sale_type = self.df_Participants_by_sale_type.reset_index(drop = True)

        self.df_USD_by_sale_type['order'] = [(list(filter(lambda x:x["launchpad"] == y, self.sales_config)))[0]['launch_order'] for y in self.df_USD_by_sale_type['Launchpad (IDO)']]
        self.df_USD_by_sale_type['order'] = self.df_USD_by_sale_type['order'].astype('int')

        self.result_data_by_sale_type = pd.merge(self.df_USD_by_sale_type, self.df_Participants_by_sale_type, on = ['Launchpad (IDO)','Sale type'])
        self.result_data_by_sale_type = self.result_data_by_sale_type.sort_values(by = ['order'], ascending = True)

        # BY USER TYPE

        self.df_user_type = pd.DataFrame(self.data.groupby(['launchpad', 'Buyer'])['USD amount'].sum())
        self.df_user_type['Launchpad (IDO)'] = self.df_user_type.index.get_level_values(0)
        self.df_user_type['Buyer'] = self.df_user_type.index.get_level_values(1)
        self.df_user_type = self.df_user_type.reset_index(drop = True)

        self.df_user_type['state'] = np.where(self.df_user_type['USD amount'] < 10, '0-10 USD',
            np.where((self.df_user_type['USD amount'] >= 10) & (self.df_user_type['USD amount'] < 100), '10-100 USD',
            np.where((self.df_user_type['USD amount'] >= 100) & (self.df_user_type['USD amount'] < 1000), '100-1000 USD', 
            np.where((self.df_user_type['USD amount'] >= 1000) & (self.df_user_type['USD amount'] < 5000), '1000-5000 USD', '>5000 USD'))))

    def by_launchpad(self):

        USD_and_participants = create_ez_bar(
            self.df_USD_and_Participants,
            'Launchpad (IDO)',
            'USD amount',
            'Buyer',
            None,
            None,
            False,
            ['#DAA520', '#8A2BE2']
        )

        return USD_and_participants
    

    def by_sale_type(self):

        fig_USD_by_sale = create_ez_bar(
            self.result_data_by_sale_type,
            'Launchpad (IDO)',
            'USD amount',
            None,
            'Sale type',
            None,
            True,
            []
        )

        fig_participants_by_sale = create_ez_bar(
            self.result_data_by_sale_type,
            'Launchpad (IDO)',
            'Buyer',
            None,
            'Sale type',
            None,
            True,
            []
        )

        fig_USD_by_sale.update_xaxes(categoryorder = 'array', categoryarray = self.result_data_by_sale_type['Launchpad (IDO)'])
        fig_participants_by_sale.update_xaxes(categoryorder = 'array', categoryarray = self.result_data_by_sale_type['Launchpad (IDO)'])

        return fig_USD_by_sale, fig_participants_by_sale

    def user_type(self):

        ###### USD by USD amount ######

        users_usd = pd.DataFrame(self.df_user_type.groupby(['Launchpad (IDO)', 'state'])['USD amount'].sum())
        users_usd['Launchpad (IDO)'] = users_usd.index.get_level_values(0)
        users_usd['state'] = users_usd.index.get_level_values(1)
        users_usd = users_usd.reset_index(drop = True)

        users_usd['order'] = [(list(filter(lambda x:x["launchpad"] == y, self.sales_config)))[0]['launch_order'] for y in users_usd['Launchpad (IDO)']]
        users_usd['order'] = users_usd['order'].astype('int')

        ###### Users by USD amount ######

        users = pd.DataFrame(self.df_user_type.groupby(['Launchpad (IDO)', 'state'])['Buyer'].nunique())
        users['Launchpad (IDO)'] = users.index.get_level_values(0)
        users['state'] = users.index.get_level_values(1)
        users = users.reset_index(drop = True)

        result_data = pd.merge(users_usd, users, on = ['Launchpad (IDO)','state'])
        result_data = result_data.sort_values(by=['order'], ascending = True)

        fig_USD_by_sale = create_ez_bar(
            result_data,
            'Launchpad (IDO)',
            'USD amount',
            None,
            'state',
            None,
            False,
            []
        )
        
        fig_participants_by_sale = create_ez_bar(
            result_data,
            'Launchpad (IDO)',
            'Buyer',
            None,
            'state',
            None,
            False,
            []
        )

        fig_USD_by_sale.update_xaxes(categoryorder = 'array', categoryarray = self.result_data_by_sale_type['Launchpad (IDO)'])
        fig_participants_by_sale.update_xaxes(categoryorder = 'array', categoryarray = self.result_data_by_sale_type['Launchpad (IDO)'])


        return fig_USD_by_sale, fig_participants_by_sale
    

class Purchase_Rate():

    def __init__(self, full_data):
        f = open('config/IDO_pools.json')
        self.sales_config = json.load(f)

        f2 = open('config/IDO_token_contracts.json')
        self.tokens_config = json.load(f2)

        f.close()
        f2.close()

        self.data = pd.DataFrame(full_data.groupby(['launchpad', 'sale_type'])['USD_amount'].sum())
        self.data['launchpad'] = self.data.index.get_level_values(0)
        self.data['sale_type'] = self.data.index.get_level_values(1)
        self.data = self.data.reset_index(drop = True)

        self.data['order'] = [(list(filter(lambda x:x["launchpad"] == y, self.sales_config)))[0]['launch_order'] for y in self.data['launchpad']]
        self.data['order'] = self.data['order'].astype('int')

        self.data['price'] = [(list(filter(lambda x:x["launchpad"] == y, self.tokens_config)))[0]['ido_price'] for y in self.data['launchpad']]
        self.data['price'] = self.data['price'].astype('float')

        self.add_max_size(self.sales_config)

        self.data['max_size'] = self.data['price']*self.data['size']
        self.data = self.data.drop(['price', 'size'], axis=1)

        self.data['purchased_rate'] = 100*self.data['USD_amount']/self.data['max_size']

        self.data = self.data.sort_values(by = ['order'], ascending = True)
        self.data = self.data.reset_index(drop = True)

        self.data = self.data.rename(
            columns = {
                "purchased_rate": "Purchase Rate", 
                "launchpad": "Launchpad (IDO)", 
                "sale_type": "Sale type"
            })

    def add_max_size(self, config):

        launchpad = []
        sale_type = []
        size = []

        for item in config:
            launchpad.append(item['launchpad'])
            sale_type.append(item['sale_type'])
            size.append(item['size'])

        pool_size = pd.DataFrame({
            'launchpad':launchpad, 
            'sale_type':sale_type, 
            'size': size
        })
        pool_size['size'] = pool_size['size'].astype('int')

        self.data = pd.merge(self.data, pool_size, on = ['launchpad', 'sale_type'])

    def total_rate(self):

        self.fig_purchased_rate = create_ez_scatters(
            self.data,
            'Launchpad (IDO)',
            'Purchase Rate',
            None,
            'Sale type',
            None,
            []
        )

        self.fig_purchased_rate.update_xaxes(categoryorder = 'array', categoryarray = self.data['Launchpad (IDO)'])

        return self.fig_purchased_rate
    
    def rate_per_pool(self):
        total_data = pd.DataFrame(self.data.groupby(['Launchpad (IDO)']).sum())
        total_data['launchpad'] = total_data.index.get_level_values(0)
        total_data = total_data.reset_index(drop=True)

        total_data['rate'] = 100*total_data['USD_amount']/total_data['max_size']

        total_data = total_data.sort_values(by = ['order'], ascending = True)
        total_data = total_data.reset_index(drop = True)

        return create_ez_kpi(total_data['launchpad'], total_data['rate'], '', '', True)
    



########################################################
################# Staking main #########################
########################################################


class Staking():

    def __init__(self, full_data):

        self.staking_data = full_data.copy()



    def main_kpi(self):

        self.total_unique_stakers = self.staking_data['user'].nunique()
        self.staking_peak = self.staking_data['net_amt'].cumsum().max()

        return create_ez_kpi(self.total_unique_stakers, [], 'Total unique IDO stakers', '', False), create_ez_kpi(self.staking_peak, [], 'Total amount staked at peak', '', False)
    

    def IDIA_vIDIA_kpis(self):

        IDIA_data = self.staking_data[self.staking_data['token'] == 'IDIA']
        vIDIA_data = self.staking_data[self.staking_data['token'] == 'vIDIA']

        IDIA_staking_peak = IDIA_data['net_amt'].cumsum().max()
        vIDIA_staking_peak = vIDIA_data['net_amt'].cumsum().max()

        IDIA_staking_now = IDIA_data['net_amt'].sum()
        vIDIA_staking_now = vIDIA_data['net_amt'].sum()

        ######################### IDIA ###########################

        IDIA_discription = pd.concat([
            pd.DataFrame({
                'net_amt': [IDIA_staking_peak],
                'contract': 'At Peak'
            }),

            pd.DataFrame({
                'net_amt': [IDIA_staking_now],
                'contract': 'Total Now'
            })
        ])

        IDIA_discription = pd.concat([IDIA_discription, (total_sum(IDIA_data, 'net_amt', 'contract')).drop(['value', 'trackID'], axis=1)])
        IDIA_discription = IDIA_discription.reset_index(drop = True)

        ######################### vIDIA ###########################

        vIDIA_discription = pd.concat([
            pd.DataFrame({
                'net_amt': [vIDIA_staking_peak],
                'contract': 'At Peak'
            }),

            pd.DataFrame({
                'net_amt': [vIDIA_staking_now],
                'contract': 'Total Now'
            })
        ])

        vIDIA_discription = pd.concat([vIDIA_discription, (total_sum(vIDIA_data, 'net_amt', 'contract')).drop(['value', 'trackID'], axis=1)])
        vIDIA_discription = vIDIA_discription.reset_index(drop = True)

        return create_ez_kpi(IDIA_discription['contract'], IDIA_discription['net_amt'], 'IDIA', '', False), create_ez_kpi(vIDIA_discription['contract'], vIDIA_discription['net_amt'], 'vIDIA', '', False)