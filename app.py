from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import numpy as np
import itertools
from bokeh.plotting import figure, show, output_notebook
from bokeh.embed import components
from bokeh.layouts import widgetbox, column
from bokeh.models import CustomJS, ColumnDataSource, ranges, LabelSet
from bokeh.models.widgets import Dropdown, CheckboxButtonGroup
from bokeh.palettes import PuBu
#import seaborn as sns

import state_abbr

app = Flask(__name__)

observed_data = pd.read_csv('observed_agi_per_return',index_col = 0)
predicted_data = pd.read_csv('predicted_agi_per_return',index_col = 0)

@app.route('/')
@app.route('/index.html', methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        script = "states_list = ['California']"
        lineplot_div = ''
        lineplot_script = ''
        barplot_div = ''
        barplot_script = ''
          

        
    if request.method == 'POST':
        states_list = [str(state) for state in request.form["states"].split(',')]
        states_abbr = state_abbr.toggle_abbr(states_list)
        script = "states_list = %s;" % str(states_list)
       

        # define the color palette
        #ncolors = 5
        #palette = sns.palettes.color_palette('colorblind', ncolors)

        # as hex is necessary for bokeh to render the colors properly.
        #colors = itertools.cycle(palette.as_hex())
        colors = itertools.cycle(['#0072b2', '#009e73', '#d55e00', '#cc79a7', '#f0e442'])


        plot = figure(plot_width=400, plot_height=400,\
        title = 'Adjusted Gross Income per Return',\
        x_axis_label = 'Year',\
        y_axis_label = 'AGI/Return ($ thousands)')

        pred_plots = []
        obs_plots = []
        for state, color in itertools.izip(states_abbr, colors):
            #predicted = plot.line([8,9,10,11,12,13,14,15,16],predicted_data.loc[state],line_width=3,legend = state,\
            #          line_color = color,line_dash="4 4")
            pred_plots.append(plot.line([8,9,10,11,12,13,14,15,16],predicted_data.loc[state],line_width=3,legend = state,\
              line_color = color,line_dash="4 4"))
            #observed = plot.line([5,6,7,8,9,10,11,12,13,14,15],observed_data.loc[state],line_width=3,legend = state,line_color = color)
            obs_plots.append(plot.line([5,6,7,8,9,10,11,12,13,14,15],observed_data.loc[state],line_width=3,legend = state,line_color = color))
            plot.legend.location = 'top_left'

        checkbox_button_group = CheckboxButtonGroup(\
            labels=["Recorded Data", "Predictions"], active=[0, 1])

        args = {'predicted' + str(i) : pred_plots[i] for i in xrange(len(pred_plots))}
        args.update({'observed' + str(i) : obs_plots[i] for i in xrange(len(obs_plots))})
        args['checkbox_button_group']=checkbox_button_group

        code = ""
        for i in xrange(len(obs_plots)):
            code += "predicted"+ str(i)+".visible = checkbox_button_group.active.includes(1); \n"
            code += "observed"+ str(i)+".visible = checkbox_button_group.active.includes(0);"

        checkbox_button_group.callback = CustomJS(args=args, code=code)
        
        layout = column(plot,checkbox_button_group)
        lineplot_script, lineplot_div = components(layout)  
    


        correlations = pd.read_csv('correlations',index_col = 0)

        source = ColumnDataSource(dict(x = list(correlations.index), 
                              y =list(correlations.values)))

        x_label = "Feature"
        y_label = "Correlation Coefficient"
        title = "Features Correlated with AGI/Return"
        plot = figure(plot_width=600, plot_height=600, tools="save",
            x_axis_label = x_label,
            y_axis_label = y_label,
            title=title,
            x_minor_ticks=2,
            x_range = source.data["x"],
            y_range= ranges.Range1d(start=-0.4,end=0.3))


        #labels = LabelSet(x='x', y='y', text='y', level='glyph',
        #        x_offset=-13.5, y_offset=0, source=source, render_mode='canvas')

        plot.vbar(source=source,x='x',top='y',bottom=0,width=0.3, color = '#40e0d0') #, color=PuBu[7][2])
        plot.xaxis.major_label_orientation = np.pi/3

        #plot.add_layout(labels)
        barplot_script, barplot_div = components(plot) 




    return render_template('/index.html', script = script, lineplot_script = lineplot_script,
                         lineplot_div = lineplot_div, barplot_script = barplot_script,
                         barplot_div = barplot_div )
        
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=33507)
