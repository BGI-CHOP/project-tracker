import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
from dash.dependencies import Input, Output

import urllib
import pandas as pd

import flask
import os

app = dash.Dash()
server = app.server
resource_dir = os.path.realpath('./data/')

df_project = pd.read_csv('data/project.csv')
df_sample = pd.read_csv('data/sample.csv')


def get_dcc_drop(df, header, id):
    items = sorted(df[header].unique())
    opt = [{'label': str(i), 'value': str(i)} for i in items]
    return dcc.Dropdown(
        id=id, options=opt, multi=True,
        placeholder=header)


def get_fig_dict(df, header):
    yes = df[df[header] == 1].count()[header]
    no = df[df[header] == 0].count()[header]
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


logo = html.Img(src='/static/logo.png')
head2 = html.H2('Gabriella Miller Kids First Data Tracker')

drop_year = get_dcc_drop(df_project, 'Year', 'year')
drop_pi = get_dcc_drop(df_project, 'Contact PI', 'pi')
drop_inst = get_dcc_drop(df_project, 'Institution Name', 'inst')
drop_title = get_dcc_drop(df_project, 'Title', 'title')

fig1 = get_dcc_graph('ship', get_fig_dict(df_sample, 'Sample Shipped'))
fig2 = get_dcc_graph('seq', get_fig_dict(df_sample, 'NGS Generation'))
fig3 = get_dcc_graph('drc', get_fig_dict(df_sample, 'NGS Data Ready'))
fig4 = get_dcc_graph('cvtc', get_fig_dict(df_sample, 'Cavatica Ready'))
fig5 = get_dcc_graph('ghorm', get_fig_dict(df_sample, 'Genome Hormonization'))
fig6 = get_dcc_graph('phorm', get_fig_dict(df_sample, 'Clinical Hormonization'))

table = dt.DataTable(
            rows=df_sample.to_dict('records'),
            columns=df_sample.columns,
            editable=False,
            id='sample_table')

layout = {'margin-top': '5'}
layout_fig = {'height': '220px'}
layout_btn = {'margin-bottom': '35', 'margin-top': '5'}
layout_table = {'font-size': '12'}


app.layout = html.Div(
    [
        html.P(' '),
        html.Div(
            [
                html.Div([head2], className='col-sm-9'),
                html.Div([logo], className='col-sm-3')
            ],
            className='row'
        ),
        html.Hr(),
        html.Div(
            [
                html.Div([drop_year], className='col-sm-2', style=layout),
                html.Div([drop_pi], className='col-sm-4', style=layout),
                html.Div([drop_inst], className='col-sm-6', style=layout),
                html.Div([drop_title], className='col-sm-12', style=layout)
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div([fig1], className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div([fig2], className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div([fig3], className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div([fig4], className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div([fig5], className='col-lg-2 col-sm-4', style=layout_fig),
                html.Div([fig6], className='col-lg-2 col-sm-4', style=layout_fig)
            ],
        ),
        html.Div([table], className='row', style=layout_table),
        html.Div(
            [
                html.A(html.Button('download csv'), 
                    id='export-url', download='kf-sample-stats.csv')
            ],
            className='row pull-right', style=layout_btn
        )],
    className='eight columns offset-by-two'
)


@app.server.route('/static/<resource>')
def serve_static(resource):
    return flask.send_from_directory(resource_dir, resource)


@app.callback(
    Output('ship', 'figure'), [Input('pi', 'value')])
def update_fig_ship(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        return get_fig_dict(new_df, 'Sample Shipped')
    except:
        pass


@app.callback(
    Output('seq', 'figure'), [Input('pi', 'value')])
def update_fig_seq(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        return get_fig_dict(new_df, 'NGS Generation')
    except:
        pass


@app.callback(
    Output('drc', 'figure'), [Input('pi', 'value')])
def update_fig_drc(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        return get_fig_dict(new_df, 'NGS Data Ready')
    except:
        pass


@app.callback(
    Output('cvtc', 'figure'), [Input('pi', 'value')])
def update_fig_cvtc(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        return get_fig_dict(new_df, 'Cavatica Ready')
    except:
        pass


@app.callback(
    Output('ghorm', 'figure'), [Input('pi', 'value')])
def update_fig_ghorm(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        return get_fig_dict(new_df, 'Genome Hormonization')
    except:
        pass


@app.callback(
    Output('phorm', 'figure'), [Input('pi', 'value')])
def update_fig_phorm(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        return get_fig_dict(new_df, 'Clinical Hormonization')
    except:
        pass


@app.callback(
    Output('sample_table', 'rows'), [Input('pi', 'value')])
def update_sample_table(selected_pi):
    try:
        new_df = df_sample[df_sample['Contact PI'].isin(selected_pi)]
        return new_df.to_dict('records')
    except:
        pass


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
    app.run_server(debug=True, port=1105)
