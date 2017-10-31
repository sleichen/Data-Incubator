from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import numpy as np
import itertools
from bokeh.plotting import figure, show, output_notebook
from bokeh.embed import components
import seaborn as sns

import state_abbr

app = Flask(__name__)

agi_data = pd.read_csv('agi_data',index_col = 0)
plot_data = agi_data[['agi05','agi06','agi07','agi08','agi09','agi10','agi11','agi12','agi13','agi14']]

@app.route('/')
@app.route('/index.html', methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        script = "states_list = ['California']"
        bok_div = ''
        bok_script = ''      
        
    if request.method == 'POST':
        states_list = [str(state) for state in request.form["states"].split(',')]
        states_abbr = state_abbr.toggle_abbr(states_list)
        script = "states_list = %s;" % str(states_list)
       

        # define the color palette
        ncolors = 5
        palette = sns.palettes.color_palette('colorblind', ncolors)
        # as hex is necessary for bokeh to render the colors properly.
        colors = itertools.cycle(palette.as_hex())

        plot = figure(plot_width=400, plot_height=400,\
             title = 'Total Adjusted Gross Income',
             x_axis_label = 'Year',
             y_axis_label = 'AGI ($ millions)')


        for state, color in itertools.izip(states_abbr, colors):
            plot.line([5,6,7,8,9,10,11,12,13,14],plot_data.loc[state]/10**6,line_width=3,legend = state,line_color = color)    

        
        
        bok_script, bok_div = components(plot)  
    
    return render_template('/index.html', script = script, bok_script = bok_script, bok_div = bok_div )
        
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=33507)
