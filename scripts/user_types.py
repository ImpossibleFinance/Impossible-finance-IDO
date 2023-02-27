import pandas as pd
import json
import plotly.graph_objects as go
import numpy as np

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

    fig_USD_by_sale = go.Figure()
    fig_participants_by_sale = go.Figure()

    unique_state = result_data['state'].unique()

    for state in unique_state:
        data_sale = result_data[result_data["state"] == state]

        
        fig_USD_by_sale.add_trace(go.Bar(
            x = data_sale["launchpad"], 
            y = data_sale["USD_amount"],
            name = state,
            hovertemplate = state + ': $%{y:,.1f}<extra></extra>'
            ))

        fig_participants_by_sale.add_trace(go.Bar(
            x = data_sale["launchpad"], 
            y = data_sale["user"],
            name = state,
            hovertemplate = state + ': %{y:,.0f}<extra></extra>'
            ))


    fig_USD_by_sale.update_layout(
        title = 'User type per category (USD amount)',
        height = 600,
        hovermode = "x unified",
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )
    fig_participants_by_sale.update_layout(
        title = 'User type per category (Number of users)',
        height = 600,
        hovermode = "x unified",
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )


    fig_USD_by_sale.update_xaxes(
        categoryorder = 'array', 
        categoryarray = result_data['launchpad'].unique()
    )

    fig_participants_by_sale.update_xaxes(
        categoryorder = 'array', 
        categoryarray = result_data['launchpad'].unique()
    )

    f.close()

    return fig_USD_by_sale, fig_participants_by_sale