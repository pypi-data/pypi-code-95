# -*- coding: utf-8 -*-
#
# Copyright 2021 Compasso UOL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Report Class Implementation"""
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import base64
from io import BytesIO



class Report():
    def __init__(self, summary_dict:dict,  output_dir:str):
        """Initialize the report class
        :param summary_dict: The dictionary with the summary of the files read
        :param output_dir: Output Directory
        """
        self.summary_dict = summary_dict
        self.output_dir = output_dir


    def create_visual(self):
        """Create the report's table and chart
        :return: the table in html and the encoded chart
        """
        #Table 1
        df = pd.DataFrame.from_dict(self.summary_dict["Files"], orient='index')
        df.reset_index(inplace = True)
        df.columns = ["Files","Number of Queries", "Successful Queries", "Failed Queries", "Errors Types"]
        for i in df:
            if i != "Failed Queries":
                df[i] = df[i].apply(pd.Series)
            else:
                df_failed =  pd.json_normalize(df["Failed Queries"])
                df = df.drop(["Failed Queries"], axis = 1)
        df = df.join(df_failed)
        df = df.fillna(0)
        table_html = df.to_html(classes="mt40 datatable", table_id = "T_0001")
        # Chart
        er_types = df.iloc[:, 3].tolist()
        r_types = [ item for elem in er_types for item in elem]
        er = pd.DataFrame(r_types)
        er.columns = ["errors"]
        sns.set_theme(style="whitegrid")
        ax = sns.countplot(y = er.iloc[:,0], palette=["black"],  order=er.errors.value_counts().iloc[:10].index)
        plt.title('Most Common Errors')
        total = len(er)
        for p in ax.patches:
            percentage = '{:.1f}%'.format(100 * p.get_width()/total)
            x = p.get_x() + p.get_width() + 0.02
            y = p.get_y() + p.get_height()/2
            ax.annotate(percentage, (x, y))
        fig = plt.gcf()
        fig.set_size_inches(14, 5)
        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        data_u = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        img_tag = '<img src="data:image/png;base64,{0}" style="max-height: 600px; max-width: 800px;">'.format(data_u)

        return table_html,img_tag

    def generate_report(self):
        """Create the report in html
        """
        table_html,img_tag = self.create_visual()

        heading = '<h1 style="font-style: italic;">Migration Report</h1>'

        n_files = self.summary_dict['Failed_files'] + self.summary_dict['Sucess_files']

        input_dir = '<li><b>Input Directory: </b>'+ self.summary_dict['Input_dir'] + '</li>'
        source = '<li><b>Source: </b>'+ self.summary_dict['From_dialect'] + '</li>'
        destination = '<li><b>Target: </b>'+ self.summary_dict['To_dialect'] + '</li>'
        total_files = '<dt><li><b>Total Files Read: </b>'+ str(n_files) + '</li></dt>'
        sus_files = '<dd><li><b>Fully Translated: </b>'+ str(self.summary_dict['Sucess_files']) + '</li></dd>'
        fai_files = '<dd><li><b>Partially Translated: </b>'+ str(self.summary_dict['Failed_files']) + '</li></dd>'

        info = '<dl>'+input_dir+source+destination+total_files+sus_files+fai_files+'</dl>'

        table_head = '''<h3><span style="font-style: italic;">Detailed analysis</span>
                            <input style="width: 300px; margin-left: auto; float: right;" 
                            type="search" placeholder="Search..." class="form-control search-input" data-table="datatable"/>
                        </h3>'''

        table_style = '''<style  type="text/css" > #T_0001 thead {background-color: #000;color: white;}    
                        #T_0001 th,td {text-align: center;border: 1px solid #706E6E;padding: 5px;}    
                        #T_0001 {border-collapse: collapse;font-size: 11pt;border: 1px solid #706E6E;margin-left: auto;margin-right: auto;}
                        </style>'''

        table_script = '''<script>
        (function(document) {
            'use strict';
            var F_Table = (function(Array) {
                var input;
                function _InSearch(e) {
                    input = e.target;
                    var tables = document.getElementsByClassName(input.getAttribute('data-table'));
                    Array.forEach.call(tables, function(table) {
                        Array.forEach.call(table.tBodies, function(tbody) {
                            Array.forEach.call(tbody.rows, function(row) {
                                var content = row.textContent.toLowerCase();
                                var search_val = input.value.toLowerCase();
                                row.style.display = content.indexOf(search_val) > -1 ? '' : 'none';
                            });
                        });
                    });
                }
                return {
                    init: function() {
                        var inputs = document.getElementsByClassName('search-input');
                        Array.forEach.call(inputs, function(input) {
                            input.oninput = _InSearch;
                        });
                    }
                };
            })(Array.prototype);
            document.addEventListener('readystatechange', function() {
                if (document.readyState === 'complete') {
                    F_Table.init();
                }
            });
        })(document);
       </script>'''    


        table = '<div class="container">' + table_head + table_style + table_html + '</div>' + table_script 


        fig = '<div class="chart"> '+ '<h3 style="font-style: italic;">Main errors:</h3>'+ img_tag +'</div>'

        html =  heading + info + fig + table 


        report = os.path.join(self.output_dir, "Report")
        if not os.path.exists(report):
            os.makedirs(report)
        with open(report+"/report.html","w+") as file:
                file.write(html)
        
