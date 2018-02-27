import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
from dash.dependencies import Input, Output

import urllib
import pandas as pd

import flask
import os


def get_dcc_drop(header, id):
    df = df_sample.copy()
    items = sorted(df[header].unique())
    opt = [{'label': str(i), 'value': str(i)} for i in items]
    return dcc.Dropdown(
        id=id, options=opt,
        multi=True,
        placeholder=header)


def get_fig_dict(df, header):
    yes = df[df[header] == 1].count()[header]
    no = df[df[header] == 0].count()[header]
    fy = float(yes)
    fn = float(no)
    pct = "{:.2%}<br />".format(float(fy/(fy+fn)))
    header = header.replace('Data ', 'Data<br />')
    data = dict(
        values=[yes, no],
        labels=['Complete', 'Waiting'],
        marker=dict(
            colors=['#009ABA', '#ED309D']
        ),
        textposition='none',
        hole=.95,
        type='pie'
    )
    layout = dict(
        showlegend=False,
        height=210,
        width=150,
        margin=dict(
            b=0, l=0, r=0, t=0, pad=0
        ),
        annotations=[dict(
            x=0.5,
            y=0.5,
            text=pct+header,
            showarrow=False
        )]
    )
    return dict(data=[data], layout=layout)


def get_dcc_graph(id, fig_dict):
    return dcc.Graph(
        id=id,
        figure=fig_dict,
        config=dict(displayModeBar=False, displaylogo=False)
    )


def get_drop_retrun(header, opt):
    df = df_sample.copy()
    if not opt:
        return df
    else:
        opt = [str(i) for i in opt]
        return df[df[header].isin(opt)]


def get_new_df(year, pi, inst, title):
    year_row = get_drop_retrun('Year', year)
    pi_row = get_drop_retrun('Contact PI', pi)
    inst_row = get_drop_retrun('Institution Name', inst)
    title_row = get_drop_retrun('Title', title)
    frameList = [year_row, pi_row, inst_row, title_row]
    idx = pd.concat(frameList, axis=1, join='inner').index
    return pd.concat(frameList).loc[idx].drop_duplicates()


app = dash.Dash()
server = app.server
resource_dir = os.path.realpath('./static/')

df_project = pd.read_csv('data/project.csv')
df_sample = pd.read_csv('data/sample-random.csv')

logo = html.Img(src='/static/logo.png')
head2 = html.H2('Gabriella Miller Kids First Data Tracker')

drop_year = get_dcc_drop('Year', 'year')
drop_pi = get_dcc_drop('Contact PI', 'pi')
drop_inst = get_dcc_drop('Institution Name', 'inst')
drop_title = get_dcc_drop('Title', 'title')

fig1 = get_dcc_graph('ship', get_fig_dict(df_sample, 'Sample Shipped'))
fig2 = get_dcc_graph('seq', get_fig_dict(df_sample, 'Sample Sequenced'))
fig3 = get_dcc_graph('drc', get_fig_dict(df_sample, 'DRC Received'))
fig4 = get_dcc_graph('cvtc', get_fig_dict(df_sample, 'Available on Cavatica'))
fig5 = get_dcc_graph('gharm', get_fig_dict(df_sample, 'Genomics Data Harmonized'))
fig6 = get_dcc_graph('pharm', get_fig_dict(df_sample, 'Phenotype Data Harmonized'))

table = dt.DataTable(
            rows=[],
            columns=df_sample.columns,
            editable=False,
            id='sample_table')

layout = {'margin-top': '5', 'padding-right': '5', 'padding-left': '0'}
layout_fig = {'height': '220px'}
layout_btn = {'margin-bottom': '35', 'margin-top': '5'}
layout_table = {'font-size': '12'}

app.title = 'dev-kf-tracker'

app.layout = html.Div(
    [
        html.P(' '),
        html.Div(
            [
                html.Div(head2, id='head', className='col-sm-9'),
                html.Div(logo, className='col-sm-3')
            ],
            className='row'
        ),
        html.Hr(),
        html.Div(
            [
                html.Div(drop_title, className='col-sm-12', style=layout),
                html.Div(drop_year, className='col-sm-2', style=layout),
                html.Div(drop_pi, className='col-sm-4', style=layout),
                html.Div(drop_inst, className='col-sm-6', style=layout)
            ], className='row'
        ),
        html.Div(
            [
                html.Div(fig1, className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div(fig2, className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div(fig3, className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div(fig4, className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div(fig5, className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div(fig6, className='col-lg-2 col-sm-4', style=layout_fig)
            ], className='row'
        ),
        html.Div(table, className='row', style=layout_table),
        html.Div(
            html.A(
                html.Button('download csv'),
                id='export-url',
                download='kf-sample-stats.csv'
            ),
            className='row pull-right', style=layout_btn
        )],
    className='eight columns offset-by-two'
)


@app.server.route('/static/<resource>')
def serve_static(resource):
    return flask.send_from_directory(resource_dir, resource)


@app.callback(
    Output('ship', 'figure'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_fig_ship(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    return get_fig_dict(new_df, "Sample Shipped")


@app.callback(
    Output('seq', 'figure'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_seq_ship(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    return get_fig_dict(new_df, "Sample Sequenced")


@app.callback(
    Output('drc', 'figure'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_drc_ship(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    return get_fig_dict(new_df, "DRC Received")


@app.callback(
    Output('cvtc', 'figure'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_cvtc_ship(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    return get_fig_dict(new_df, "Available on Cavatica")


@app.callback(
    Output('gharm', 'figure'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_gharm_ship(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    return get_fig_dict(new_df, "Genomics Data Harmonized")


@app.callback(
    Output('pharm', 'figure'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_pharm_ship(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    return get_fig_dict(new_df, "Phenotype Data Harmonized")


@app.callback(
    Output('sample_table', 'rows'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_sample_table(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    return new_df.to_dict('records')


@app.callback(
    Output('export-url', 'href'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_download_link(year, pi, inst, title):
    new_df = get_new_df(year, pi, inst, title)
    csv = new_df.to_csv(index=False, encoding='utf-8')
    return "data:text/csv;charset=utf-8," + urllib.quote(csv)


app.css.append_css({
    'external_url': '/static/bootstrap.min.css'
})

app.css.append_css({
    'external_url': '/static/tracker.css'
})


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
