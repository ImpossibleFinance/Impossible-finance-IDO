from dash import html, dcc, Input, Output, State, ClientsideFunction

from scripts.information_by_pools import *
from scripts.best_impossible_users import *
from scripts.pools_usage import *
from scripts.prices import *

from scripts.Functions import *
from scripts.local_functions import *

config = {
    'displayModeBar': False
}

full_data = load_full_csv_data_ido()
#prices_data = load_csv('data/Prices.csv')

total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs = main_kpis(full_data)


USD_by_launchpad, Num_participants = purchased_stats_by_launchpad(full_data)

fig_USD_by_sale, fig_participants_by_sale = purchased_stats_by_launchpad_and_sale(full_data)

fig_USD_by_user_type, fig_participants_by_user_type = purchased_stats_by_user_type(full_data)

table_with_all_users, users_distribution = top_users(full_data)

max_pool_size, purchased_rate, total_purchased_rate = tokens_for_sale(full_data)

#prices_first_period(prices_data)