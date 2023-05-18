from config import *

dash.register_page(__name__)


class TopUsers():

    def __init__(self, wallet, data, full_data):
        self.main_kpis = main_kpis(data)

        self.pieces_stats = Main_Purchased_Info(data)

        self.data_by_launchpad = self.pieces_stats.by_launchpad()

        self.data_by_sale = self.pieces_stats.by_sale_type()

        ##################################################
        #################### TOP LIST ####################
        ##################################################

        temp_df = pd.DataFrame(full_data.groupby('from')['USD_amount'].sum())
        temp_df['user'] = temp_df.index.get_level_values(0)
        temp_df = temp_df.reset_index(drop = True)

        temp_df2 = pd.DataFrame(full_data.groupby('from')['launchpad'].nunique())
        temp_df2['user'] = temp_df2.index.get_level_values(0)
        temp_df2 = temp_df2.reset_index(drop = True)

        self.result_data = pd.merge(temp_df, temp_df2, on = ['user'])
        self.result_data = self.result_data.sort_values(by = ['launchpad', 'USD_amount'], ascending = False)
        self.result_data['USD_amount'] = self.result_data['USD_amount'].map('${:,.2f}'.format)
        self.result_data = self.result_data.reset_index(drop = True)

        self.top_rank = '#' + str(self.result_data[self.result_data['user'] == wallet].index[0] + 1)

    def rerender(self):

        _total_unique_users = 'out of ' + str(total_unique_users)

        children = html.Div([

            html.Div([
                html.Iframe(
                    src = "assets/arken_idia_swap.html"
                )
            ], id = 'buy-more-idia', className = "arken_idia_swap"),

            html.Div(
                html.Div([
                    html.H1(children = 'Your Impossible Rank:'),
                    html.P(children = self.top_rank),

                    html.H6(children = _total_unique_users),
                ], className = "user_rank_card"),
            ),

            html.H1('Analysis of participant:', className = "main-header-title"),

            html.Div(
                children = kpi_single(self.main_kpis[1], 'Total USD spent', ''), 
                className = "kpi_container"
            ),

            html.Div(
                children = kpi_single(self.main_kpis[2], 'IDO participated', ''), 
                className = "kpi_container"
            ),

            html.Div(
                children = kpi_single(self.main_kpis[3], 'Total purchase transactions', ''), 
                className = "kpi_container"
            ),

            dcc.Graph(
                id = 'user-usd-by-launchpad',
                figure = self.data_by_launchpad[0],
                config = config,
            ),

            dcc.Graph(
                id = 'usd-by-launchpad-by-sale',
                figure = self.data_by_sale[0],
                config = config,
            )
        ]),

        return children


layout = html.Div(children = [

    html.Div([
        dcc.Link(
            "Home", href = '/'
        )
    ], className = "home_button"),

    html.H6(children = "Enter your wallet to continue:", className = "main-header-title"),

    html.Div([
        dcc.Input(id = 'wallet-address', value = '0x...', type = 'text'),
        html.Button('Submit', id = 'submit-wallet', n_clicks = 0),
    ]),
    
    html.Div(id = 'output-render', className = "description-main"),
])


@callback(
    Output('output-render', 'children'),
    Input('submit-wallet', 'n_clicks'),
    State('wallet-address', 'value')
)
def update_rerender(n_clicks, input_wallet):

    if len(input_wallet) == 42:

        wallet = input_wallet.lower()

        wallet_data = full_data[full_data['from'] == wallet]

        topClass = TopUsers(wallet, wallet_data, full_data)
        return topClass.rerender()
    
    else:
        return 'Enter address: 0x...'