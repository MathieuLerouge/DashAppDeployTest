# Libraries
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import os


# Extract data frame
main_directory = os.getcwd()
# main_directory.removesuffix("/src")
if "src" in main_directory:
    main_directory = main_directory[:-4]
df = pd.read_csv(f"{main_directory}/data/COVID_data.csv")
df_by_country = df.groupby('countriesAndTerritories', as_index=False)[['deaths', 'cases']].sum()


# Create dash application
app = dash.Dash(__name__, assets_folder="../assets")


# Define application layout
app.layout = html.Div([
    html.Div([
        dash_table.DataTable(
            id='datatable_id',
            data=df_by_country.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in df_by_country.columns
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=False,
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=6,
            style_cell_conditional=[
                {'if': {'column_id': 'countriesAndTerritories'},
                 'width': '40%', 'textAlign': 'left'},
                {'if': {'column_id': 'deaths'},
                 'width': '30%', 'textAlign': 'left'},
                {'if': {'column_id': 'cases'},
                 'width': '30%', 'textAlign': 'left'},
            ],
        ),
    ], className='row'),
    html.Div([
        html.Div([
            dcc.Dropdown(id='linedropdown',
                         options=[
                             {'label': 'Deaths', 'value': 'deaths'},
                             {'label': 'Cases', 'value': 'cases'}
                         ],
                         value='deaths',
                         multi=False,
                         clearable=False
                         ),
        ], className='six columns'),
        html.Div([
            dcc.Dropdown(id='piedropdown',
                         options=[
                             {'label': 'Deaths', 'value': 'deaths'},
                             {'label': 'Cases', 'value': 'cases'}
                         ],
                         value='cases',
                         multi=False,
                         clearable=False
                         ),
        ], className='six columns'),
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='linechart')], className='six columns'),
        html.Div([dcc.Graph(id='piechart')], className='six columns'),
    ], className='row'),

])


# Create application callbacks
@app.callback(
    [Output('piechart', 'figure'),
     Output('linechart', 'figure')],
    [Input('datatable_id', 'selected_rows'),
     Input('piedropdown', 'value'),
     Input('linedropdown', 'value')]
)
def update_data(chosen_rows, piedropval, linedropval):
    if len(chosen_rows) == 0:
        df_filterd = df_by_country[df_by_country['countriesAndTerritories'].isin(['China', 'Iran', 'Spain', 'Italy'])]
    else:
        df_filterd = df_by_country[df_by_country.index.isin(chosen_rows)]
    pie_chart = px.pie(
        data_frame=df_filterd,
        names='countriesAndTerritories',
        values=piedropval,
        hole=.3,
        labels={'countriesAndTerritories': 'Countries'}
    )
    # extract list of chosen countries
    list_chosen_countries = df_filterd['countriesAndTerritories'].tolist()
    # filter original df according to chosen countries
    # because original df has all the complete dates
    df_line = df[df['countriesAndTerritories'].isin(list_chosen_countries)]
    line_chart = px.line(
        data_frame=df_line,
        x='dateRep',
        y=linedropval,
        color='countriesAndTerritories',
        labels={'countriesAndTerritories': 'Countries', 'dateRep': 'date'},
    )
    line_chart.update_layout(uirevision='foo')
    return pie_chart, line_chart


# Main
if __name__ == '__main__':
    app.run_server(debug=True)
