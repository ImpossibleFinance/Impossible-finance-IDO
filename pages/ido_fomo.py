from config import *

dash.register_page(__name__)

class PricesFOMO():

    def __init__(self, ido_name, amount):

        path = 'data/Prices.csv'

        self.prices_data = read_data_from_csv(path)

        self.prices_data = self.prices_data[self.prices_data['token'] == ido_name]

        self.amount = float(amount)

        self.prices_data['USD Amount'] = self.amount*self.prices_data['Price']

        self.prices_data = self.prices_data.rename(columns = {
            "days_from_ido": "Days after IDO", 
            "roi": "ROI",
            "token": "Token"
        })

        self.price_chart = fig_line_over_time(
            self.prices_data, 
            'Days after IDO', 
            'Price', 
            'Token', 
            False, 
            True
        )

        self.portfolio_chart = fig_line_over_time(
            self.prices_data, 
            'Days after IDO', 
            'USD Amount', 
            'Token', 
            False, 
            True
        )

    def rerender(self):

        children = html.Div([

            html.H1('Your FOMO:', className = "main-header-title"),

            dcc.Graph(
                id = 'price-chart-usd',
                figure = self.price_chart,
                config = config,
            ),

            dcc.Graph(
                id = 'portfolio-chart-usd',
                figure = self.portfolio_chart,
                config = config,
            ),
        ]),

        return children
        

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
            value = 'Sportium',
            id = 'ido-selections'
        ),
    ]),

    html.Div([
        html.H6(children = "Tokens bought:"),
        dcc.Input(id = 'token-amount', value = '0', type = 'text'),
    ]),

    html.Button('Submit', id = 'submit-button', n_clicks = 0),

    html.Div(id = 'output-render-ido'),
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
        return 'Amoujt should be >0'
    pricesFM = PricesFOMO(input_ido, amount)

    return pricesFM.rerender()