import pandas as pd
import json
import plotly.graph_objects as go

def top_users(full_data):

    f = open('config/IDO_pools.json')
    sales_config = json.load(f)

    ##### total purchased usd ######
    temp_df = pd.DataFrame(full_data.groupby('from')['USD_amount'].sum())
    temp_df['user'] = temp_df.index.get_level_values(0)
    temp_df = temp_df.reset_index(drop = True)

    temp_df2 = pd.DataFrame(full_data.groupby('from')['launchpad'].nunique())
    temp_df2['user'] = temp_df2.index.get_level_values(0)
    temp_df2 = temp_df2.reset_index(drop = True)

    result_data = pd.merge(temp_df, temp_df2, on = ['user'])
    result_data = result_data.sort_values(by = ['launchpad', 'USD_amount'], ascending = False)
    result_data['USD_amount'] = result_data['USD_amount'].map('${:,.2f}'.format)

    #result_data.to_csv('top_if_users.csv', index = False)

    ido_distribution = pd.DataFrame(result_data.groupby('launchpad')['user'].nunique())
    ido_distribution['launchpad'] = ido_distribution.index.get_level_values(0)
    ido_distribution = ido_distribution.reset_index(drop = True)

    fig_table = go.Figure(data=[go.Table(
        columnwidth = [80,50, 40],
        header=dict(
            values = ['<b>User</b>','<b>IDO participated</b>','<b>USD spent</b>'],
            line_color = 'darkslategray',
            fill_color = 'grey',
            align = ['left','center'],
            font = dict(color = 'white', size = 20),
        ),
        cells = dict(
            values = [
            result_data['user'],
            result_data['launchpad'],
            result_data['USD_amount']],
            line_color='darkslategray',
            align = ['left', 'center'],
            font = dict(color = 'darkslategray', size = 12)
        )
    )
    ])

    fig_distribution = go.Figure(go.Bar(
            x = ido_distribution['user'],
            y = ido_distribution['launchpad'],
            orientation = 'h',
            hovertemplate = '%{y:,.0f}<extra></extra>' + 'Number of Users: ' + '%{x:,.0f}<extra></extra>',
            marker = dict(
                color = ido_distribution['user'],
                colorscale = 'oryel')
            ))

    fig_table.update_layout(
        height = 1000,
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )

    fig_distribution.update_layout(
        height = 500,
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False,
        xaxis_title = "Number of users", 
        yaxis_title = "Number of IDOs"
    )
    fig_distribution.update_xaxes(type = "log")

    return fig_table, fig_distribution