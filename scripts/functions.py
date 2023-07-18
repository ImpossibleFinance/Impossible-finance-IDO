from math import log, floor
import pandas as pd
from plotly.subplots import make_subplots
import json
import os
import numpy as np
import pathlib
from random import randint

from dash import html, Dash
import plotly.graph_objs as go

from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import Query



kpi_style = {
    'display': 'flex', 
    'align-items': 'center', 
    'justify-content': 'left',
    'margin-top': '10px'
}

def number_format(number):
    if abs(float(number)) > 1:
        units = ['', 'K', 'M', 'B', 'T', 'P']
        k = 1000.0
        magnitude = int(floor(log(number, k)))
        if isinstance(number, float):
            return '%.2f%s' % (number / k**magnitude, units[magnitude])
        if isinstance(number, int):
            return '%d%s' % (number / k**magnitude, units[magnitude])
    else:
        dist = int(('%e' %number).partition('-')[2]) - 1
        format = '%.' + str(dist + 2) + 'f'
        return format %number






def read_data_from_csv(path):
    df = pd.read_csv(path)

    lower_columns = ['hash', 'from', 'to']

    if 'Date(UTC)' in df:
        df['Date(UTC)'] = pd.to_datetime(pd.to_datetime(df['Date(UTC)']).dt.strftime('%Y-%m-%d'))

    for low in lower_columns:
        if low in df:
            df[low] = df[low].str.lower()
    
    return df






def total_sum(data, value, group_by):
    data_sum = data.groupby(group_by).sum()
    data_sum[group_by] = data_sum.index.get_level_values(0)
    data_sum = data_sum.sort_values(by = [value], ascending = False)
    data_sum = data_sum.reset_index(drop=True)

    return data_sum

def average(data, value, group_by):

    data_average  = data.groupby([group_by]).mean()
    data_average[group_by] = data_average.index.get_level_values(0)
    data_average = data_average.sort_values(by = [value], ascending = False)
    data_average = data_average.reset_index(drop=True)

    return data_average



#################################################################################################################
################################################# MAIN CHARTS ###################################################
#################################################################################################################


def creal_graph():
    fig = go.Figure()

    fig.update_layout(
        height = 200,
        hovermode = "x unified",
        plot_bgcolor = '#171730',
        paper_bgcolor = '#171730',
        font = dict(color = 'white'),
        showlegend = False
    )

    return fig


######################################################################
############################### KPI ##################################
######################################################################



class KPI():

    def __init__(self, column_A, column_B, title, subtitle, pics):
        
        self.column_A = column_A
        self.column_B = column_B

        self.pics = pics

        if len(self.column_B) == 0:

            self.div_output = self.single()

            self.counter = html.Div([
                html.H2(children = title),
                html.H3(children = subtitle),
                html.Div(children = self.div_output)
            ], className = "card_container"),

        else:

            self.div_output = self.double()

            self.counter = html.Div([
                html.H1(children = title),
                html.H3(children = subtitle),
                html.Div(children = self.div_output)
            ], className = "card_container"),

    def single(self):

        div_output = (
            html.Span([
                html.A(number_format(self.column_A)) if type(self.column_A) != str else html.A(self.column_A),
            ], style = kpi_style
            ),
        )

        return div_output
    
    def double(self):

        div_output = []

        for j in range(len(self.column_A)):
            if self.pics == True:
                div_output.append(
                    html.Span([
                        html.Img(src = "assets/" + (self.column_A[j]).lower() + ".png", height = 22),
                        html.Span(self.column_A[j], className = "a_list_kpi"),
                        html.Span(number_format(self.column_B[j]), className = "b_list_kpi") if type(self.column_B[j]) != str else html.Span(self.column_B[j], className = "b_list_kpi"),
                    ], style = kpi_style
                    ),
                )
                
            else:
                div_output.append(
                    html.Span([
                        html.Span(self.column_A[j], className = "a_list_kpi"),
                        html.Span(number_format(self.column_B[j]), className = "b_list_kpi") if type(self.column_B[j]) != str else html.Span(self.column_B[j], className = "b_list_kpi"),
                    ], style = kpi_style
                    ),
                )

        return div_output

    def get_figure(self):
        return self.counter

def create_ez_kpi(column_A, column_B, title, subtitle, pics):

    ez_kpi = KPI(column_A, column_B, title, subtitle, pics)

    return ez_kpi.get_figure()

######################################################################
############################### LINE #################################
######################################################################


