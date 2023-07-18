from dash import html, dcc, Input, Output, State, ClientsideFunction, callback, ctx
import dash
from datetime import timedelta


from scripts.Functions import *
from scripts.local_functions import *

config = {
    'displayModeBar': False
}

################## MAIN DATA ##################

full_data = load_full_csv_data_ido()
prices_data = load_prices_csv_data()
staking_data = load_staking_csv_data()


unique_IDO_names = staking_data['launchpad'].unique()


######################################################
#################### MAIN KPI ########################
######################################################

total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs = main_kpis(full_data)

######################################################
#################### FIRST PART ######################
######################################################

first_part = Main_Purchased_Info(full_data)

USD_and_participants_by_launchpad = first_part.by_launchpad()

fig_USD_by_sale, fig_participants_by_sale = first_part.by_sale_type()

fig_USD_by_user_type, fig_participants_by_user_type = first_part.user_type()

######################################################
#################### SECOND PART #####################
######################################################

p_rate = Purchase_Rate(full_data)

total_purchased_rate = p_rate.total_rate()

purchased_rate = p_rate.rate_per_pool()


######################################################
#################### STAKING PART ####################
######################################################


list_of_unique_idos = [
    html.Button(
        item,
        id = item + "-click-button",
        className = "item"
    ) for item in unique_IDO_names
]

stake = Staking(staking_data)

total_stake_users, staked_peak = stake.main_kpi()

IDIA_kpi, vIDIA_kpi = stake.IDIA_vIDIA_kpis()