import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    dbc.Button("Success", color="success", className="mr-1")
)

if __name__ == "__main__":
    app.run_server()
