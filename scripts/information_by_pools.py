import pandas as pd
import json
import plotly.graph_objects as go


def purchased_stats_by_launchpad(full_data):

    ##### USD ######
    df = pd.DataFrame(full_data.groupby('launchpad')['USD_amount'].sum())
    df['launchpad'] = df.index.get_level_values(0)
    df = df.reset_index(drop=True)

    USD_fig = go.Figure(data=[
        go.Pie(
            labels = df['launchpad'], 
            values = df['USD_amount'],
            text = df['USD_amount'],
            #hoverinfo = 'label+value+percent',
            textinfo = 'label',
            textfont = dict(size = 13),
            hole = 0.7,
            hovertemplate = '%{text:,.2f}$<extra></extra>',
            rotation = 90)
        ])

    USD_fig.update_layout(
        height = 700,
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        hovermode = 'closest',
        legend = {
            'orientation': 'h',
            'xanchor': 'center',
            'yanchor': 'top',
            'x': 0.5,
            'y': 1.25
        }
    )

    ##### Participants ######
    df2 = pd.DataFrame(full_data.groupby('launchpad')['from'].nunique())
    df2['launchpad'] = df2.index.get_level_values(0)
    df2 = df2.reset_index(drop=True)

    Participants_fig = go.Figure(data=[
        go.Pie(
            labels = df2['launchpad'], 
            values = df2['from'],
            text = df2['from'],
            textinfo = 'label+value',
            textfont = dict(size = 13),
            hovertemplate = '%{text:,.0f}<extra></extra>',
            hole = 0.7,
            rotation = 90)
        ])

    Participants_fig.update_layout(
        height = 700,
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        hovermode = 'closest',
        legend = {
            'orientation': 'h',
            'xanchor': 'center',
            'yanchor': 'top',
            'x': 0.5,
            'y': 1.25
        }
    )

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
    unique_sale_type = result_data['sale_type'].unique()


    fig_USD_by_sale = go.Figure()
    fig_participants_by_sale = go.Figure()

    for sale in unique_sale_type:
        data_sale = result_data[result_data["sale_type"] == sale]

        if sale == 'Standard Sale' or sale == 'Unlimited Sale':
        
            fig_USD_by_sale.add_trace(go.Bar(
                x = data_sale["launchpad"], 
                y = data_sale["USD_amount"],
                name = sale,
                marker_color = 'blue 'if sale == 'Standard Sale' else 'red',
                hovertemplate = sale + ': $%{y:,.1f}<extra></extra>'
                ))

            fig_participants_by_sale.add_trace(go.Bar(
                x = data_sale["launchpad"], 
                y = data_sale["from"],
                name = sale,
                marker_color = 'blue 'if sale == 'Standard Sale' else 'red',
                hovertemplate = sale + ': %{y:,.0f}<extra></extra>'
                ))
        else:

            fig_USD_by_sale.add_trace(go.Bar(
                x = data_sale["launchpad"], 
                y = data_sale["USD_amount"],
                name = sale,
                hovertemplate = sale + ': $%{y:,.1f}<extra></extra>'
                ))

            fig_participants_by_sale.add_trace(go.Bar(
                x = data_sale["launchpad"], 
                y = data_sale["from"],
                name = sale,
                hovertemplate = sale + ': %{y:,.0f}<extra></extra>'
                ))
    
    fig_USD_by_sale.update_layout(
        title = 'Tokens purchased (USD)',
        barmode = 'stack',
        height = 600,
        hovermode = "x unified",
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )
    fig_participants_by_sale.update_layout(
        title = 'IDO participants',
        barmode = 'stack',
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
    