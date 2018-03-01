import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
from dash.dependencies import Input, Output

import urllib
import pandas as pd

import flask
import os

layout = {'margin-top': '5', 'padding-right': '5', 'padding-left': '0'}
layout_btn = {'margin-bottom': '35', 'margin-top': '5'}
layout_table = {'font-size': '12'}
layout_bar = {'height': '25px', 'margin-top': '0'}


def get_dcc_drop(header, id):
    df = df_csv.copy()
    items = sorted(df[header].unique())
    opt = [{'label': str(i), 'value': str(i)} for i in items]
    return dcc.Dropdown(
        id=id, options=opt,
        multi=True,
        placeholder=header)


def get_drop_retrun(header, opt):
    df = df_csv.copy()
    if not opt:
        return df
    else:
        opt = [str(i) for i in opt]
        return df[df[header].isin(opt)]


def get_new_df(exp, dis, stp, gen, eth, rac):
    exp_row = get_drop_retrun('experimental_strategy', exp)
    dis_row = get_drop_retrun('disease_type', dis)
    stp_row = get_drop_retrun('sample_type', stp)
    gen_row = get_drop_retrun('gender', gen)
    eth_row = get_drop_retrun('ethnicity', eth)
    rac_row = get_drop_retrun('race', rac)
    frameList = [exp_row, dis_row, stp_row, gen_row, eth_row, rac_row]
    idx = pd.concat(frameList, axis=1, join='inner').index
    return pd.concat(frameList).loc[idx].drop_duplicates()


def get_dcc_bar(df, header):
    df_raw = df_csv.copy()
    total = len(df_raw[header].unique())
    query = len(df[header].unique())
    fy = float(total)
    fn = float(query)
    pct = "{:.2%}".format(float(fn/fy))
    html_bar = html.Div(
        style={'width': pct,
               'height': '25px',
               'font-size': '14'},
        children='{} ({}/{})'.format(pct, query, total),
        className='progress-bar progress-bar-info'
    )
    header = html.Div(header.replace('_id', ' number:'))
    html_bar = html.Div(html_bar, className='progress', style=layout_bar)
    return html.Div([header, html_bar])

app = dash.Dash()
server = app.server
resource_dir = os.path.realpath('./static/')

df_csv = pd.read_csv('data/1519753644215-manifest.csv')

logo = html.Img(src='/static/CBTTC-logo.png')
head2 = html.H2('CBTTC Available Genomic Data')

drop_exp_str = get_dcc_drop('experimental_strategy', 'experimental_strategy')
drop_dis_typ = get_dcc_drop('disease_type', 'disease_type')
drop_smp_typ = get_dcc_drop('sample_type', 'sample_type')
drop_gender = get_dcc_drop('gender', 'gender')
drop_ethnici = get_dcc_drop('ethnicity', 'ethnicity')
drop_race = get_dcc_drop('race', 'race')

bar1 = get_dcc_bar(df_csv, 'case_id')
bar2 = get_dcc_bar(df_csv, 'sample_id')

table = dt.DataTable(rows=[], columns=df_csv.columns,
                     editable=False, id='table')

app.title = 'cbttc-ngs-data'

dropdowns = html.Div(
    [
        html.Div(drop_dis_typ, className='col-sm-12', style=layout),
        html.Div(drop_exp_str, className='col-sm-6', style=layout),
        html.Div(drop_smp_typ, className='col-sm-6', style=layout),
        html.Div(drop_gender,  className='col-sm-4', style=layout),
        html.Div(drop_ethnici, className='col-sm-4', style=layout),
        html.Div(drop_race,    className='col-sm-4', style=layout)
    ], className='col-sm-6'
)

progress_bars = html.Div([bar1, bar2], className='col-sm-6', id='bar')


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
        html.Div([dropdowns, progress_bars], className='row'),
        html.Div(table, className='row', style=layout_table),
        html.Div(
            html.A(
                html.Button('download csv'),
                id='export-url',
                download='cbttc-ngs-data.csv'
            ),
            className='row pull-right', style=layout_btn
        )],
    className='eight columns offset-by-two'
)


@app.server.route('/static/<resource>')
def serve_static(resource):
    return flask.send_from_directory(resource_dir, resource)


@app.callback(
    Output('bar', 'children'),
    [Input('experimental_strategy', 'value'), Input('disease_type', 'value'),
     Input('sample_type', 'value'), Input('gender', 'value'),
     Input('ethnicity', 'value'), Input('race', 'value')])
def update_fig(exp, dis, stp, gen, eth, rac):
    new_df = get_new_df(exp, dis, stp, gen, eth, rac)
    return [get_dcc_bar(new_df, 'case_id'),
            get_dcc_bar(new_df, 'sample_id')]


@app.callback(
    Output('table', 'rows'),
    [Input('experimental_strategy', 'value'), Input('disease_type', 'value'),
     Input('sample_type', 'value'), Input('gender', 'value'),
     Input('ethnicity', 'value'), Input('race', 'value')])
def update_sample_table(exp, dis, stp, gen, eth, rac):
    new_df = get_new_df(exp, dis, stp, gen, eth, rac)
    return new_df.to_dict('records')


@app.callback(
    Output('export-url', 'href'),
    [Input('experimental_strategy', 'value'), Input('disease_type', 'value'),
     Input('sample_type', 'value'), Input('gender', 'value'),
     Input('ethnicity', 'value'), Input('race', 'value')])
def update_download_link(exp, dis, stp, gen, eth, rac):
    new_df = get_new_df(exp, dis, stp, gen, eth, rac)
    csv = new_df.to_csv(index=False, encoding='utf-8')
    return "data:text/csv;charset=utf-8," + urllib.quote(csv)


app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
})

app.css.append_css({
    'external_url': '/static/tracker.css'
})


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
