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

@app.server.after_request
def apply_caching(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubdomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    return response

@app.server.errorhandler(500)
def handle_internal_server_error(e):
    return flask.render_template("404.html", code=e.code, name=e.name, description="Something went wrong")


app.layout = html.Div([])

if __name__ == '__main__':
    app.run_server(debug = True)

    