class Line():
    def __init__(self, data, x, y1, y2, _group_by, _config, _log_scale, _colors):

        self.log_scale = _log_scale

        if y2 == None:
            self.ez_lines = go.Figure()
            if _group_by == None:
                self.make_simple_line(data, x, y1, _colors[0])
            else:
                self.make_single_line(data, x, y1, _group_by, _config)


            for i, d in enumerate(self.ez_lines.data):
                self.ez_lines.add_scatter(
                    x = [d.x[-1]], 
                    y = [d.y[-1]],
                    mode = 'markers',
                    marker = dict(color = d.marker.color, size = 10),
                    hoverinfo = 'skip',
                    showlegend = False,
                )

        else:
            self.ez_lines = make_subplots(specs = [[{"secondary_y": True}]])
            self.make_sub_line(data, x, y1, y2, _colors)


        self.ez_lines.update_layout(
            xaxis_title = x, 
            yaxis_title = y1,
            height = 500,
            hovermode = "x unified",
            plot_bgcolor = '#171730',
            paper_bgcolor = '#171730',
            font = dict(color = 'white'),
            showlegend = False
        )

        if y2 != None:
            self.ez_lines.update_layout(
                yaxis2_title = y2
            )
            
        self.ez_lines.update_xaxes(tickangle = 45)

        self.check_if_log()

    def add_figure(self, _data, _x, _y, _name, _color):

        if _color != None:
            self.ez_lines.add_trace(go.Scatter(
                x = _data[_x],
                y = _data[_y],
                name = _name,
                marker_color = _color,
                showlegend = False
            ))

        else:
            self.ez_lines.add_trace(go.Scatter(
                x = _data[_x],
                y = _data[_y],
                name = _name,
                showlegend = False
            ))

        return True
    
    def make_simple_line(self, data, x, y1, _color):

        self.add_figure(data, x, y1, y1, _color)

        return True

    def make_single_line(self, data, x, y1, _group_by, _config):
        
        self.groups = data[_group_by].unique()

        for group in self.groups:
            data_group = data[data[_group_by] == group]

            if _config == None:
                self.add_figure(data_group, x, y1, group, None)
            else:
                self.add_figure(data_group, x, y1, group, ((list(filter(lambda xx:xx["chain_name"] == group, _config)))[0]["colors"]))


        return True

    def make_sub_line(self, data, x, y1, y2, _colors):

        self.ez_lines.add_trace(
            go.Scatter(
                x = data[x],
                y = data[y1],
                showlegend = False,
                name = y1,
                legendgroup = 1,
                marker_color = _colors[0]
            ),
            secondary_y = False,
        )

        self.ez_lines.add_trace(
            go.Scatter(
                x = data[x],
                y = data[y2],
                showlegend = False,
                name = y2,
                legendgroup = 2,
                marker_color = _colors[1]
            ),
            secondary_y = True,
        )

    def check_if_log(self):

        if self.log_scale:
            self.ez_lines.update_yaxes(type = "log")

        return True
    
    def get_figure(self):
        return self.ez_lines


def create_ez_line(data, x, y1, y2, _group_by, _config, _log, _colors):

    ez_lines = Line(data, x, y1, y2, _group_by, _config, _log, _colors)

    return ez_lines.get_figure()


#######################################################################
############################### BARS ##################################
#######################################################################

