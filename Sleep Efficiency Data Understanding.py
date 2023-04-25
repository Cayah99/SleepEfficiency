#!pip install bokeh

from bokeh.io import curdoc, output_notebook
from bokeh.layouts import layout, column, row, gridplot
from bokeh.models import ColumnDataSource, Select, Div, RangeSlider, Range1d, HoverTool, Circle, Grid, Line, LinearAxis, Plot, FactorRange
from bokeh.plotting import figure, show
import pandas as pd
from bokeh.palettes import Viridis6
from bokeh.transform import dodge
from bokeh.models.widgets import Panel, Tabs
from sklearn.preprocessing import MinMaxScaler

df_sleep_efficiency = pd.read_csv('Data/Sleep_Efficiency.csv')

changed_df_sleep_efficiency = df_sleep_efficiency.copy()
changed_df_sleep_efficiency['Sleep efficiency'] = [round(num, 1) for num in changed_df_sleep_efficiency['Sleep efficiency']]
df_dummies_smoking= pd.get_dummies(changed_df_sleep_efficiency["Smoking status"])
changed_df_sleep_efficiency = pd.concat((df_dummies_smoking, changed_df_sleep_efficiency), axis=1)
changed_df_sleep_efficiency = changed_df_sleep_efficiency.drop(["Smoking status"], axis=1)
changed_df_sleep_efficiency = changed_df_sleep_efficiency.drop(["No"], axis=1)
changed_df_sleep_efficiency = changed_df_sleep_efficiency.rename(columns={"Yes": "Smoking status"})

axis_map = {
    "Caffeine Consumption (in mg)": "Caffeine consumption",
    "Alcohol Consumption (in oz)": "Alcohol consumption",
    "Exercise Frequency (number of times per week)": "Exercise frequency"}

title = Div(text='<h2 style="text-align: center">Machine Learning Project, Sleep Efficiency</h2>')
subtitle = Div(text='<h3 style="text-align: center">Floor Halkes, Jochem Bus and Kyra Jongman</h3>')
sleep_efficiency_text = Div(text='<h3 style="text-align: center">Sleep efficiency graphs:</h3>')
age_group_text = Div(text='<h3 style="text-align: center">Age group graphs:</h3>')

gender = Select(title="Gender:", options=["Both", "Male", "Female"], value="Both", height=50)
min_age = min(changed_df_sleep_efficiency['Age'])
max_age = max(changed_df_sleep_efficiency['Age'])
slider_range = RangeSlider(title="Choose age", start=min_age, end=max_age, value=(min_age, max_age), step=1, height=50)
y_axis = Select(title="Variable to be compared with sleep efficiency: ", options=sorted(axis_map.keys()), value= "Alcohol Consumption (in oz)", height=50)

def select_gender_and_age():
    gender_val = gender.value
    age_val_1 = slider_range.value[0]
    age_val_2 = slider_range.value[1]

    if gender_val == 'Both':
        selected = changed_df_sleep_efficiency[(changed_df_sleep_efficiency["Age"] >= age_val_1) & (changed_df_sleep_efficiency['Age'] <= age_val_2)] 
    else:
        selected = changed_df_sleep_efficiency[(changed_df_sleep_efficiency["Age"] >= age_val_1) & (changed_df_sleep_efficiency['Age'] <= age_val_2)]  
        selected = selected[selected.Gender.str.contains(gender_val)] 
    return selected

#Age Group
source = ColumnDataSource(data=dict(x=[], top=[]))
p = figure(title="", sizing_mode="stretch_width")
p.vbar(x = 'x', top = 'top', source = source, width = 0.8, color='#F24300') 

#Smoking
source1 = ColumnDataSource(data=dict(x=[], top=[]))
p1 = figure(title="", sizing_mode="stretch_width")
p1.vbar(x = 'x', top = 'top', source = source1, width = 0.8, color='#F24300')

#Sleep duration
source3 = ColumnDataSource(data=dict(x=[], top = []))
p3 = figure(title="", sizing_mode="stretch_width")
p3.vbar(x = 'x', top = 'top', source = source3, width = 0.8, color='#F24300')

#Different sleep percentages (REM, deep sleep, light sleep)
source4 = ColumnDataSource(data=dict(x=[], REM_sleep = [], Deep_sleep = [], Light_sleep = []))
p4 = figure(title="", sizing_mode="stretch_width")

sleep_category = ['REM_sleep', 'Deep_sleep', 'Light_sleep']
colors = ["#FADD69", "#F24300", "#4F76B2"] 
p4.vbar_stack(sleep_category, x='x', width=0.8, color=colors, source=source4, legend_label=sleep_category)

