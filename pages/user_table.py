import dash
from dash import html, dcc

from config import *

dash.register_page(__name__)

layout = html.Div(children=[

    html.Div([
        dcc.Link(
            "Home", href = '/'
        )
    ], className = "home_button"),

    html.Div([
        html.Div([
            "User Wallet: ",
            dcc.Input(id = 'my-input', value = 'All', type = 'text')
        ]),
    ], className = "table_line"),

    html.Div(children = dcc.Graph(
        id = 'users-table',
       figure = table_with_all_users,
        config = config
    )),
])