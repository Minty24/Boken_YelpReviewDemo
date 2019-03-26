#libraies
from math import pi
import numpy as np
import pandas as pd
from collections import Counter
from bokeh.plotting import figure
from bokeh.layouts import widgetbox,row,column
from bokeh.models import (ColumnDataSource,HoverTool,ResetTool,
                         UndoTool,RedoTool,ZoomInTool,ZoomOutTool,
                          BoxSelectTool,
                         SaveTool,PanTool,CategoricalColorMapper,
                         Spacer,LabelSet,LinearAxis)
from bokeh.models.widgets import Select,RangeSlider,TextInput
from bokeh.palettes import RdYlGn
from bokeh.io import curdoc
from bokeh.sampledata.us_states import data as states

if 'HI' in states:
    del states['HI']
elif 'AK' in states:
    del states['AK']
else:
    pass

state_xs = [states[code]["lons"] for code in states]
state_ys = [states[code]["lats"] for code in states]


text = TextInput(title="Input Abbreviation of State you want to search, ex: NY(New York)")
search = TextInput(title="Type the Category you want to search")
slider = RangeSlider(start=0,end=24,step=1,value=(8,23),title='Hours')
hover = HoverTool(tooltips=[('Name','@name'),
                            ('Address','@address'),
							('City','@city'),
							('State','@state'),
							('Zipcode','@Zip'),
                            ('Rating', '@rating'),
							('Currently Opening','@status')
							])

hover_bar = HoverTool(tooltips=[('Rating','@x1'),
                                ('Number of Business','@y1')
							])

hover_pie = HoverTool(tooltips=[('Percentage','@ratio')
							])

select_day = Select(
                options=['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday','Friday','Saturday'],
                value='Monday',
                title='Day of the Week'
)

chosen_tools =[hover,ResetTool(),BoxSelectTool(),
               SaveTool(),PanTool(),
               UndoTool(),RedoTool(),ZoomInTool(),
               ZoomOutTool()
               ]

#data
data = pd.read_csv(r'~/Desktop/yelp_business.csv',index_col='business_id')
hour = pd.read_csv(r'~/Desktop/yelp_business_hours.csv',index_col='business_id')
#data = pd.read_csv(r'E:\project\CIS4170\yelp\yelp_business.csv',index_col='business_id')
#hour = pd.read_csv(r'E:\project\CIS4170\yelp\yelp_business_hours.csv',index_col='business_id')
whole = pd.merge(data,hour, left_index=True, right_index=True)

#data = pd.read_csv(r'E:\Software\WinPython\notebooks\yelp\yelp_business.csv',index_col='business_id')
state_data = whole[whole.state=='NV']
categoricaldata = state_data.categories.str.contains('')
open_data = state_data.loc[state_data[select_day.value.lower()] != 'None']
new_data = open_data.where(categoricaldata).dropna(thresh = 19).sort_values(by=['stars'],ascending=False)

#filter_data = new_data.categories.split(';')

source = ColumnDataSource(data={
    'x'       : (new_data.longitude.values),
    'y'       : (new_data.latitude.values),
    'rating'  : new_data.stars.astype(str),
    'status'  : new_data.is_open.astype(str).replace({'0':'Closed','1':'Open'}),
    'name'    : new_data.name,
    'address' : new_data.address,
	'city'	  : new_data.city,
	'state'   : new_data.state,
	'Zip'     :new_data.postal_code
    })

histo_source = Counter(new_data.stars)
keys,values = list(histo_source.keys()), list(histo_source.values())
source1 = ColumnDataSource(data={
            'x1' : keys,
            'y1' : values
})

total = sum(histo_source.values())
great = histo_source[4.0]+histo_source[4.5]+histo_source[5.0]
ratio1 = great/total

pie_source1 = ColumnDataSource(data={
                            'ratio':[ratio1, 1-ratio1],
                            'start':[0, ratio1*2*pi],
                            'end': [ratio1*2*pi, 2*pi],
                            'color': ['darkgreen', 'darkred']
})


xmin, xmax = (new_data.longitude.median()-10), (new_data.longitude.median()+10)
ymin, ymax = (new_data.latitude.median()-5), (new_data.latitude.median()+5)

