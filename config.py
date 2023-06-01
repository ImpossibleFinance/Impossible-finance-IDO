from dash import html, dcc, Input, Output, State, ClientsideFunction, callback
import dash

from scripts.Functions import *
from scripts.local_functions import *

config = {
    'displayModeBar': False
}

full_data = load_full_csv_data_ido()
unique_IDO_names = full_data['launchpad'].unique()


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