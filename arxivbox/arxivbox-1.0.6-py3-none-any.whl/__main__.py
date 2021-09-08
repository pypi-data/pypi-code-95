import warnings
warnings.filterwarnings("ignore")

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State,MATCH, ALL
#import arxiv
import numpy as np
import argparse
import os
#from arxiv import SortOrder, SortCriterion
import urllib
import feedparser
import time
import re
import gzip, json
import requests, socket

if not os.path.isdir('arxivbox'):
  os.mkdir('arxivbox')

r = requests.get("http://paperswithcode.com/media/about/links-between-papers-and-code.json.gz")
with open('arxivbox/links-between-papers-and-code.json.gz', 'wb') as f:
  f.write(r.content)
  f.close()


confs = ['all', 'arXiv', 'CVPR', "ICCV", "ECCV", "WACV", "AAAI", "BMVC", "NeurIPS", "ICML", "ICLR"]
max_res = ['all', '100', '200', "300", "400", "500","1000","1500","2000","3000","4000"]
options = ['strict', 'partly', 'all']
sort = ['relevence', 'date']

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'arxivbox'


if not os.path.isfile('arxivbox/logfav'):
  with open('arxivbox/logfav', 'w+') as f:
    f.close()

def loading(children):
  return dcc.Loading(children, type='cube', fullscreen=True, style={'opacity': 0.9})


checklist = dbc.Form([dbc.FormGroup(
    [
        dbc.Label("Conference:", width =4),
        dbc.Col(dbc.Select(id="select", style={ 'font-size': '12px',}, placeholder= 'venue',options=[{"label":i, "value":idx} for idx,i in enumerate(confs)] + [{"label":'other', 'value':-1}],value =0, ), width=5,),
        dbc.Col(dbc.Input(placeholder= 'other, eg. EMNLP', id='other_conf',style={  'display':'none'},), width=9,),], row=True,),
        
        dbc.FormGroup([dbc.Label("Maximum results:", width =5),
        dbc.Col(dbc.Select(id="select_max", style={ 'font-size': '12px'},placeholder= 'max',options=[{"label":i, "value":idx} for idx,i in enumerate(max_res)],value = 1,), width=4,)], row=True,),

        dbc.FormGroup([dbc.Label("Matching method:", width =5),
        dbc.Col(dbc.Select(id="select_option", style={ 'font-size': '12px'},placeholder= 'type',options=[{"label":i, "value":idx} for idx,i in enumerate(options)],value = 1,), width=4,)], row=True,),

        dbc.FormGroup([dbc.Label("Sort by:", width =3),
        dbc.Col(dbc.Select(id="select_sort", style={ 'font-size': '12px'},placeholder= 'sort',options=[{"label":i, "value":idx} for idx,i in enumerate(sort)],value = 1, ), width=6,)], row=True,),


         dbc.FormGroup([dbc.Checkbox(id="code_option", className="form-check-input"), dbc.Label(
                    "Show code-only results",
                    html_for="code_option",
                    className="form-check-label",
                ),
            ],
            check=False, style = {'margin-left':  '20px'}
        ),

    ], style={ 'font-size': '12px',}
)


col2 = dbc.Container([html.Br(),

    dbc.InputGroup([dbc.InputGroupAddon(dbc.Checkbox(id = 'check-all'), addon_type="prepend"),
                    dbc.Input(placeholder= 'search anything', id='search_string', style={'width':'200px'}),
                    #dbc.Select(id="select",placeholder= 'venue',options=[{"label":i, "value":idx} for idx,i in enumerate(confs)],value =0, style={'width':'10px'}),
                    #dbc.Select(id="select_max",placeholder= 'max',options=[{"label":i, "value":idx} for idx,i in enumerate(max_res)],value = 1, style={'width':'10px'}),
                    #dbc.Select(id="select_option",placeholder= 'type',options=[{"label":i, "value":idx} for idx,i in enumerate(options)],value = 1),
                    #dbc.Select(id="select_sort",placeholder= 'sort',options=[{"label":i, "value":idx} for idx,i in enumerate(sort)],value = 1),
                    #dbc.InputGroupAddon("code", addon_type="prepend"),
                    #dbc.InputGroupAddon(dbc.RadioButton(id="code_option"), addon_type="prepend"),
                    dbc.InputGroupAddon(dbc.Button("search", color="light", size = 'sm', id = 'search', className="mr-1")),], size="sm",style={'width':'500px'}
                    ),


    html.Br(),
    (html.Div(id='my-output')),
    html.Div(id='dummy'),
    loading(html.Div(id='loadig')),
    dbc.Tooltip('Show marked publications', target="check-all", placement = 'left'),
    #dbc.Tooltip('Select conference name',target="select", placement = 'left'),
    #dbc.Tooltip('Select maximum results',target="select_max", placement = 'left'),
    #dbc.Tooltip('Select matching algorithm',target="select_option", placement = 'left'),
    #dbc.Tooltip('Sort by', target="select_sort", placement = 'left'),
    #dbc.Tooltip('Show results based on code availability', target="code_option", placement = 'left'),

], style =  {'align':'center', 'width':'800px'})

