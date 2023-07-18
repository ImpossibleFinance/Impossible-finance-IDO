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
        html.Iframe(
            src = "assets/subtabs_dashboards.html",
            className = "list-dash"
        )
    ], id = 'dashboard-list'),

    html.Div([
        html.H1([' Impossible IDO Launchpad'], 
                className = "main-header-title"),
        html.H2(["The dashboard provides investors with a seamless and transparent IDO process. It allows investors to view all the available IDOs and their details, including the start and end dates of the IDO, the amount being raised, the price of the token, and the allocation limits. Investors can also participate in the IDO through the dashboard by connecting their wallets to the platform."],
                className = "description-main"),
    ]),

    html.Div([
        html.Div(
            children = create_ez_kpi(total_unique_users, [], 'Total unique IDO participants', '', False), 
            className = "kpi_container"
        ),

        html.Div(
            children = create_ez_kpi(total_usd_purchased, [], 'Total tokens bought', '', False), 
            className = "kpi_container"
        )
    ], className = "left_container"),

    html.Div([
        html.Div(
            children = create_ez_kpi(unique_IDOS, [], 'Unique IDOs', '', False), 
            className = "kpi_container"
        ),

        html.Div(
            children = create_ez_kpi(total_unique_purchase_txs, [], 'Total purchase transactions', '', False), 
            className = "kpi_container"
        ),
    ], className = "left_container"),


    html.Div([
        html.P(["Analysis of USD Token purchased VS Participants count"],className = "title_small"),
        html.Div([
            dcc.Graph(
                id = 'usd-by-launchpad',
                figure = USD_and_participants_by_launchpad,
                config = config
            ),
        ], className = "note"),
    ], className = "single_column"),

    html.Div([
        html.H1(["Sale type"], className = "title_small"),
        html.Div([
            html.Div([
                html.P(["USD raised"],className = "title_small"),
                html.Div([
                    dcc.Graph(
                        id = 'usd-by-launchpad-by-sale',
                        figure = fig_USD_by_sale,
                        config = config
                    ),
                ], className = "note"),
            ], style = {'width': '50%', 'display': 'inline-block'}),

            html.Div([
                html.P(["Participants"],className = "title_small"),
                html.Div([
                    dcc.Graph(
                        id = 'number-of-participants-by-sale',
                        figure = fig_participants_by_sale,
                        config = config
                    ),
                ], className = "note"),
            ], style = {'width': '50%', 'display': 'inline-block'}),
        ], className = "note"),
    ]),


    html.Div([
        html.H1(["User type"], className = "title_small"),
        html.Div([
            html.Div([
                html.P(["USD spent"],className = "title_small"),
                html.Div([
                    dcc.Graph(
                        id = 'usd-by-launchpad-by-user-type',
                        figure = fig_USD_by_user_type,
                        config = config
                    ),
                ], className = "note"),
            ], style = {'width': '50%', 'display': 'inline-block'}),

            html.Div([
                html.P(["Users"],className = "title_small"),
                html.Div([
                    dcc.Graph(
                        id = 'num-users-by-launchpad-by-user-type',
                        figure = fig_participants_by_user_type,
                        config = config
                    ),
                ], className = "note"),
            ], style = {'width': '50%', 'display': 'inline-block'}),
        ], className = "note"),
    ]),


    html.Div([
        html.Div([
            html.P(["Purchase rate by Pool"],className = "title_small"),
            html.Div([
                dcc.Graph(
                    id = 'total-purchased-rate',
                    figure = total_purchased_rate,
                    config = config
                ),
            ], className = "note"),
        ], className = "two_column big_colune"),
        html.Div([
            html.P(["Total Purchase Rate"],className = "title_small"),
            html.Div([
                html.Div(
                    children = purchased_rate,
                    className = "kpi_container", 
                    id = 'purchased-rate',
                    style = {'width': '100%', 'display': 'inline-block'}
                ),
            ], className = "note"),
        ], className = "two_column small_colune")
    ], className = "two_column_box")
])