#Other categories
source2 = ColumnDataSource(data=dict(x=[], top=[]))
p2 = figure(title="", sizing_mode="stretch_width")
p2.vbar(x = 'x', top = 'top', source = source2, width = 0.08, color="#F24300")

def update():
    #Age Group
    df_age = select_gender_and_age()
    df_age_group = df_age.copy()

    bins = [0, 18, 29, 39, 49, 59, 69, 120]
    labels = [0, 1, 2, 3, 4, 5, 6]
    df_age_group['age_group'] = pd.cut(df_age_group.Age, bins, labels = labels, include_lowest = True)
    df_grouped_age = df_age_group.groupby('age_group')["Sleep efficiency"].mean().reset_index()

    new_data = {
            'x': df_grouped_age['age_group'], 
            'top': round(df_grouped_age["Sleep efficiency"],2)}
    
    source.data = new_data
    
    p.xaxis.major_label_overrides = {0: "0-18", 1: "18-29", 2: "30-39", 3: "40-49", 4: "50-59", 5: "60-69"}
    p.xaxis.axis_label = "Age Group"
    p.yaxis.axis_label = "Sleep Efficiency"
    p.title.text = "Age Group VS Sleep Efficiency ({})".format(gender.value) 

    #Smoking
    df_smoking = select_gender_and_age()
    df_grouped_smoking = df_smoking.groupby('Smoking status')["Sleep efficiency"].mean().reset_index()

    new_data1 = {
            'x': df_grouped_smoking['Smoking status'].tolist(), 
            'top': round(df_grouped_smoking["Sleep efficiency"],2).tolist()}
    
    source1.data = new_data1

    p1.xaxis.major_label_overrides = {0: "No", 0.5: "", 1: "Yes"}
    p1.xaxis.axis_label = "Smoking Status"
    p1.yaxis.axis_label = "Sleep Efficiency"
    p1.title.text = "Sleep Efficiency VS Smoking Status ({})".format(gender.value) 

    #Sleep duration 
    df_grouped_age_2 = df_age_group.groupby('age_group')["Sleep duration"].mean().reset_index()

    new_data3 = {

            'x': df_grouped_age_2['age_group'], 
            'top': round(df_grouped_age_2["Sleep duration"],2)}
        
    source3.data = new_data3
    
    p3.xaxis.major_label_overrides = {0: "0-18", 1: "18-29", 2: "30-39", 3: "40-49", 4: "50-59", 5: "60-69"}
    p3.xaxis.axis_label = "Age Group"
    p3.yaxis.axis_label = "Average Sleep Duration"
    p3.title.text = "Age Group VS Average Sleep Duration ({})".format(gender.value) 

    #Different sleep percentages (REM, deep sleep, light sleep)
    df_grouped_age_3 = df_age_group.copy()
    df_grouped_age_3.rename(columns={'REM sleep percentage': "REM_sleep", 'Deep sleep percentage': "Deep_sleep", 'Light sleep percentage': "Light_sleep"}, inplace=True)
    df_grouped_age_sleep = df_grouped_age_3.groupby('age_group')[['REM_sleep', 'Deep_sleep', 'Light_sleep']].mean().reset_index() 

    new_data4 = {
                'x': df_grouped_age_sleep['age_group'], 
                'REM_sleep': df_grouped_age_sleep['REM_sleep'], 
                'Deep_sleep': df_grouped_age_sleep['Deep_sleep'], 
                'Light_sleep': df_grouped_age_sleep['Light_sleep']
            }
    source4.data = new_data4
    
    p4.xaxis.major_label_overrides = {0: "0-18", 1: "18-29", 2: "30-39", 3: "40-49", 4: "50-59", 5: "60-69"}
    p4.xaxis.axis_label = "Age Group"
    p4.yaxis.axis_label = "Average Percentage Sleep"
    p4.title.text = "Age Group VS Average Percentage Sleep ({})".format(gender.value)

    #Categories
    df_categories = select_gender_and_age()
    y_name = axis_map[y_axis.value]
    df_grouped_categories = df_categories.groupby('Sleep efficiency')[y_name].mean().reset_index()

    p2.xaxis.axis_label = "Sleep Efficiency"
    p2.yaxis.axis_label = y_axis.value
    p2.title.text = "Sleep Efficiency VS " + y_name + " ({})".format(gender.value) 

    new_data2 = {
            'x': df_grouped_categories["Sleep efficiency"].tolist(), 
            'top': round(df_grouped_categories[y_name],2).tolist()
        }
    source2.data = new_data2
    
