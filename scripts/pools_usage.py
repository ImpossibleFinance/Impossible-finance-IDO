import pandas as pd
import json
import plotly.graph_objects as go


def add_max_size(data, config):

    launchpad = []
    sale_type = []
    size = []

    for item in config:
        launchpad.append(item['launchpad'])
        sale_type.append(item['sale_type'])
        size.append(item['size'])

    pool_size = pd.DataFrame({'launchpad':launchpad, 'sale_type':sale_type, 'size': size})
    pool_size['size'] = pool_size['size'].astype('int')

    result_data = pd.merge(data, pool_size, on = ['launchpad', 'sale_type'])

    return result_data


def total_purchase_ratio(data):
    total_data = pd.DataFrame(data.groupby(['launchpad']).sum())
    total_data['launchpad'] = total_data.index.get_level_values(0)
    total_data = total_data.reset_index(drop=True)

    total_data['rate'] = 100*total_data['USD_amount']/total_data['max_size']

    total_data = total_data.sort_values(by = ['order'], ascending = True)

    fig_total_purchased_rate = go.Figure()

    fig_total_purchased_rate.add_trace(go.Scatter(
                x = total_data["launchpad"], 
                y = total_data["rate"],
                mode = 'markers',
                marker_size = 25,
                hovertemplate = '%{y:,.1f} %<extra></extra>'
                ))

    fig_total_purchased_rate.update_layout(
        title = 'Total purchased rate',
        height = 600,
        hovermode = "x unified",
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )


    fig_total_purchased_rate.update_xaxes(
        categoryorder = 'array', 
        categoryarray = total_data['launchpad'].unique()
    )

    return fig_total_purchased_rate

def tokens_for_sale(full_data):

    f = open('config/IDO_pools.json')
    sales_config = json.load(f)

    f2 = open('config/IDO_token_contracts.json')
    tokens_config = json.load(f2)

    df = pd.DataFrame(full_data.groupby(['launchpad', 'sale_type'])['USD_amount'].sum())
    df['launchpad'] = df.index.get_level_values(0)
    df['sale_type'] = df.index.get_level_values(1)
    df = df.reset_index(drop=True)

    df['order'] = [(list(filter(lambda x:x["launchpad"] == y, sales_config)))[0]['launch_order'] for y in df['launchpad']]
    df['order'] = df['order'].astype('int')

    df['price'] = [(list(filter(lambda x:x["launchpad"] == y, tokens_config)))[0]['ido_price'] for y in df['launchpad']]
    df['price'] = df['price'].astype('float')
    
    df = add_max_size(df, sales_config)

    df['max_size'] = df['price']*df['size']
    df = df.drop(['price', 'size'], axis=1)

    df['purchased_rate'] = 100*df['USD_amount']/df['max_size']

    unique_sale_type = df['sale_type'].unique()

    df = df.sort_values(by = ['order'], ascending = True)

    fig_max_pool_size = go.Figure()
    fig_purchased_rate = go.Figure()

    for sale in unique_sale_type:
        data_sale = df[df["sale_type"] == sale]

        if sale == 'Standard Sale' or sale == 'Unlimited Sale':
        
            fig_max_pool_size.add_trace(go.Bar(
                x = data_sale["launchpad"], 
                y = data_sale["max_size"],
                name = sale,
                marker_color = 'blue 'if sale == 'Standard Sale' else 'red',
                hovertemplate = sale + ': $%{y:,.1f}<extra></extra>'
                ))
            
            fig_purchased_rate.add_trace(go.Scatter(
                x = data_sale["launchpad"], 
                y = data_sale["purchased_rate"],
                mode = 'markers',
                name = sale,
                marker_size = 12,
                marker_color = 'blue 'if sale == 'Standard Sale' else 'red',
                hovertemplate = sale + ': %{y:,.1f} %<extra></extra>'
                ))
        else:

            fig_max_pool_size.add_trace(go.Bar(
                x = data_sale["launchpad"], 
                y = data_sale["max_size"],
                name = sale,
                hovertemplate = sale + ': $%{y:,.1f}<extra></extra>'
                ))
            
            fig_purchased_rate.add_trace(go.Scatter(
                x = data_sale["launchpad"], 
                y = data_sale["purchased_rate"],
                mode = 'markers',
                name = sale,
                marker_size = 12,
                hovertemplate = sale + ': %{y:,.1f} %<extra></extra>'
                ))
    
    fig_max_pool_size.update_layout(
        title = 'Total Token for Sale',
        barmode = 'stack',
        height = 600,
        hovermode = "x unified",
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )

    fig_purchased_rate.update_layout(
        title = 'Launchpad purchased rate',
        height = 600,
        hovermode = "x unified",
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )

    fig_max_pool_size.update_xaxes(
        categoryorder = 'array', 
        categoryarray = df['launchpad'].unique()
    )

    fig_purchased_rate.update_xaxes(
        categoryorder = 'array', 
        categoryarray = df['launchpad'].unique()
    )

    f.close()
    f2.close()

    fig_total_purchased_rate = total_purchase_ratio(df)

    return fig_max_pool_size, fig_purchased_rate, fig_total_purchased_rate