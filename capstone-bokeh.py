import pandas as pd
import requests
#import matplotlib.pyplot as plt
import json
from bokeh.io import output_notebook, show, output_file, curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, AdaptiveTicker, ColumnDataSource, Paragraph
from bokeh.palettes import brewer
import bokeh
from bokeh import palettes
from bokeh.layouts import row, column, layout, Spacer
from bokeh.models.widgets import Select
from bokeh.tile_providers import get_provider, Vendors
import pyproj

tile_provider = get_provider(Vendors.CARTODBPOSITRON)

crs = pyproj.CRS.from_epsg(3857)

proj = pyproj.Transformer.from_crs(crs.geodetic_crs,crs)

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

def web_mercator(df):
       testlist1 = []
       for sublist in list(zip(df['xs'],df['ys'])):
              testlist1.append(list(zip(*sublist)))

       ptest = []
       for tract in testlist1:
              ptest.append([proj.transform(pt[1],pt[0]) for pt in tract])

       xlist = []
       ylist = []
       for tract in ptest:
              xlist.append([i[0] for i in tract])
              ylist.append([i[1] for i in tract])

       df['xs'] = xlist
       df['ys'] = ylist
       return df

def make_plot(source,bgvar):
       #Define a sequential multi-hue color palette.
       palette = bokeh.palettes.viridis(256)
       #Reverse color order so that dark blue is highest obesity.
       palette = palette[::-1]
       #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
       color_mapper = LinearColorMapper(palette = palette)

       hover = HoverTool(tooltips = [ ('Life Expectancy','@outp_life'),('Predicted Life Expectancy','@outp_outp'),(feb[str(bgvar)],('@'+str(bgvar)))])
       #Create color bar.
       ticker = AdaptiveTicker(desired_num_ticks = 8)

       color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 20, height = 500,
       border_line_color=None,location = (0,0), orientation = 'vertical',ticker=ticker)
       #Create figure object.
       p = figure(title = 'Life Expectancy in the City of St Louis, MO', plot_height = 600 , plot_width = 450, toolbar_location = None, tools=[hover],x_range=(-10060000, -10035000), y_range=(4658000, 4685000), x_axis_type="mercator", y_axis_type="mercator")
       p.add_tile(tile_provider)
       p.xgrid.grid_line_color = None
       p.ygrid.grid_line_color = None
       #Add patch renderer to figure. 
       p.patches('xs','ys', source = source,fill_color = {'field' :str(bgvar), 'transform' : color_mapper}, line_color = 'black', line_width = 0.25, fill_alpha = 0.26)
       #Specify figure layout.
       p.add_layout(color_bar, 'right')
       
       return p

bef_select = Select(value='Uninsured (%)', title='Built Environment Feature', options=sorted(bef.keys()))
bef1 = bef_select.value

df_start = parse_json(urlbokeh)
df = web_mercator(df_start)
source = get_dataset(df,bef[bef1])
plot1 = make_plot(source,bef[bef_select.value])

def update_plot(attrname, old, new):
       #bef1 = bef[bef_select.value]

       # src = get_dataset(df,bef[bef_select.value])
       # source.data.update(src.data)
       source.data = get_dataset(df,bef[bef_select.value]).data
       newplot = make_plot(source,bef[bef_select.value])
       layout.children[0] = newplot

bef_select.on_change('value', update_plot)
#controls = bef_select
para = Paragraph(text = "This interactive map displays the results of my machine learning model predicting life expectancy in each census tract, based on eight different measures of the built environment (which you can choose above!), along with the empirically measured life expectancy for each census tract, and the built environment factor you selected. The colors of the map are a visual representation of how the selected built environment measure differs across the city by census tract. Indigo census tracts have the highest measured values, like downtown St. Louis has the most Metrolink stations (4), while yellow census tracts have the lowest measured values, like most of the rest of city has no Metrolink stations at all.")
# layout = layout(children = [
#     [plot1],[bef_select, para]
#     ], sizing_mode = 'fixed')

layout = row(plot1,column(bef_select,Spacer(height_policy = "max"),para,Spacer(height = 160)))
curdoc().add_root(layout)
curdoc().title = "Life Expectancy in the City of St Louis, MO"
#output_notebook()
#show(row(plot1,controls))