app.layout = dbc.Container(dbc.Row(
            [   dbc.Col(html.Div([html.Br(), html.Hr(), html.P('Advanced Options' , style={'font-size': '18px'}), html.Hr(), checklist, html.Hr(),])),
                dbc.Col(col2),
                
 
            ],
        ))

@app.callback( Output(component_id = 'other_conf', component_property ='style'),Input(component_id = 'select', component_property ='value'),)
def update(v):

  if int(v) ==  -1:
    return { 'font-size': '12px'}
  else:
    return {'display':'none'}

@app.callback(
    [Output(component_id='my-output', component_property='children'),Output(component_id='loadig', component_property='children'),],
    [Input(component_id='search', component_property='n_clicks'), Input(component_id='check-all', component_property='checked')],
    [State(component_id='select', component_property='value'),
     State(component_id='search_string', component_property='value'),
     State(component_id='select_max', component_property='value'),
     State(component_id='select_option', component_property='value'),
     State(component_id='select_sort', component_property='value'),
     State(component_id='code_option', component_property='checked'),
     State(component_id='other_conf', component_property='value'),
     ])

def update_output_div(n_click, check_all, select_id, string, select_max, select_option, select_sort, code_option,other_conf):

  #with gzip.open('links-between-papers-and-code.json.gz', 'rt', encoding='UTF-8') as zipfile:
  #  pwcdata = json.load(zipfile)

  with open('arxivbox/logfav', 'r') as f:
    favlist = [ii[:-1][:-2] for ii in f.readlines()]
    f.close()
  with open('arxivbox/logfav', 'r') as f:
    favlistv = [ii[:-1] for ii in f.readlines()]
    f.close()

  #print (check_all)

  with gzip.open('arxivbox/links-between-papers-and-code.json.gz', 'rt', encoding='UTF-8') as zipfile:
    pwcdata = json.load(zipfile)
    pwcdata = {x['paper_arxiv_id']: x['repo_url'] for x in pwcdata}
    #print ('loading')

  if True:

     # print (confs, select_id)
      if int(select_id)==-1:
        conf = other_conf.upper()
      else:
        conf = confs[int(select_id)]
      max = max_res[int(select_max)]
      if max == 'all':
        max = float('inf')
      else:
        max = int(max)
      if not n_click:
        max = 25
      if conf == 'all':
        conf_query = "("+' OR '.join(['(co:'+conf +' OR jr:'+conf+')' for conf in confs[2:]])
      elif conf == 'arXiv':
        conf_query = "("+'cat:cs.CV'
      else:
        conf_query = "("+'co:'+conf +' OR jr:'+conf

      #print (conf_query)

      if string is None or string.strip() is "":
        query = conf_query + ')'
      else:


        string = re.sub(' +', ' ', string).strip()

        query = conf_query + ") AND "  + '(('+ ' AND '.join(['all:'+i for i in string.split(' ')]) + '))' #OR (' + ' AND '.join(['abs:'+i for i in string.split(' ')]) + '))'

      #print (query)

      query = query.replace(' ', '+').replace('(','%28').replace(')','%29')
      strtime = time.time()
      if int(select_sort)==1:
        sort_method = '&sortBy=submittedDate&sortOrder=descending'
      else:
        sort_method = '&sortBy=relevance&sortOrder=descending'

      if check_all:
        #print('https://export.arxiv.org/api/query?'+ 'search_query='+query+'&max_results='+str(max)+'&id_list='+','.join(favlistv) +'&sortBy=submittedDate&sortOrder=descending')
        data = urllib.request.urlopen('https://export.arxiv.org/api/query?id_list='+','.join(list(set(favlistv))) +sort_method).read()
        search = feedparser.parse(data)
      else:

        data = urllib.request.urlopen('https://export.arxiv.org/api/query?search_query='+query+'&max_results='+str(max)+ sort_method).read()
        search = feedparser.parse(data)

      time_diff = time.time()-strtime


      all_text = []
      count = 0
      for idx, result in enumerate(search['entries']):
        skip = False

        categories = result['arxiv_primary_category']['term']
        title = result['title']
        authors = ', '.join([i.name for i in result['authors']])
        comments = result['arxiv_comment'] if ('arxiv_comment' in result.keys()) else None
        jour_ref = result['arxiv_journal_ref'] if ('arxiv_journal_ref' in result.keys()) else None
        arxiv_id = result['id']
        pdf_url = arxiv_id.replace('abs', 'pdf')
        #print (result['published'])
        published = '-'.join(result['published'].split('-')[:2])#+'-'+result['published'].split('-')[2][:2]
        id_ = arxiv_id.split('/')[-1]


        if comments is not None:
          for q in confs[2:]:
            if q.lower() in comments.lower():
              conf_name_show = q
              if 'workshop' in comments.lower():
                 conf_name_show = conf_name_show +' (w)'
              skip = True

        if jour_ref is not None and skip is False:

          for q in confs[2:]:
            if q.lower() in jour_ref.lower():
              conf_name_show = q
              if 'workshop' in jour_ref.lower():
                conf_name_show = conf_name_show +' (w)'
              skip = True

        if skip is False:
          conf_name_show = 'arXiv'

        if skip ==True and conf == 'arXiv':
          continue

        if int(select_id)==-1:
          conf_name_show = conf

        author_list = authors#', '.join([au.name for au in result.authors])
        if arxiv_id.split('/abs/')[-1][:-2] in favlist:
          check_fav = True
        else:
          check_fav = False

        text = result['title'] + ' ' + result['summary']

        if int(select_option)==0:
          if string is None or string.strip() is "":
            pass
          elif string.lower() in text.lower():
            pass
          else:
            continue
        elif int(select_option)==1:
          if string is None or string.strip() is "":
            pass
          elif sum([ ij.lower() in text.lower() for ij in string.split(' ')]) == len(string.split(' ')):
            pass
          else:
            continue
        else:
          pass

        if conf !='arXiv':
          if id_[:-2] in pwcdata.keys():
            arxiv_list = html.Div([dbc.Checkbox(className="form-check-input", checked = check_fav, id = {'type': 'check-fav','index': arxiv_id},  style={'margin-top':'7px'}), dbc.Badge('[' + published + '] ', color="primary", className="mr-1"),

                                dbc.Badge(conf_name_show, color="success", className="mr-1"),
                                dbc.Badge('code', color="danger", href = pwcdata[id_[:-2]], className="mr-1", target='_blank'),
                                dbc.Badge(title, color="light", href = arxiv_id, className="mr-1", id={'type': 'title','index': arxiv_id}, target='_blank') ,
                                dbc.Badge('[pdf]', color="light", href = pdf_url, className="mr-1", target='_blank'),
                                #dbc.Badge('[code]', color="light", href = pwcdata[id_[:-2]], className="mr-1", target='_blank'), 
                                html.P(author_list, style={
                                  'margin-top':   '0px',
                                  'margin-left':  '20px',
                                  'font-size': '12px'}),
                                #dbc.Badge('[abstract]', color="light",href = result.pdf_url, className="mr-1"),
                                html.Hr()
                                ])
          else:
            if code_option == True:

              continue

            arxiv_list = html.Div([dbc.Checkbox(className="form-check-input", checked = check_fav, id = {'type': 'check-fav','index': arxiv_id},  style={'margin-top':'7px'}), dbc.Badge('[' + published + '] ', color="primary", className="mr-1"),

                                dbc.Badge(conf_name_show, color="success", className="mr-1"),
                                #
                                dbc.Badge(title, color="light", href = arxiv_id, className="mr-1", id={'type': 'title','index': arxiv_id}, target='_blank') ,
                                dbc.Badge('[pdf]', color="light", href = pdf_url, className="mr-1", target='_blank'),
                                #dbc.Badge('[code]', color="light", href = pwcdata[id_[:-2]], className="mr-1", target='_blank'), 
                                html.P(author_list, style={
                                  'margin-top':   '0px',
                                  'margin-left':  '20px',
                                  'font-size': '12px'}),
                                #dbc.Badge('[abstract]', color="light",href = result.pdf_url, className="mr-1"),
                                html.Hr()
                                ])
        else:
          if comments !=None:
            comtext = 'Comment: '+ comments
          elif jour_ref !=None:
            comtext = 'Comment: '+ jour_ref
          else:
            comtext = None

          if id_[:-2] in pwcdata.keys():
            arxiv_list = html.Div([dbc.Checkbox(className="form-check-input", checked = check_fav, id = {'type': 'check-fav','index': arxiv_id},  style={'margin-top':'7px'}), dbc.Badge('[' + published + '] ', color="primary", className="mr-1"),

                                dbc.Badge(conf_name_show, color="success", className="mr-1"),
                                dbc.Badge('code', color="danger", href = pwcdata[id_[:-2]], className="mr-1", target='_blank'),
                                dbc.Badge(title, color="light", href = arxiv_id, className="mr-1", id={'type': 'title','index': arxiv_id}, target='_blank') ,
                                dbc.Badge('[pdf]', color="light", href = pdf_url, className="mr-1", target='_blank'),
                                #dbc.Badge('[code]', color="light", href = pwcdata[id_[:-2]], className="mr-1", target='_blank'), 
                                html.P(author_list, style={
                                  'margin-top':   '0px',
                                  'margin-left':  '20px',
                                  'font-size': '12px'}),
                                html.P(comtext, style={
                                  'margin-top':   '-10px',
                                  'margin-left':  '20px',
                                  'font-size': '12px',
                                  'color':'blue'}),

                                #dbc.Badge('[abstract]', color="light",href = result.pdf_url, className="mr-1"),
                                html.Hr()
                                ])
          else:
            if code_option == True:

              continue

            arxiv_list = html.Div([dbc.Checkbox(className="form-check-input", checked = check_fav, id = {'type': 'check-fav','index': arxiv_id},  style={'margin-top':'7px'}), dbc.Badge('[' + published + '] ', color="primary", className="mr-1"),

                                dbc.Badge(conf_name_show, color="success", className="mr-1"),
                                #
                                dbc.Badge(title, color="light", href = arxiv_id, className="mr-1", id={'type': 'title','index': arxiv_id}, target='_blank') ,
                                dbc.Badge('[pdf]', color="light", href = pdf_url, className="mr-1", target='_blank'),
                                #dbc.Badge('[code]', color="light", href = pwcdata[id_[:-2]], className="mr-1", target='_blank'), 
                                html.P(author_list, style={
                                  'margin-top':   '0px',
                                  'margin-left':  '20px',
                                  'font-size': '12px'}),
                                html.P(comtext, style={
                                  'margin-top':   '-10px',
                                  'margin-left':  '20px',
                                  'font-size': '12px',
                                  'color':'blue'}),

                                #dbc.Badge('[abstract]', color="light",href = result.pdf_url, className="mr-1"),
                                html.Hr()
                                ])

        #print ( 'https://imgsvcga.s3.ap-south-1.amazonaws.com/'+id_+'.pdf.jpg')
        count = count + 1
        all_text.append(arxiv_list)
        #if is_abs:
        #  all_text.append(html.P('Abstract: ' + result['summary'], style={
        #                        'margin-top':   '0px',
        #                        'margin-left':  '20px',
        #                        'font-size': '10px'}),
        #                    #dbc.Badge('[abstract]', color="light",href = result.pdf_url, className="mr-1"),
        #                    #html.Img(src = 'http://www.arxiv-sanity.com/static/thumbs/2104.08850v1.pdf.jpg')
        #                    )
      all_text = [html.P('fetched '+str(count) + ' results in '+str(round(time_diff, 2)) +' seconds' , style={
                              'margin-top':   '0px',
                              'margin-left':  '0px',
                              'font-size': '12px'})] + all_text



      return all_text, dash.no_update

  else:




      return dash.no_update, dash.no_update


