from dash import Dash, html
import flask

###############################################################
############################# App #############################
###############################################################

server = flask.Flask(__name__)
app = Dash(
    __name__, 
    server = server, 
    use_pages = True
)

@app.server.errorhandler(InternalServerError)
def handle_internal_server_error(e):
    dialog_err = f'INTERNAL SERVER ERROR - code={e.code}, name={e.name}, description={e.description}'
    return render_template("exception.html", code=e.code, name=e.name, description=e.description)


app.layout = html.Div([])

if __name__ == '__main__':
    app.run_server(debug = True)