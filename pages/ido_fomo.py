from config import *

dash.register_page(__name__)


layout = html.Div(children = [

    html.Div([
        dcc.Link(
            "Home", href = '/'
        )
    ], className = "home_button"),

    html.H1(children = "Parameters:", className = "main-header-title"),

    html.Div([
        html.H6(children = "Select IDO:"),
        dcc.Dropdown(
            options = unique_IDO_names,
            value = 'Arken',
            id = 'ido-selections'
        ),
    ]),

    html.Div([
        html.H6(children = "Tokens bought:"),
        dcc.Input(id = 'token-amount', value = '0', type = 'text'),
    ]),

    html.Button('Submit', id = 'submit-wallet', n_clicks = 0),
])