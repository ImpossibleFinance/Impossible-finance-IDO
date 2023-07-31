from config import *

dash.register_page(__name__)


class TopUsers():

    def __init__(self, wallet, data, full_data):
        self.main_kpis = main_kpis(data)

        self.hashes = data['hash'].tolist()
        self.launchpad = data['launchpad'].tolist()
        self.sale_type = data['sale_type'].tolist()
        self.blockchain = data['blockchain'].tolist()
        self.USD_amount = data['USD_amount'].tolist()

        self.description = []

        for j in range(len(self.USD_amount)):
            self.description.append(str(self.sale_type[j] + ' : ' + str(number_format(self.USD_amount[j])) + ' USD'))


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

            html.Div(
                html.Div([
                    html.Iframe(src = "assets/arken_idia_swap.html"),
                    html.H1(children = 'Your Impossible Rank:'),
                    html.P(children = self.top_rank),

                    html.H6(children = _total_unique_users),
                ], className = "user_rank_card"),
            ),

            html.H1('Analysis of wallet:', className = "main-header-title"),

            html.Div(
                children = create_ez_kpi(self.main_kpis[1], [], 'Total USD spent', '', False), 
                className = "kpi_container",
                style = {'width': '33%', 'display': 'inline-block'}
            ),

            html.Div(
                children = create_ez_kpi(self.main_kpis[2], [], 'IDO participated', '', False), 
                className = "kpi_container",
                style = {'width': '33%', 'display': 'inline-block'}
            ),

            html.Div(
                children = create_ez_kpi(self.main_kpis[3], [], 'Total purchase transactions', '', False), 
                className = "kpi_container",
                style = {'width': '33%', 'display': 'inline-block'}
            ),

            html.Div([
                html.P(["Explorer"],className = "title_small"),
                html.Div([
                    html.Div(
                        children = create_ez_kpi(self.launchpad, self.description, '', 'Explore purchase transactions for specific wallet', True),
                        className = "kpi_container", 
                        id = 'explorer-idos',
                        style = {'width': '100%', 'display': 'inline-block'}
                    ),
                ],),
            ], className = "single_column"),

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

    html.H6(children = "Enter your wallet to continue:", className = "main-header-title"),

    html.Div([
        dcc.Input(id = 'wallet-address', placeholder = '0x...', type = 'text'),
        html.Button('Submit', id = 'submit-wallet', n_clicks = 0),
    ], className = "web_style_input"),
    
    html.Div(id = 'output-render-user'),
])


@callback(
    Output('output-render-user', 'children'),
    Input('submit-wallet', 'n_clicks'),
    State('wallet-address', 'value')
)
def update_rerender_user(n_clicks, input_wallet):

    if input_wallet != None:
        if len(input_wallet) == 42:

            wallet = input_wallet.lower()

            wallet_data = full_data[full_data['from'] == wallet]

            topClass = TopUsers(wallet, wallet_data, full_data)
            return topClass.rerender()

        else:
            return ''
        
    else:
        return ''