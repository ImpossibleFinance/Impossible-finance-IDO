from config import *

dash.register_page(__name__)

class PricesFOMO():

    def __init__(self, ido_name, amount):

        path = 'data/Prices.csv'

        self.amount = amount

        self.prices_data = read_data_from_csv(path)

        self.prices_data = self.prices_data[self.prices_data['token'] == ido_name]

        f = open('config/IDO_token_contracts.json')
        IDO_token_contracts = json.load(f)
        f.close()

        for item in IDO_token_contracts:
            if ido_name == item['launchpad']:
                self.start_price = float(item['ido_price'])

        self.prices_data['Token amount'] = float(self.amount)/self.start_price

        self.prices_data['USD Amount'] = self.prices_data['Token amount']*self.prices_data['Price']

        self.prices_data = self.prices_data.rename(columns = {
            "days_from_ido": "Days after IDO", 
            "roi": "ROI",
            "token": "Token"
        })

        self.prices_data = self.prices_data.sort_values(by = ['Days after IDO'])
        self.prices_data = self.prices_data.reset_index(drop = True)

        self.price_chart = create_ez_line(
            self.prices_data, 
            'Days after IDO', 
            'Price', 
            None,
            'Token', 
            False, 
            True,
            []
        )

        self.portfolio_chart = create_ez_line(
            self.prices_data, 
            'Days after IDO', 
            'USD Amount', 
            None,
            'Token', 
            False, 
            True,
            []
        )

        self.print_array = [
            'IDO',
            '1st day',
            'Today'
        ]

        self.price_stats = [
            self.start_price,
            self.prices_data.iloc[0]['Price'],
            self.prices_data.iloc[-1]['Price']
        ]

        self.portfolio_stats = [
            self.amount,
            self.prices_data.iloc[0]['USD Amount'],
            self.prices_data.iloc[-1]['USD Amount']
        ]


    def rerender(self):

        children = html.Div([

            html.H1('Your FOMO:', className = "main-header-title"),

            html.Div(
                children = create_ez_kpi(self.amount, [], 'USD spent to IDO', '', False), 
                className = "kpi_container",
                style = {'width': '33%', 'display': 'inline-block'}
            ),

            html.Div(
                children = create_ez_kpi(str(number_format(self.prices_data.iloc[-1]['ROI'])) + 'x', [], 'Your ROI', '', False), 
                className = "kpi_container",
                style = {'width': '33%', 'display': 'inline-block'}
            ),

            html.Div(
                children = create_ez_kpi(self.prices_data.iloc[-1]['USD Amount'], [], 'Portfolio Now', '', False), 
                className = "kpi_container",
                style = {'width': '33%', 'display': 'inline-block'}
            ),

            html.Div([
                html.Div([
                    html.P(["Token Price"],className = "title_small"),
                    dcc.Graph(
                        config = config, 
                        id = 'price-chart-usd',
                        figure = self.price_chart,
                        style={'width': '100%', 'display': 'inline-block'}
                    ),
                    ], className = "two_column big_colune"),
                html.Div([
                    html.P(["Price Stats"],className = "title_small"),
                    html.Div(
                        children = create_ez_kpi(self.print_array, self.price_stats, '', '', False),
                        className = "kpi_container", 
                        id = 'price-stats-ido',
                        style = {'width': '100%', 'display': 'inline-block'}
                    ),
                    ], className = "two_column small_colune")
            ], className = "two_column_box"),

            html.Div([
                html.Div([
                    html.P(["Token Price"],className = "title_small"),
                    dcc.Graph(
                        config = config, 
                        id = 'portfolio-chart-usd',
                        figure = self.portfolio_chart,
                        style={'width': '100%', 'display': 'inline-block'}
                    ),
                    ], className = "two_column big_colune"),
                html.Div([
                    html.P(["Portfolio Stats"],className = "title_small"),
                    html.Div(
                        children = create_ez_kpi(self.print_array, self.portfolio_stats, '', '', False),
                        className = "kpi_container", 
                        id = 'portfolio-stats-ido',
                        style = {'width': '100%', 'display': 'inline-block'}
                    ),
                    ], className = "two_column small_colune")
            ], className = "two_column_box"),
        ]),

        return children
        

layout = html.Div(children = [

    html.Div([
        html.Img(src = "assets/DataLab.svg", alt = " ", className = "if-ico"),
    ],className = "header-title"),

    html.Div([
        html.Iframe(
            src = "assets/other_dashboards_list.html",
            className = "list-dash"
        )
    ], id = 'dashboard-list'),

    html.Div([
        html.Iframe(
            src = "assets/subtabs_dashboards.html",
            className = "list-dash"
        )
    ], id = 'dashboard-list'),


    html.Div([
        html.H1([
            html.Div(id = 'output-render-ido')
        ],className = "left"),
                
        html.Div([
            html.H2('Parameters'),

            html.P('Select IDO'),

            dcc.Dropdown(
                options = unique_IDO_names,
                value = 'Sportium',
                id = 'ido-selections',
                placeholder = "Select IDO",
                className = "dropdown-table-input"
            ),

            html.Br(),
            html.P('Tokens bought (USD)'),

            dcc.Input(
                id = 'token-amount', 
                type = 'number',
                placeholder = "USD Amount"
            ),

            html.Button('Submit', id = 'submit-button', n_clicks = 0)

        ], className = "right_container"),
    ], className = "grid-container")
])


@callback(
    Output('output-render-ido', 'children'),
    Input('submit-button', 'n_clicks'),
    State('ido-selections', 'value'),
    State('token-amount', 'value')
)
def update_rerender_ido(n_clicks, input_ido, amount):

    if n_clicks == 0:
        return 'Submit info above'
    if amount == '0':
        return 'Amount should be > 0'
    pricesFM = PricesFOMO(input_ido, amount)

    return pricesFM.rerender()