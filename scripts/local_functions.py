from scripts.Functions import *
import pathlib

import numpy as np

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
        
        self.data = self.data.rename(
            columns = {
                "USD_amount": "USD amount", 
                "from": "Buyer", 
                "sale_type": "Sale type"
            })

        # MAIN

        self.df_USD_by_launchpad = pd.DataFrame(self.data.groupby('launchpad')['USD amount'].sum())
        self.df_USD_by_launchpad['Launchpad (IDO)'] = self.df_USD_by_launchpad.index.get_level_values(0)
        self.df = self.df_USD_by_launchpad.reset_index(drop=True)

        self.df_Participants_by_launchpad = pd.DataFrame(self.data.groupby('launchpad')['Buyer'].nunique())
        self.df_Participants_by_launchpad['Launchpad (IDO)'] = self.df_Participants_by_launchpad.index.get_level_values(0)
        self.df_Participants_by_launchpad = self.df_Participants_by_launchpad.reset_index(drop=True)

        # BY SALE TYPE

        f = open('config/IDO_pools.json')
        self.sales_config = json.load(f)
        f.close()

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

        USD_fig = pie_distribution(self.df_USD_by_launchpad, 'Launchpad (IDO)', 'USD amount', '{text:,.2f}$')

        Participants_fig = pie_distribution(self.df_Participants_by_launchpad, 'Launchpad (IDO)', 'Buyer', '{text:,.0f}')

        return USD_fig, Participants_fig
    

    def by_sale_type(self):

        fig_USD_by_sale = distribution_bars(
            self.result_data_by_sale_type, 
            'Launchpad (IDO)', 
            'USD amount', 
            'Sale type', 
            False,
            'stack'
        )

        fig_USD_by_sale.update_xaxes(categoryorder = 'array', categoryarray = self.result_data_by_sale_type['Launchpad (IDO)'])

        fig_participants_by_sale = distribution_bars(
            self.result_data_by_sale_type, 
            'Launchpad (IDO)', 
            'Buyer', 
            'Sale type',
            False,
            'stack'
        )

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

        fig_USD_by_sale = distribution_bars(
            result_data, 
            'Launchpad (IDO)', 
            'USD amount', 
            'state', 
            False,
            False
        )
        
        fig_participants_by_sale = distribution_bars(
            result_data, 
            'Launchpad (IDO)', 
            'Buyer', 
            'state', 
            False,
            False
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

        self.unique_sale_type = self.data['sale_type'].unique()

        self.data = self.data.sort_values(by = ['order'], ascending = True)

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
        self.fig_max_pool_size = go.Figure()
        self.fig_purchased_rate = go.Figure()

        for sale in self.unique_sale_type:
            data_sale = self.data[self.data["sale_type"] == sale]

            if sale == 'Standard Sale' or sale == 'Unlimited Sale':
            
                self.fig_max_pool_size.add_trace(go.Bar(
                    x = data_sale["launchpad"], 
                    y = data_sale["max_size"],
                    name = sale,
                    marker_color = 'blue 'if sale == 'Standard Sale' else 'red',
                    hovertemplate = sale + ': $%{y:,.1f}<extra></extra>'
                    ))
                
                self.fig_purchased_rate.add_trace(go.Scatter(
                    x = data_sale["launchpad"], 
                    y = data_sale["purchased_rate"],
                    mode = 'markers',
                    name = sale,
                    marker_size = 12,
                    marker_color = 'blue 'if sale == 'Standard Sale' else 'red',
                    hovertemplate = sale + ': %{y:,.1f} %<extra></extra>'
                    ))
            else:

                self.fig_max_pool_size.add_trace(go.Bar(
                    x = data_sale["launchpad"], 
                    y = data_sale["max_size"],
                    name = sale,
                    hovertemplate = sale + ': $%{y:,.1f}<extra></extra>'
                    ))
                
                self.fig_purchased_rate.add_trace(go.Scatter(
                    x = data_sale["launchpad"], 
                    y = data_sale["purchased_rate"],
                    mode = 'markers',
                    name = sale,
                    marker_size = 12,
                    hovertemplate = sale + ': %{y:,.1f} %<extra></extra>'
                    ))
                
        self.fig_max_pool_size.update_layout(
            title = 'Total Token for Sale',
            barmode = 'stack',
            height = 600,
            hovermode = "x unified",
            plot_bgcolor = '#171730',
            paper_bgcolor = '#171730',
            font = dict(color = 'white'),
            showlegend = False
        )

        self.fig_purchased_rate.update_layout(
            title = 'Launchpad purchased rate',
            height = 600,
            hovermode = "x unified",
            plot_bgcolor = '#171730',
            paper_bgcolor = '#171730',
            font = dict(color = 'white'),
            showlegend = False
        )

        self.fig_max_pool_size.update_xaxes(
            categoryorder = 'array', 
            categoryarray = self.data['launchpad'].unique()
        )

        self.fig_purchased_rate.update_xaxes(
            categoryorder = 'array', 
            categoryarray = self.data['launchpad'].unique()
        )

        return self.fig_purchased_rate, self.fig_max_pool_size
    
    def rate_per_pool(self):
        total_data = pd.DataFrame(self.data.groupby(['launchpad']).sum())
        total_data['launchpad'] = total_data.index.get_level_values(0)
        total_data = total_data.reset_index(drop=True)

        total_data['rate'] = 100*total_data['USD_amount']/total_data['max_size']

        total_data = total_data.sort_values(by = ['rate'], ascending = True)

        return kpi(total_data['launchpad'], total_data['rate'], '', '')