gender.on_change('value', lambda attr, old, new: update())
slider_range.on_change('value', lambda attr, old, new: update())
y_axis.on_change('value', lambda attr, old, new: update()) 

layout1 = layout([
    [title],
    [subtitle],    
    [gender], 
    [slider_range],
    [y_axis],
    [sleep_efficiency_text],
    [p2, p1], 
    [age_group_text],
    [p, p3, p4]], sizing_mode='scale_width')

update()

#Other not filterd graphs
df_sleep_efficiency = pd.read_csv('Data/Sleep_Efficiency.csv')
df_categories = df_sleep_efficiency.copy()

features_list = ['Exercise frequency', 'Alcohol consumption', 'Caffeine consumption']
df_features = df_categories[features_list]

scaler = MinMaxScaler()
scaler.fit(df_features)
scaled_features = scaler.transform(df_features)

df_scaled = df_categories.copy()
df_scaled[features_list] = scaled_features

bins = [0.5, 0.59, 0.69, 0.79, 0.89, 1]
labels = ['0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']
df_scaled['sleep_efficiency_group'] = pd.cut(df_scaled['Sleep efficiency'], bins, labels = labels, include_lowest = True)

df_normal_categories = df_scaled.groupby('sleep_efficiency_group')[['Caffeine consumption', 'Alcohol consumption', 'Exercise frequency']].mean().reset_index()
sleep_efficiency_groups = ['0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']
categories = ['Caffeine consumption', 'Alcohol consumption', 'Exercise frequency']

data = {
    'x': df_normal_categories['sleep_efficiency_group'], 
    'Caffeine consumption' : round(df_normal_categories['Caffeine consumption'],2).tolist(),
    'Alcohol consumption': round(df_normal_categories['Alcohol consumption'],2).tolist(),
    'Exercise frequency': round(df_normal_categories['Exercise frequency'],2).tolist() 
}

x = [ (sleep_group, category) for sleep_group in sleep_efficiency_groups for category in categories]
counts = sum(zip(data['Caffeine consumption'], data['Alcohol consumption'], data['Exercise frequency']), ())
source5 = ColumnDataSource(data=dict(x=[], top=[], color=[]))

data_for_plot = {
    'x' : x, 
    'top' : counts,
    'color': 5*["#FADD69", "#F24300", "#4F76B2"] 
}
source5.data = data_for_plot

p5 = figure(x_range=FactorRange(*x), height=350, title="",
           toolbar_location=None, tools="")

p5.vbar(x = 'x', top = 'top', source = source5, width = 0.8, color='color')

p5.y_range.start = 0
p5.x_range.range_padding = 0.1
p5.xaxis.major_label_orientation = 1.57
p5.xgrid.grid_line_color = None

p5.xaxis.axis_label = "Sleep Efficiency"
p5.yaxis.axis_label = 'Scaled categories'
p5.title.text = "Sleep Efficiency VS " + 'Caffeine & Alcohol consumption and Exercise frequency'

df_sleep_categories = df_scaled.groupby('sleep_efficiency_group')[['REM sleep percentage', 'Deep sleep percentage', 'Light sleep percentage']].mean().reset_index()
sleep_efficiency_groups = ['0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']
sleep_categories = ['REM sleep percentage', 'Deep sleep percentage', 'Light sleep percentage']

data = {
    'x': df_sleep_categories['sleep_efficiency_group'], 
    'REM sleep percentage' : round(df_sleep_categories['REM sleep percentage'],2).tolist(),
    'Deep sleep percentage': round(df_sleep_categories['Deep sleep percentage'],2).tolist(),
    'Light sleep percentage': round(df_sleep_categories['Light sleep percentage'],2).tolist() 
}

x = [ (sleep_group, sleep_category) for sleep_group in sleep_efficiency_groups for sleep_category in sleep_categories]
counts = sum(zip(data['REM sleep percentage'], data['Deep sleep percentage'], data['Light sleep percentage']), ())
source6 = ColumnDataSource(data=dict(x=[], top=[], color=[]))

data_for_plot_1 = {
    'x' : x, 
    'top' : counts,
    'color': 5*["#FADD69", "#F24300", "#4F76B2"] 
}
source6.data = data_for_plot_1

p6 = figure(x_range=FactorRange(*x), height=350, title="",
           toolbar_location=None, tools="")

p6.vbar(x = 'x', top = 'top', source = source6, width = 0.8, color='color')

p6.y_range.start = 0
p6.x_range.range_padding = 0.1
p6.xaxis.major_label_orientation = 1.57
p6.xgrid.grid_line_color = None

