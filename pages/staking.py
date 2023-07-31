
from config import *

dash.register_page(__name__)


class Staking_render():

    def __init__(self, data, launchpad):

        f = open('config/IDO_staking_period.json')
        self.IDO_staking_period = json.load(f)
        f.close()

        self.launchpad = launchpad

        for item in self.IDO_staking_period:
            if item['launchpad'] == launchpad:
                self.start_staking_period = pd.to_datetime(item['start_staking_period'])
                self.end_staking_period = pd.to_datetime(item['end_staking_period'])
                self.purchase_date = pd.to_datetime(item['purchase_date'])
                self.status = item['status']
        
        self.staking_data = data.copy()
        self.staking_data['date'] = pd.to_datetime(self.staking_data['date'])
        self.staking_data = self.staking_data.sort_values(by = ['date'], ascending = True)
        self.staking_data = self.staking_data[self.staking_data['date'] < self.purchase_date + timedelta(days = 30)]
        self.staking_data = self.staking_data.reset_index(drop = True)

        self.staked_staking_peak = self.staking_data['net_amt'].cumsum().max()
        self.total_stakers = self.staking_data['user'].nunique()

        self.staking_data = self.staking_data.rename(columns = {
            "date": "Date",
            "sale_type": "Sale Type",
            "user": "Staker"
        })

    def create_launchpad_name(self):

        return create_ez_kpi(self.launchpad, [], 'Selected Launchpad', '', False)

    def get_main_kpi(self):

        return create_ez_kpi(self.total_stakers, [], 'Total unique IDO stakers', '', False), create_ez_kpi(self.staked_staking_peak, [], 'Total amount staked at peak', '', False)


    def get_main_historical_line(self):

        self.staking_data['TVL'] = self.staking_data.groupby('Sale Type')['net_amt'].cumsum()

        historical_TVL_line = create_ez_line(
            self.staking_data,
            'Date',
            'TVL',
            None,
            'Sale Type',
            None,
            False,
            []
        )

        historical_TVL_line.add_annotation(
            x = self.purchase_date, 
            y = self.staking_data[self.staking_data['Date'] > self.purchase_date]['TVL'].max(),
            text = "Purchasing was started",
            showarrow = True,
            arrowhead = 1,
            ax = 50,
            ay = -30,
            bordercolor = "#c7c7c7",
            borderwidth = 2,
            borderpad = 4,
            bgcolor = "#ff7f0e"
        )
        

        return historical_TVL_line
    
    def get_top_stakers(self):

        self.staking_data['tvl_by_staker'] = self.staking_data.groupby('Staker')['net_amt'].cumsum()

        users_data = pd.DataFrame(self.staking_data.groupby('Staker')['tvl_by_staker'].max())
        users_data['Staker'] = users_data.index.get_level_values(0)
        users_data = users_data.sort_values(by = ['tvl_by_staker'], ascending = False)
        users_data = users_data.reset_index(drop = True)

        users_data = users_data.head(15)

        #print(users_data)
        #print(users_data[users_data['Staker'] == '0xC194aEDDB83DeFD5dBE7213Cb4fD64962c4ADcDC'.lower()])

        return create_ez_kpi(users_data['Staker'], users_data['tvl_by_staker'], '', '', False)



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
        html.H1([' Impossible IDO Staking (IDIA / vIDIA)'], 
                className = "main-header-title"),
        html.H2(["The Impossible Finance IDO staking dashboard is a web-based platform that provides users with detailed information and metrics related to the staking of the IDIA tokens. It is designed to offer users an intuitive and user-friendly interface to monitor their staking activities."],
                className = "description-main"),
    ]),




    html.Div([
        html.Div(
            children = total_stake_users, 
            className = "kpi_container"
        ),

        html.Div(
            children = staked_peak, 
            className = "kpi_container"
        ),

    ], className = "left_container"),


    html.Div([
        html.Div(
            children = IDIA_kpi, 
            className = "kpi_container"
        ),

        html.Div(
            children = vIDIA_kpi, 
            className = "kpi_container"
        ),

    ], className = "left_container"),


    html.Div([
        html.Ul(list_of_unique_idos, className = "list")
    ], className = "viewport"),

    html.Div(
        id = "render-staking-ido-output"
    )

])


@callback(
    Output('render-staking-ido-output', 'children'),
    [Input(item + '-click-button', 'n_clicks') for item in unique_IDO_names]
)
def display_clicked_content(*click_info):

    render = []

    if not ctx.triggered:
        _ido = None
    else:
        _ido = (ctx.triggered[0]['prop_id'].split('.')[0]).replace('-click-button', '')

    if _ido != None:
        strender = Staking_render(staking_data[staking_data['launchpad'] == _ido], _ido)

        launchpad_name = strender.create_launchpad_name()

        specific_main_kpis = strender.get_main_kpi()

        historical_line = strender.get_main_historical_line()

        top_stakers = strender.get_top_stakers()

        render = [
            html.Div([
                html.Div(
                    children = launchpad_name, 
                    className = ""
                ),
            ], className = "description-main"
            ),


            html.Div([
                html.Div(
                    children = specific_main_kpis[0], 
                    className = "kpi_container"
                ),

                html.Div(
                    children = specific_main_kpis[1], 
                    className = "kpi_container"
                ),

            ], className = "left_container"),

            html.Div([
                html.Div([
                    html.P(["Historical TVL (IDIA/vIDIA tokens)"], className = "title_small"),
                    dcc.Graph(
                        config = config, 
                        id = 'tvl-chart-historical',
                        figure = historical_line,
                        style={'width': '100%', 'display': 'inline-block'}
                    ),
                    ], className = "two_column big_colune"),
                html.Div([
                    html.P(["Top Stakers"],className = "title_small"),
                    html.Div(
                        children = top_stakers,
                        className = "kpi_container", 
                        id = 'tvl-stats-ido',
                        style = {'width': '100%', 'display': 'inline-block'}
                    ),
                    ], className = "two_column small_colune")
            ], className = "two_column_box"),
        ]

    return render