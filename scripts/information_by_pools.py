import pandas as pd
import json
import numpy as np

from scripts.Functions import *

def purchased_stats_by_launchpad(full_data):

    ##### USD ######
    df = pd.DataFrame(full_data.groupby('launchpad')['USD_amount'].sum())
    df['launchpad'] = df.index.get_level_values(0)
    df = df.reset_index(drop=True)

    ##### Participants ######
    df2 = pd.DataFrame(full_data.groupby('launchpad')['from'].nunique())
    df2['launchpad'] = df2.index.get_level_values(0)
    df2 = df2.reset_index(drop=True)

    USD_fig = pie_distribution(df, 'launchpad', 'USD_amount', '{text:,.2f}$')

    Participants_fig = pie_distribution(df2, 'launchpad', 'from', '{text:,.0f}')

    return USD_fig, Participants_fig


def purchased_stats_by_launchpad_and_sale(full_data):

    f = open('config/IDO_pools.json')
    sales_config = json.load(f)

    df = pd.DataFrame(full_data.groupby(['launchpad', 'sale_type'])['USD_amount'].sum())
    df['launchpad'] = df.index.get_level_values(0)
    df['sale_type'] = df.index.get_level_values(1)
    df = df.reset_index(drop=True)

    df['order'] = [(list(filter(lambda x:x["launchpad"] == y, sales_config)))[0]['launch_order'] for y in df['launchpad']]
    df['order'] = df['order'].astype('int')

    df2 = pd.DataFrame(full_data.groupby(['launchpad', 'sale_type'])['from'].nunique())
    df2['launchpad'] = df2.index.get_level_values(0)
    df2['sale_type'] = df2.index.get_level_values(1)
    df2 = df2.reset_index(drop=True)


    result_data = pd.merge(df, df2, on=['launchpad','sale_type'])
    result_data = result_data.sort_values(by=['order'], ascending = True)

    fig_USD_by_sale = distribution_bars(
        result_data, 
        'launchpad', 
        'USD_amount', 
        'sale_type', 
        False,
        'stack'
    )
    fig_participants_by_sale = distribution_bars(
        result_data, 
        'launchpad', 
        'from', 
        'sale_type',
        False,
        'stack'
    )

    f.close()

    return fig_USD_by_sale, fig_participants_by_sale
    

def purchased_stats_by_user_type(full_data):

    f = open('config/IDO_pools.json')
    sales_config = json.load(f)

    ##### total purchased usd ######
    df = pd.DataFrame(full_data.groupby(['launchpad', 'from'])['USD_amount'].sum())
    df['launchpad'] = df.index.get_level_values(0)
    df['user'] = df.index.get_level_values(1)
    df = df.reset_index(drop = True)

    df['state'] = np.where(df['USD_amount'] < 10, '0-10 USD',
        np.where((df['USD_amount'] >= 10) & (df['USD_amount'] < 100), '10-100 USD',
        np.where((df['USD_amount'] >= 100) & (df['USD_amount'] < 1000), '100-1000 USD', 
        np.where((df['USD_amount'] >= 1000) & (df['USD_amount'] < 5000), '1000-5000 USD', '>5000 USD'))))

    ###### USD by USD amount ######

    users_usd = pd.DataFrame(df.groupby(['launchpad', 'state'])['USD_amount'].sum())
    users_usd['launchpad'] = users_usd.index.get_level_values(0)
    users_usd['state'] = users_usd.index.get_level_values(1)
    users_usd = users_usd.reset_index(drop = True)

    users_usd['order'] = [(list(filter(lambda x:x["launchpad"] == y, sales_config)))[0]['launch_order'] for y in users_usd['launchpad']]
    users_usd['order'] = users_usd['order'].astype('int')

    ###### Users by USD amount ######

    users = pd.DataFrame(df.groupby(['launchpad', 'state'])['user'].nunique())
    users['launchpad'] = users.index.get_level_values(0)
    users['state'] = users.index.get_level_values(1)
    users = users.reset_index(drop = True)

    result_data = pd.merge(users_usd, users, on=['launchpad','state'])
    result_data = result_data.sort_values(by=['order'], ascending = True)

    fig_USD_by_sale = distribution_bars(
        result_data, 
        'launchpad', 
        'USD_amount', 
        'state', 
        False,
        False
    )
    
    fig_participants_by_sale = distribution_bars(
        result_data, 
        'launchpad', 
        'user', 
        'state', 
        False,
        False
    )

    f.close()

    return fig_USD_by_sale, fig_participants_by_sale