class Bar():

    def __init__(self, data, x, y1, y2, _group_by, _config, _stack, _colors):

        self.stack = _stack

        if y2 == None:
            self.ez_bars = go.Figure()
            if _group_by == None:
                self.make_simple_bar(data, x, y1, _colors[0])
            else:
                self.make_single_bars(data, x, y1, _group_by, _config)

        else:
            self.ez_bars = make_subplots(specs = [[{"secondary_y": True}]])
            self.make_sub_bars(data, x, y1, y2, _colors)


        self.ez_bars.update_layout(
            xaxis_title = x, 
            yaxis_title = y1,
            height = 500,
            hovermode = "x unified",
            plot_bgcolor = '#171730',
            paper_bgcolor = '#171730',
            font = dict(color = 'white'),
            showlegend = False
        )

        if y2 != None:
            self.ez_bars.update_layout(
                yaxis2_title = y2
            )
            

        self.ez_bars.update_xaxes(tickangle = 45)

        self.check_if_stacked()
        
    def make_sub_bars(self, data, x, y1, y2, _colors):

        self.ez_bars.add_trace(
            go.Bar(
                x = data[x],
                y = data[y1],
                showlegend = False,
                name = y1,
                offsetgroup = 1,
                marker_color = _colors[0]
            ),
            secondary_y = False,
        )

        self.ez_bars.add_trace(
            go.Bar(
                x = data[x],
                y = data[y2],
                showlegend = False,
                name = y2,
                offsetgroup = 2,
                marker_color = _colors[1]
            ),
            secondary_y = True,
        )

        self.ez_bars.update_layout(
            barmode = 'group',
        )

    def make_single_bars(self, data, x, y1, _group_by, _config):
        
        self.groups = data[_group_by].unique()

        for group in self.groups:
            data_group = data[data[_group_by] == group]

            if _config == None:
                self.add_figure(data_group, x, y1, group, None)
            else:
                self.add_figure(data_group, x, y1, group, ((list(filter(lambda xx:xx["chain_name"] == group, _config)))[0]["colors"]))


        return True
    
    def make_simple_bar(self, data, x, y1, _color):

        self.add_figure(data, x, y1, y1, _color)

        return True

    def add_figure(self, _data, _x, _y, _name, _color):

        if _color != None:
            self.ez_bars.add_trace(go.Bar(
                x = _data[_x],
                y = _data[_y],
                name = _name,
                marker_color = _color
            ))

        else:
            self.ez_bars.add_trace(go.Bar(
                x = _data[_x],
                y = _data[_y],
                name = _name
            ))

        return True
    
    def check_if_stacked(self):

        if self.stack:
            self.ez_bars.update_layout(barmode = 'stack')

        return True

    def get_figure(self):
        return self.ez_bars
        

def create_ez_bar(data, x, y1, y2, _group_by, _config, _stack, _colors):

    ez_bars = Bar(data, x, y1, y2, _group_by, _config, _stack, _colors)

    return ez_bars.get_figure()



######################################################################
############################### PIE ##################################
######################################################################


class Pie():

    def __init__(self, data, x, y):
        
        self.ez_pies = go.Figure(data=[go.Pie(
            labels = data[x], 
            values = data[y],
            text = data[y],
            textinfo = 'label',
            textfont = dict(size = 13),
            hole = 0.7,
            rotation = 90
        )])

        self.ez_pies.update_layout(
            height = 600,
            plot_bgcolor = '#171730',
            paper_bgcolor = '#171730',
            font = dict(color = 'white'),
            hovermode = 'closest',
            showlegend = False
        )

    def get_figure(self):
        return self.ez_pies
    

######################################################################
############################# SCATTER ################################
######################################################################


class Scatter():

    def __init__(self, data, x, y1, y2, _group_by, _config, _colors):

        if y2 == None:
            self.ez_scatters = go.Figure()
            if _group_by == None:
                #self.make_simple_scatter(data, x, y1, _colors[0])
                pass
            else:
                self.make_single_scatter(data, x, y1, _group_by, _config)

        else:
            pass
            #self.ez_scatters = make_subplots(specs = [[{"secondary_y": True}]])
            #self.make_sub_scatters(data, x, y1, y2, _colors)


        self.ez_scatters.update_layout(
            xaxis_title = x, 
            yaxis_title = y1,
            height = 500,
            hovermode = "x unified",
            plot_bgcolor = '#171730',
            paper_bgcolor = '#171730',
            font = dict(color = 'white'),
            showlegend = False
        )

        if y2 != None:
            self.ez_scatters.update_layout(
                yaxis2_title = y2
            )
            
        self.ez_scatters.update_xaxes(tickangle = 45)

    def make_single_scatter(self, data, x, y1, _group_by, _config):
        
        self.groups = data[_group_by].unique()

        for group in self.groups:
            data_group = data[data[_group_by] == group]

            if _config == None:
                self.add_figure(data_group, x, y1, group, None)
            else:
                self.add_figure(data_group, x, y1, group, ((list(filter(lambda xx:xx["chain_name"] == group, _config)))[0]["colors"]))


        return True
    
    def add_figure(self, _data, _x, _y, _name, _color):

        if _color != None:
            self.ez_scatters.add_trace(go.Scatter(
                x = _data[_x],
                y = _data[_y],
                mode = 'markers',
                marker_size = 12,
                name = _name,
                marker_color = _color
            ))

        else:
            self.ez_scatters.add_trace(go.Scatter(
                x = _data[_x],
                y = _data[_y],
                mode = 'markers',
                marker_size = 12,
                name = _name
            ))

        return True
    
    def get_figure(self):
        return self.ez_scatters
    

def create_ez_scatters(data, x, y1, y2, _group_by, _config, _colors):

    ez_scatters = Scatter(data, x, y1, y2, _group_by, _config, _colors)

    return ez_scatters.get_figure()