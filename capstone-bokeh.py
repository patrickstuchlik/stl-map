import pandas as pd
import requests
#import matplotlib.pyplot as plt
import json
from bokeh.io import output_notebook, show, output_file, curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, AdaptiveTicker, ColumnDataSource
from bokeh.palettes import brewer
import bokeh
from bokeh import palettes
from bokeh.layouts import row, column, layout
from bokeh.models.widgets import Select

def parse_json(url):
       r = requests.get(url)
       g = json.loads(r.content)
       dfeat = dict()
       for i in g['features']:
              dfeat[i['properties']['GEOID']] = {'xs': [x[0] for innerx in i['geometry']['coordinates'] for x in innerx],
                                               'ys': [y[1] for innery in i['geometry']['coordinates'] for y in innery],
                                               'outp_life' : i['properties']['outp_life'],
                                               'outp_outp' : i['properties']['outp_outp'],
                                               'outp_food1' : i['properties']['outp_food1'],
                                               'outp_mw' : i['properties']['outp_mw'],
                                               'outp_cg' : i['properties']['outp_cg'],
                                               'outp_metro' : i['properties']['outp_metro'],
                                               'outp_bike_' : i['properties']['outp_bike_'],
                                               'outp_park1' : i['properties']['outp_park1'],
                                               'outp_walk' : i['properties']['outp_walk'],
                                               'outp_unins' : i['properties']['outp_unins'],
                                               }
       return pd.DataFrame.from_dict(dfeat,orient='index',columns=['xs','ys','outp_life','outp_outp','outp_food1','outp_mw','outp_cg','outp_metro','outp_bike_','outp_park1','outp_walk','outp_unins'])

urlbokeh = 'https://raw.githubusercontent.com/patrickstuchlik/shape1/master/stl.json'

bef = {'Food Access (%)' : 'outp_food1',
       'Milkweed Gardens (Number)' : 'outp_mw',
       'Community Gardens (Number)' : 'outp_cg',
       'Metrolink (Number)' : 'outp_metro',
       'Bike Lanes (Miles)' : 'outp_bike_',
       'Public Parks (Sq Ft)' : 'outp_park1',
       'Walkability (Score)' : 'outp_walk',
       'Uninsured (%)' : 'outp_unins'
}

feb = {bef[k] : k for k in bef}

def get_dataset(src,bg):
       df = src[['xs','ys','outp_life','outp_outp',str(bg)]]
       # df2 = pd.DataFrame()
       # df2['xs']=df['xs']
       # df2['ys']=df['ys']
       # df2['outp_life']=df['outp_life']
       # df2['outp_outp']=df['outp_outp']
       # df2[str(bg)] = df[str(bg)]
       return ColumnDataSource(data=df)

def make_plot(source,bgvar):
       #Define a sequential multi-hue color palette.
       palette = bokeh.palettes.Plasma[7]
       #Reverse color order so that dark blue is highest obesity.
       palette = palette[::-1]
       #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
       color_mapper = LinearColorMapper(palette = palette)

       hover = HoverTool(tooltips = [ ('Life Expectancy','@outp_life'),('Predicted Life Expectancy','@outp_outp'),(feb[str(bgvar)],('@'+str(bgvar)))])
       #Create color bar.
       ticker = AdaptiveTicker()

       color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 20, height = 500,
       border_line_color=None,location = (0,0), orientation = 'vertical',ticker=ticker)
       #Create figure object.
       p = figure(title = 'Life Expectancy', plot_height = 600 , plot_width = 450, toolbar_location = None, tools=[hover])
       p.xgrid.grid_line_color = None
       p.ygrid.grid_line_color = None
       #Add patch renderer to figure. 
       p.patches('xs','ys', source = source,fill_color = {'field' :str(bgvar), 'transform' : color_mapper}, line_color = 'black', line_width = 0.25, fill_alpha = 1)
       #Specify figure layout.
       p.add_layout(color_bar, 'right')
       return p

bef_select = Select(value='Uninsured', title='Built Environment Feature', options=sorted(bef.keys()))
bef1 = bef_select.value

df = parse_json(urlbokeh)
source = get_dataset(df,bef[bef1])
plot1 = make_plot(source,bef[bef_select.value])

def update_plot(attrname, old, new):
       #bef1 = bef[bef_select.value]

       # src = get_dataset(df,bef[bef_select.value])
       # source.data.update(src.data)
       source.data = get_dataset(df,bef[bef_select.value]).data
       newplot = make_plot(source,bef[bef_select.value])
       layout.children[0].children[0] = newplot

bef_select.on_change('value', update_plot)
#controls = bef_select
layout = layout([[plot1,bef_select]])
curdoc().add_root(layout)
curdoc().title = "Life Expectancy"
#output_notebook()
#show(row(plot1,controls))
