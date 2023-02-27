from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import flask

from scripts.main_kpi import *
from scripts.information_by_pools import *
from scripts.user_types import *
from scripts.best_impossible_users import *
from scripts.pools_usage import *

from scripts.functions import *

config = {
    'displayModeBar': False
}


full_data = load_full_csv_data()

total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs, unique_sale_type = main_kpis(full_data)


USD_by_launchpad, Num_participants = purchased_stats_by_launchpad(full_data)

fig_USD_by_sale, fig_participants_by_sale = purchased_stats_by_launchpad_and_sale(full_data)

fig_USD_by_user_type, fig_participants_by_user_type = purchased_stats_by_user_type(full_data)

table_with_all_users, users_distribution = top_users(full_data)

max_pool_size, purchased_rate, total_purchased_rate = tokens_for_sale(full_data)

###############################################################
############################# App #############################
###############################################################

server = flask.Flask(__name__)
app = Dash(__name__, server = server, use_pages = True)


app.layout = html.Div([
	
])


if __name__ == '__main__':
    app.run_server(debug = True)