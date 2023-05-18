from config import *

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
        html.Img(src = "assets/DataLab.svg", alt = " ", className = "if-ico"),
    ],className = "header-title"),
    
    html.Div([
        html.Iframe(
            src = "assets/other_dashboards_list.html",
            className = "list-dash"
        )
    ], id = 'dashboard-list'),

    html.Div([
        html.H1([' Impossible IDO Launchpad'], 
                className = "main-header-title"),
        html.H2(["The comparison of ..."],
                className = "description-main"),
    ]),

    html.Div([
        html.Div(
            children = kpi_single(total_unique_users, 'Total unique IDO participants', ''), 
            className = "kpi_container"
        ),

        html.Div(
            children = kpi_single(total_usd_purchased, 'Total tokens bought', ''), 
            className = "kpi_container"
        ),

        html.Div(
            children = kpi_single(unique_IDOS, 'Unique IDOs', ''), 
            className = "kpi_container"
        ),

        html.Div(
            children = kpi_single(total_unique_purchase_txs, 'Total purchase transactions', ''), 
            className = "kpi_container"
        ),
    ], className = "card_container"),


    html.Div([
        html.H1('Analysis of USD tokens purchased'),

        html.H2('Total raised'),

        dcc.Graph(
            id = 'usd-by-launchpad',
            figure = USD_by_launchpad,
            config = config
        ),

        html.H2('USD raised by Sale type'),

        dcc.Graph(
            id = 'usd-by-launchpad-by-sale',
            figure = fig_USD_by_sale,
            config = config
        ),

        html.H2('USD raised by User type'),

        dcc.Graph(
            id = 'usd-by-launchpad-by-user-type',
            figure = fig_USD_by_user_type,
            config = config
        )
    ],className = "usd_and_users_cards"
    ),
    html.Div([
        html.H1('Analysis of participants count'),

        html.H2('Total participants'),

        dcc.Graph(
            id = 'number-of-participants',
            figure = Num_participants,
            config = config
        ),

        html.H2('Participants by Sale type'),


        dcc.Graph(
            id = 'number-of-participants-by-sale',
            figure = fig_participants_by_sale,
            config = config
        ),

        html.H2('Participants by User type'),

        dcc.Graph(
            id = 'num-users-by-launchpad-by-user-type',
            figure = fig_participants_by_user_type,
            config = config
        )
    ],className = "usd_and_users_cards"
    ),


    html.H1('Total purchase rate', className = 'left_container_h1'),

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

######################## WIP ############################

    html.Div(
        [
            html.Div([
                dcc.Link(
                    "User Database", href = '/user-table'
                )
            ], className = "user_table"),
        ], className = "flex_user_table"
    ),

    html.Div(
        [
            html.Div([
                dcc.Link(
                    "IDO FOMO", href = '/ido-fomo'
                )
            ], className = "user_table"),
        ], className = "flex_user_table"
    ),
])