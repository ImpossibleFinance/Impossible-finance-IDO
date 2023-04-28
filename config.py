from dash import html, dcc, Input, Output, State, ClientsideFunction
import dash
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler


from scripts.best_impossible_users import *
from scripts.prices import *

from scripts.Functions import *
from scripts.local_functions import *

config = {
    'displayModeBar': False
}

full_data = load_full_csv_data_ido()
#prices_data = load_csv('data/Prices.csv')

######################################################
#################### MAIN KPI ########################
######################################################

total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs = main_kpis(full_data)

######################################################
#################### FIRST PART ######################
######################################################

first_part = Main_Purchased_Info(full_data)

USD_by_launchpad, Num_participants = first_part.by_launchpad()

fig_USD_by_sale, fig_participants_by_sale = first_part.by_sale_type()

fig_USD_by_user_type, fig_participants_by_user_type = first_part.user_type()

######################################################
#################### SECOND PART #####################
######################################################

p_rate = Purchase_Rate(full_data)

total_purchased_rate, max_pool_size = p_rate.total_rate()

purchased_rate = p_rate.rate_per_pool()

######################################################
#################### USER PART #######################
######################################################

table_with_all_users, users_distribution = top_users(full_data)

#prices_first_period(prices_data)