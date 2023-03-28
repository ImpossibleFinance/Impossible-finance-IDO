from dash import Dash, html
import flask

###############################################################
############################# App #############################
###############################################################

external_scripts = [
    'https://cdn.jsdelivr.net/npm/web3@1.6.0/dist/web3.min.js'
]

server = flask.Flask(__name__)
app = Dash(
    __name__, 
    server = server, 
    use_pages = True,
    external_scripts = external_scripts
)


app.layout = html.Div([])

if __name__ == '__main__':
    app.run_server(debug = True)