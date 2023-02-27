from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import flask

from scripts.main_kpi import *
from scripts.information_by_pools import *
from scripts.user_types import *
from scripts.best_impossible_users import *

config = {
    'displayModeBar': False
}

pool_addresses = []
full_data = pd.DataFrame()
currency = ['BUSD', 'IDIA']

f = open('config/IDO_pools.json')
IDO_pools = json.load(f)


for item in IDO_pools:
    pool_addresses.append(item['pool_address'].lower())

f.close()

for token in currency:
    df = pd.read_csv('transactions_data/' + str(token) +'_to_pools_transactions.csv')
    df['hash'] = df['hash'].str.lower()
    df['from'] = df['from'].str.lower()
    df['to'] = df['to'].str.lower()
    if token == 'BUSD':
        df['USD_amount'] = df['amount']
    if token == 'IDIA':
        df['USD_amount'] = df['amount']*0.025/0.0136
    full_data = pd.concat([full_data, df])
    
full_data = full_data.loc[(full_data['to']).isin(pool_addresses)]

total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs, unique_sale_type = main_kpis(full_data)


USD_by_launchpad, Num_participants = purchased_stats_by_launchpad(full_data)

fig_USD_by_sale, fig_participants_by_sale = purchased_stats_by_launchpad_and_sale(full_data)

fig_USD_by_user_type, fig_participants_by_user_type = purchased_stats_by_user_type(full_data)

table_with_all_users, users_distribution = top_users(full_data)

###############################################################
############################# App #############################
###############################################################

server = flask.Flask(__name__)
app = Dash(__name__, server = server, use_pages = True)


app.layout = html.Div([
	
])


if __name__ == '__main__':
    app.run_server(debug = True)