import dash
from dash import html, dcc

from app import *

###########################################################################
############################# Page ########################################
###########################################################################

dash.register_page(
    __name__,
    path = '/',
    title = 'IDO Dashboard',
    name = 'IDO Dashboard'
)

layout = html.Div([
    html.Div([
        html.Div([
            html.H6(children = 'Total unique IDO participants',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{total_unique_users:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'blue',
                    'fontSize': 45,
                }
            )
        ], className = "card_container"),
        html.Div([
            html.H6(children = 'Total tokens purchased',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"${total_usd_purchased:,.1f}",
                style = {
                    'textAlign': 'center',
                    'color': 'yellow',
                    'fontSize': 45,
                }
            )
        ], className = "card_container"),
        html.Div([
            html.H6(children = 'Number of IDOs',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{unique_IDOS:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 45,
                }
            )
        ], className = "card_container"),
    ], className = "container"),

    html.Div([
        html.Div([
            html.H6(children = 'Total purchase transactions',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{total_unique_purchase_txs:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'blue',
                    'fontSize': 45,
                }
            )
        ], className = "card_container_double"),
        html.Div([
            html.H6(children = 'Unique Sale Types',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{unique_sale_type:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 45,
                }
            )
        ], className = "card_container_double"),
    ], className = "container"),


    html.Div([
        html.H1('Analysis of USD tokens purchased'),
        dcc.Graph(
            id = 'usd-by-launchpad',
            figure = USD_by_launchpad,
            config = config
        ),
        dcc.Graph(
            id = 'usd-by-launchpad-by-sale',
            figure = fig_USD_by_sale,
            config = config
        ),
        dcc.Graph(
            id = 'usd-by-launchpad-by-user-type',
            figure = fig_USD_by_user_type,
            config = config
        )
    ],className = "usd_and_users_cards"
    ),
    html.Div([
        html.H1('Analysis of participants count'),
        dcc.Graph(
            id = 'number-of-participants',
            figure = Num_participants,
            config = config
        ),
        dcc.Graph(
            id = 'number-of-participants-by-sale',
            figure = fig_participants_by_sale,
            config = config
        ),
        dcc.Graph(
            id = 'num-users-by-launchpad-by-user-type',
            figure = fig_participants_by_user_type,
            config = config
        )
    ],className = "usd_and_users_cards"
    ),

    html.Div(
        [
            html.Div([
                dcc.Link(
                    "User Database", href = '/user-table'
                )
            ], className = "user_table"),

            html.Div(children = dcc.Graph(
                id = 'users-histogram',
                figure = users_distribution,
                config = config
            ), style={'width': '50%', 'display': 'inline-block'},
            ),
        ], className = "flex_user_table"
    ),

    dcc.Graph(
        id = 'total-purchased-rate',
        figure = total_purchased_rate,
        config = config
    ),

    html.Div(children = dcc.Graph(
        id = 'max-pool-size',
        figure = max_pool_size,
        config = config
        ),
        style={'width': '50%', 'display': 'inline-block'},
    ),

    html.Div(children = dcc.Graph(
        id = 'purchased-rate',
        figure = purchased_rate,
        config = config
        ),
        style={'width': '50%', 'display': 'inline-block'},
    ),

])