p6.xaxis.axis_label = "Sleep Efficiency"
p6.yaxis.axis_label = 'Sleep categories'
p6.title.text = 'Sleep Efficiency VS REM sleep, deep sleep and light sleep percentage'

layout3 = layout([
    [p5], 
    [p6]], sizing_mode='scale_width')

axis_map_corr = {
    "Alcohol Consumption (in oz)": "Alcohol consumption",
    "Exercise Frequency (number of times per week)": "Exercise frequency", 
    "Age":"Age", 
    "Smoking Status": "Smoking status"}

dependent_variable = Div(text='<h3 style="text-align: center">The dependent variable of this project is Sleep Efficiency</h3>')
y_axis_corr = Select(title="Choose variable in order to calculate correlation with other variables: ", options=sorted(axis_map_corr.keys()), value= "Alcohol Consumption (in oz)", height=50)

source_corr_1 = ColumnDataSource(data=dict(x=[], y=[], y_predicted=[]))
p_corr_line_1 = figure(title="", sizing_mode="stretch_width")
p_corr_line_1.circle(x = "x", y= "y", source = source_corr_1, fill_alpha=0.2, size=10, color='#F24300')

source_corr_2 = ColumnDataSource(data=dict(x=[], y=[], y_predicted=[]))
p_corr_line_2 = figure(title="", sizing_mode="stretch_width")
p_corr_line_2.circle(x = "x", y= "y", source = source_corr_2, fill_alpha=0.2, size=10, color='#F24300')

source_corr_3 = ColumnDataSource(data=dict(x=[], y=[], y_predicted=[]))
p_corr_line_3 = figure(title="", sizing_mode="stretch_width")
p_corr_line_3.circle(x = "x", y= "y", source = source_corr_3, fill_alpha=0.2, size=10, color='#F24300')

source_corr_4 = ColumnDataSource(data=dict(x=[], y=[], y_predicted=[]))
p_corr_line_4 = figure(title="", sizing_mode="stretch_width")
p_corr_line_4.circle(x = "x", y= "y", source = source_corr_4, fill_alpha=0.2, size=10, color='#F24300')

def make_plot():
    y_name = axis_map_corr[y_axis_corr.value]

    new_data_corr1 = {
        'x': changed_df_sleep_efficiency["Age"], 
        'y': changed_df_sleep_efficiency[y_name]
    }
    source_corr_1.data = new_data_corr1

    p_corr_line_1.xaxis.axis_label = "Age"
    p_corr_line_1.yaxis.axis_label = y_axis.value
    p_corr_line_1.title.text = "Age VS " + y_name

    new_data_corr2 = {
        'x': changed_df_sleep_efficiency["Smoking status"], 
        'y': changed_df_sleep_efficiency[y_name]
    }
    source_corr_2.data = new_data_corr2

    p_corr_line_2.xaxis.axis_label = "Smoking Status"
    p_corr_line_2.yaxis.axis_label = y_axis.value
    p_corr_line_2.title.text = "Smoking Status VS " + y_name

    new_data_corr3 = {
        'x': changed_df_sleep_efficiency["Exercise frequency"], 
        'y': changed_df_sleep_efficiency[y_name]
    }
    source_corr_3.data = new_data_corr3

    p_corr_line_3.xaxis.axis_label = "Exercise Frequency"
    p_corr_line_3.yaxis.axis_label = y_axis.value
    p_corr_line_3.title.text = "Exercise Frequency VS " + y_name

    new_data_corr4 = {
        'x': changed_df_sleep_efficiency["Alcohol consumption"], 
        'y': changed_df_sleep_efficiency[y_name]
    }
    source_corr_4.data = new_data_corr4

    p_corr_line_4.xaxis.axis_label = "Alcohol Consumption"
    p_corr_line_4.yaxis.axis_label = y_axis.value
    p_corr_line_4.title.text = "Alcohol Consumption VS " + y_name

y_axis_corr.on_change('value', lambda attr, old, new: make_plot()) 

grid = gridplot([[p_corr_line_1, p_corr_line_2], [p_corr_line_3, p_corr_line_4]], toolbar_location=None)

make_plot()

layout2 = layout([
    [dependent_variable],
    [y_axis_corr], 
    [grid]], sizing_mode='scale_width')

tab1 = Panel(child=layout1, title='General information')
tab2 = Panel(child=layout3,title="Other not filtered graphs")
tab3 = Panel(child=layout2,title="Correlation between independent variables")
tabs = Tabs(tabs=[tab1, tab2, tab3])

curdoc().add_root(tabs)
curdoc().title = "Sleep Efficiency"