rating_list = new_data.stars.unique().astype(str).tolist()
palettes_list = len(rating_list)
if palettes_list < 3:
    mapper == False
else:
    mapper = CategoricalColorMapper(palette=RdYlGn[palettes_list], factors=rating_list)


plot = figure(title='Yelp Rating',
              x_range=(xmin, xmax),
              y_range=(ymin, ymax),
              plot_width=500,
              plot_height=400,
              tools=chosen_tools)

plot.circle(x = 'x',
            y = 'y',
            fill_alpha=0.7,
            source=source,
            color = {'field':'rating','transform': mapper},
            legend='rating'
            )

bar1 = figure(title="Overall Rating within this Area",
              tools = [hover_bar,SaveTool()],
              plot_width = plot.plot_width,
              plot_height = 400,background_fill_color="white")

bar1.vbar(x='x1', width=0.3, bottom=0,top='y1', color='firebrick', source = source1)

labels = LabelSet(x='x1', y='y1',text = 'y1',
                  x_offset=-13.5,level = 'glyph',
                  source=source1, render_mode='canvas')
bar1.add_layout(labels)

plot.patches(state_xs, state_ys, fill_alpha=0.0,
          line_color="#884444", line_width=2, line_alpha=0.3)

#plot.legend.click_policy="mute"
plot.title.text_font_size = '16pt'
plot.title.align = 'left'

pie1 = figure(title = 'Percentage of 4 Stars and above in this category',
              plot_width = plot.plot_width,
              plot_height = 400,
              tools = [hover_pie,SaveTool()])

pie1.wedge(x=0, y=0, start_angle='start', end_angle='end', radius=0.7,
        color='color', alpha=0.8, source=pie_source1)

#defining the update function
def update_value(attr, old, new):

    state_data1 = whole[whole.state==text.value]
    categoricaldata1 = state_data1.categories.str.contains(search.value)
    open_data1 = state_data1.loc[state_data1[select_day.value.lower()] != 'None']
    new_data1 = open_data1.where(categoricaldata1).dropna(thresh = 18).sort_values(by=['stars'],ascending=False)


    update_data={
    'x'       : new_data1.longitude,
    'y'       : new_data1.latitude,
    'rating'  : new_data1.stars.astype(str),
    'state'   : new_data1.state,
    'name'    : new_data1.name,
    'address' : new_data1.address,
    'status'  : new_data1.is_open.astype(str),
    'Day'     : new_data1.name,
    'city'	  : new_data.city,
    'state'   : new_data.state,
    'Zip'     :new_data.postal_code
    }


    histo_source1 = Counter(new_data1.stars)
    keys1,values1 = list(histo_source1.keys()), list(histo_source1.values())
    update_data1 ={
    		'x1' : keys1,
    		'y1' : values1
    }

    total1 = sum(histo_source1.values())
    great1 = histo_source1[4.0]+histo_source1[4.5]+histo_source1[5.0]
    ratio12 = great1/total1
    update_data2 ={
                    'start':[0, ratio12*2*pi],
                    'end':[ratio12*2*pi, 2*pi],
                    'ratio':[ratio12, 1-ratio12],
                    'color':['darkgreen', 'darkred']
    }

    source.data = update_data
    source1.data = update_data1
    pie_source1.data = update_data2

    xmin, xmax = (new_data1.longitude.median()-10), (new_data1.longitude.median()+10)
    ymin, ymax = (new_data1.latitude.median()-5), (new_data1.latitude.median()+5)

    rating_list = new_data1.stars.unique().astype(str).tolist()
    palettes_list = len(rating_list)
    if palettes_list < 3:
    	mapper == False
    else:
    	mapper = CategoricalColorMapper(palette=RdYlGn[palettes_list], factors=rating_list)

    plot.title.text = 'Yelp Rating about %s in %s on %s' % (search.value,text.value,select_day.value)

text.on_change('value',update_value)
select_day.on_change('value',update_value)
slider.on_change('value', update_value)
search.on_change('value', update_value)
#hover.on_change('value',update_value)

layout = row(widgetbox(text,slider,search,select_day), column(plot,row(bar1,pie1)))
curdoc().add_root(layout)
curdoc().title = "Yelp Rate in US"
