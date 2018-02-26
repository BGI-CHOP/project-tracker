import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
from dash.dependencies import Input, Output, Event, State

import urllib
import pandas as pd

import flask
import os

app = dash.Dash()
server = app.server
resource_dir = os.path.realpath('./data/')

df_project = pd.read_csv('data/project.csv')
df_sample = pd.read_csv('data/sample-details.csv')


def get_dcc_drop(header, id):
    df = df_sample.copy()
    items = sorted(df[header].unique())
    opt = [{'label': str(i), 'value': str(i)} for i in items]
    return dcc.Dropdown(
        id=id, options=opt,
        multi=True,
        placeholder=header)


def get_fig_dict(df, header):
    df = df_sample.copy()
    yes = len(df[df[header] == 1].count())
    no = len(df[df[header] == 0].count())
    fy = float(yes)
    fn = float(no)
    pct = "{:.2%}<br />".format(float(fy/(fy+fn)))
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


logo = html.Img(src='/static/logo.png')
head2 = html.H2('Gabriella Miller Kids First Data Tracker')

drop_year = get_dcc_drop('Year', 'year')
drop_pi = get_dcc_drop('Contact PI', 'pi')
drop_inst = get_dcc_drop('Institution Name', 'inst')
drop_title = get_dcc_drop('Title', 'title')

fig1 = get_dcc_graph('ship', get_fig_dict(df_sample, 'Sample Shipped'))
fig2 = get_dcc_graph('seq', get_fig_dict(df_sample, 'NGS Generation'))
fig3 = get_dcc_graph('drc', get_fig_dict(df_sample, 'NGS Data Ready'))
fig4 = get_dcc_graph('cvtc', get_fig_dict(df_sample, 'Cavatica Ready'))
fig5 = get_dcc_graph('ghorm', get_fig_dict(df_sample, 'Genome Hormonization'))
fig6 = get_dcc_graph('phorm', get_fig_dict(df_sample, 'Clinical Hormonization'))

table = dt.DataTable(
            rows=[],
            columns=df_sample.columns,
            editable=False,
            id='sample_table')

layout = {'margin-top': '5'}
layout_fig = {'height': '220px'}
layout_btn = {'margin-bottom': '35', 'margin-top': '5'}
layout_table = {'font-size': '12'}

app.title = 'local-kf-tracker'


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
                html.Button('download csv'), id='export-url', download='kf-sample-stats.csv'
            ),
            className='row pull-right', style=layout_btn
        )],
    className='eight columns offset-by-two'
)


@app.server.route('/static/<resource>')
def serve_static(resource):
    return flask.send_from_directory(resource_dir, resource)


@app.callback(
    Output('sample_table', 'rows'),
    [Input('year', 'value'), Input('pi', 'value'),
     Input('inst', 'value'), Input('title', 'value')])
def update_sample_table(year, pi, inst, title):
    year_row = get_drop_retrun('Year', year)
    pi_row = get_drop_retrun('Contact PI', pi)
    inst_row = get_drop_retrun('Institution Name', inst)
    title_row = get_drop_retrun('Title', title)
    frameList = [year_row, pi_row, inst_row, title_row]
    return pd.concat(frameList, axis=1, join='inner').to_dict('records')


@app.callback(
    Output('export-url', 'href'), [Input('pi', 'value')])
def update_download_link(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        csv = new_df.to_csv(index=False, encoding='utf-8')
        return "data:text/csv;charset=utf-8," + urllib.quote(csv)
    except:
        pass


app.css.append_css({
    'external_url': '/static/bootstrap.min.css'
})

app.css.append_css({
    'external_url': '/static/tracker.css'
})


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