@app.callback(
    Output(component_id='dummy', component_property='children'),
    [Input(component_id={'type': 'check-fav',  'index': ALL}, component_property='checked')],)
   # [State(component_id='check-fav', component_property='id')])

def update_fav(checked):

    #print ('********')

    #print (checked, len(dash.callback_context.triggered),dash.callback_context.triggered[0]['prop_id'])

    if len(dash.callback_context.triggered) == 1:

      if dash.callback_context.triggered[0]['value'] == True:
        arxivid = dash.callback_context.triggered[0]['prop_id'].split('/abs/')[1].split('","type":"check-fav"')[0]

        with open('arxivbox/logfav', 'a+') as f:
          f.write(arxivid + '\n')
          f.close()

      if dash.callback_context.triggered[0]['value'] == False:

        arxivid = dash.callback_context.triggered[0]['prop_id'].split('/abs/')[1].split('","type":"check-fav"')[0]
        #print (arxivid)

        with open('arxivbox/logfav', 'r') as f:
          favlist = [ii[:-1] for ii in f.readlines()]
          f.close()

        #if arxivid in favlist:
        #  #print ('removed')
        #  favlist.remove(arxivid)

        favlist = [i for j, i in enumerate(favlist) if i != arxivid]

        with open('arxivbox/logfav', 'w+') as f:
          for i in favlist:
            f.write(i + '\n')
          f.close()




if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    app.run_server(port=port, debug=False)







