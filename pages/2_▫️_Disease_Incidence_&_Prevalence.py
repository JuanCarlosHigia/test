import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import time
import base64
from st_pages import hide_pages, Page, Section, show_pages, add_page_title
st.set_page_config(page_title="HIGIA", layout = "wide")
if st.session_state.logged_in == False:
    st.switch_page("auth.py")
show_pages(
    [
        Page("auth.py", "Auth", "▫️"),
        Page("pages/1_▫️_Introduction.py", "Introduction", "▫️"),
        Page("pages/2_▫️_Disease_Incidence_&_Prevalence.py", "Disease Incidence & Prevalence", "▫️"),
        Page("pages/3_▫️_Disease_Risk_Prediction.py", "Disease Risk Prediction", "▫️"),
        Page("pages/4_▫️_Clinical_Workflow_Analysis.py", "Clinical Workflow Analysis", "▫️"),
        Page("pages/5_▫️_Hospital Risk Prevention.py", "Hospital Risk Prevention", "▫️"),
    ]
)
hide_pages(["Auth"])

col45, col46 = st.columns([7, 1])
with col45:
    st.markdown('# Disease Incidence & Prevalence')
with col46:
    st.image("flag_EUA.png", width=100)


COLORS = {
"CKD": "#0068C9",
"Diabetes":"#83C9FF" ,
"Dyslipidemia": "#FF2B2B" ,
"Heart Disease":"#FFABAB" ,
"Hypertension": "#29B09D" ,
"Nash": "#7DEFA1" ,
"Obesity":"#FF8700" 
}

#Logo
@st.cache_data()
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(
    png_file,
    background_position="50% 0%",  # Adjusted to move the image to the top
    margin_top="0%",  # Adjusted margin to move the image to the top
    image_width="50%",
    image_height="",
    separation="50px"  # Added separation between menu and logo
):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    margin-top: %s;
                    background-size: %s %s;
                    padding-top: %s;  # Added padding to create separation
                }
            </style>
            """ % (
        binary_string,
        background_position,
        margin_top,
        image_width,
        image_height,
        separation  # Apply the separation as padding
    )
def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )

add_logo("p1.png")

def to_quarter(month):
    if month <= 4:
        return 'Q1'
    elif month <= 8:
        return 'Q2'
    else:
        return 'Q3'

def get_biannual_range(year):
    if year % 2 == 0:
        return f"{year}-{year+1}"
    else:
        return f"{year-1}-{year}"
    
def transform_row(row):
    # Split the row by comma and space
    components = row.split(", ")
    # Map each component using the mapping dictionary
    mapped_components = [mapping.get(component, component) for component in components]
    # Join the mapped components back into a string
    return ", ".join(mapped_components)


new_nat = "Emirati"
factor = 12

#Read csv files
df_agg_diseases = pd.read_csv("DEFINITIVE_TABLES/DIS_NAT_GEN_AGE.csv")
df_agg_diseases["DISEASE"] = df_agg_diseases["DISEASE"].replace("Heart disease", "Heart Disease")
df_disease_temporal = pd.read_csv("DEFINITIVE_TABLES/MONTH_YEAR_MONTHYEAR_YEARQUARTER_BIANUAL_DISEASE_GEND_NAT_AGE_DETECTED.csv")
df_disease_temporal["DISEASE"] = df_disease_temporal["DISEASE"].replace("Heart disease", "Heart Disease")
df_combinations = pd.read_csv("DEFINITIVE_TABLES/COMBINATIONS.csv")
df_population = pd.read_csv("DEFINITIVE_TABLES/POPULATION_EUA.csv")
df_count_groups = pd.read_csv("DEFINITIVE_TABLES/COUNTS_GROUPS.csv")
#Adapt code
df_agg_diseases["COUNTS"] = df_agg_diseases["COUNTS"] * factor
df_disease_temporal.rename(columns={'Detected Cases': 'Count'}, inplace=True)
df_disease_temporal["Count"] = df_disease_temporal["Count"] * factor
df_combinations["COUNTS"] = df_combinations["COUNTS"] * factor
df_count_groups["COUNTS"] = df_count_groups["COUNTS"] * factor
df_disease_temporal = df_disease_temporal[~df_disease_temporal['Year'].isin([2006, 2007, 2008])]
df_disease_temporal['Year'] = df_disease_temporal['Year'].apply(lambda x: x + 2)

df_agg_diseases["NATIONALITY"] = df_agg_diseases["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_disease_temporal["NATIONALITY"] = df_disease_temporal["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_combinations["NATIONALITY"] = df_combinations["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_count_groups["NATIONALITY"] = df_count_groups["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
#Age_group NON DYNAMIC plot
df_age_groups = df_agg_diseases

#Set options of selectors
nationalities = sorted(list(set(df_agg_diseases["NATIONALITY"].values)))
nationalities.insert(0, "All Nationalities")

genders = sorted(list(set(df_agg_diseases["GENDER"].values)))
genders.insert(0, "All Genders")

ages_groups = sorted(list(set(df_agg_diseases["AGE_GROUP"].values)))
ages_groups.insert(0, "All Ages")

diseases = sorted(list(set(df_agg_diseases["DISEASE"].values)))
diseases.insert(0, "All Diseases")

mapping = {"Heart disease":"CVD", "Nash":"NASH", "Diabetes":"DT2", "Dyslipidemia":"DYS", "Obesity":"OBE", "Hypertension":"HYP", "CKD":"CKD"}
#Selectors
Nationality = st.sidebar.selectbox("Nationality:", nationalities)
Gender = st.sidebar.selectbox("Gender:", genders)
Age_group = st.sidebar.selectbox("Age:", ages_groups)
Num_combined = st.sidebar.selectbox("Number of diseases:", ["2", "3", "+3"])

#Filtering 
filtered_dataframes = {
    'df_agg_diseases': df_agg_diseases,
    'df_disease_temporal': df_disease_temporal,
    'df_age_groups': df_age_groups,
    'df_combinations': df_combinations,
    'df_count_groups': df_count_groups  # Added df_count_groups to the filtering process
}

# Apply filters based on the sidebar selections
for key in filtered_dataframes:
    if Nationality != "All Nationalities":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["NATIONALITY"] == Nationality]
    if Gender != "All Genders":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["GENDER"] == Gender]
    if Age_group != "All Ages" and key != 'df_age_groups':  # df_age_groups is excluded from age filtering
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["AGE_GROUP"] == Age_group]

# Update the original dataframes after filtering
df_agg_diseases, df_disease_temporal, df_age_groups, df_combinations, df_count_groups = (
    filtered_dataframes['df_agg_diseases'],
    filtered_dataframes['df_disease_temporal'],
    filtered_dataframes['df_age_groups'],
    filtered_dataframes['df_combinations'],
    filtered_dataframes['df_count_groups']  # Updated to include df_count_groups
)

# Define group columns for aggregation
group_columns = {
    'df_agg_diseases': ["NATIONALITY", "GENDER", "DISEASE", "AGE_GROUP"],
    'df_disease_temporal': ["MONTH", "Year", "NATIONALITY", "GENDER", "DISEASE", "AGE_GROUP"],
    'df_age_groups': ["NATIONALITY", "GENDER", "DISEASE", "AGE_GROUP"],
    'df_combinations': ["NATIONALITY", "GENDER", "COMBINED_DIAGS", "AGE_GROUP"],
    'df_count_groups': ["NATIONALITY", "GENDER", "AGE_GROUP"]  # Added group columns for df_count_groups
}


# Remove unnecessary columns and group by the remaining columns if the selection is 'All'
for key in group_columns:
    if Nationality == "All Nationalities":
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["NATIONALITY"])
        group_columns[key].remove("NATIONALITY")
    if Gender == "All Genders":
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["GENDER"])
        group_columns[key].remove("GENDER")
    if Age_group == "All Ages" and key != 'df_age_groups':
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["AGE_GROUP"])
        group_columns[key].remove("AGE_GROUP")
    # Group by the remaining columns and sum the counts
    if group_columns[key]:
        if 'COUNTS' in filtered_dataframes[key].columns:
            filtered_dataframes[key] = filtered_dataframes[key].groupby(group_columns[key]).agg({'COUNTS': 'sum'}).reset_index()
        if 'Count' in filtered_dataframes[key].columns:
            filtered_dataframes[key] = filtered_dataframes[key].groupby(group_columns[key]).agg({'Count': 'sum'}).reset_index()

# Update the original dataframes after grouping
df_agg_diseases, df_disease_temporal, df_age_groups, df_combinations, df_count_groups = (
    filtered_dataframes['df_agg_diseases'],
    filtered_dataframes['df_disease_temporal'],
    filtered_dataframes['df_age_groups'],
    filtered_dataframes['df_combinations'],
    filtered_dataframes['df_count_groups']  # Updated to include df_count_groups
)
total_count_CASE = int(df_count_groups["COUNTS"].sum())
df_agg_diseases['PERCENTAGE'] = round((df_agg_diseases['COUNTS'] / total_count_CASE), 4)

df_disease_temporal = df_disease_temporal.sort_values(by=['DISEASE', 'Year', 'MONTH'])
df_disease_temporal['Sum'] = df_disease_temporal.groupby(['DISEASE'])['Count'].cumsum()
df_disease_temporal['MONTH_YEAR'] = pd.to_datetime(df_disease_temporal['Year'].astype(str) + '-' + df_disease_temporal['MONTH'].astype(str))
df_disease_temporal['Year-Quarter'] = df_disease_temporal['MONTH_YEAR'].dt.year.astype(str) + ' ' + df_disease_temporal['MONTH_YEAR'].dt.month.apply(to_quarter)
df_disease_temporal['Bianual'] = df_disease_temporal['Year'].apply(get_biannual_range)

df_combinations = df_combinations.sort_values(by="COUNTS", ascending=False)
df_combinations["NUM_DIAGS"] = df_combinations["COMBINED_DIAGS"].apply(lambda x : 0 if x == "No diags" else len(x.split(",")))
df_combinations["NUM_DIAGS"] = df_combinations["NUM_DIAGS"].apply(lambda x : str(x) if x <= 3 else "+3")
df_combinations = df_combinations[df_combinations["NUM_DIAGS"] == Num_combined]
total_count = df_combinations['COUNTS'].sum()
df_combinations['PERCENTAGE'] = round((df_combinations['COUNTS'] / total_count), 4)
df_combinations["COMBINED_DIAGS_CODES"] = df_combinations["COMBINED_DIAGS"].apply(transform_row)

columns = ["Count", "Sum"]
c2 = ["Year", "Year-Quarter", "Bianual"]

#Pie chart plot
s = 50
op = 0.05
f=12
h = 300
w= 500
colors = ["#F8D800", "#0396FF", "#EA5455", "#7367F0", "#32CCBC", "#28C76F", "#9F44D3", "#DE4313", "#3CD500", "#FA742B", "#C32BAC", "#00E4FF"]

selector = alt.selection_point(
    fields=['DISEASE'],
    value=None
)

base = alt.Chart(df_agg_diseases).encode(
 theta = alt.Theta("sum(COUNTS)", stack = True), color = alt.Color("DISEASE:N", title = "Diseases", scale=alt.Scale(domain=list(COLORS.keys()), range=list(COLORS.values()))), 
 opacity = alt.condition(selector, alt.value(1), alt.value(0.3)),
 tooltip=[
        alt.Tooltip('DISEASE:N', title='Disease:'),
        alt.Tooltip('sum(COUNTS):N', title='Number of cases:', format=',')
    ])

pie = base.mark_arc(outerRadius = 150, innerRadius = 50).add_params(selector)
text = base.mark_text(radius=185, size=15, fontWeight='bold').encode(text=alt.Text("PERCENTAGE:Q", format=".0%"))

pie_diseases = (pie + text).properties(title = alt.TitleParams("Total Cases per Disease in 2023", anchor='middle', frame='bounds'))
#Age group bars
diseases_age_group = alt.Chart(df_age_groups).mark_bar(innerRadius=10).encode(
            x = alt.X("DISEASE:N", title = "", axis=alt.Axis(labelAngle=90)),
            y = alt.Y("sum(COUNTS):Q", title="Number of cases"),
            color=alt.Color("DISEASE", scale=alt.Scale(domain=list(COLORS.keys()), range=list(COLORS.values()))),
            facet=alt.Facet("AGE_GROUP:N", columns=8, title="")
        ).transform_filter(selector).properties(width=150, height=400, title=alt.TitleParams("Case Distribution by Age Group 2011 - 2023", anchor='middle', frame='bounds'))
#Temporal view
option1 = st.sidebar.selectbox('Count Method:', columns, index = 1)
option2 = st.sidebar.selectbox("Time Filter: ", c2)
points_counts = alt.Chart(df_disease_temporal).transform_fold(
        columns,
        as_=["Aggregation of number of cases", 'value']
    ).transform_filter(
        (alt.datum['Aggregation of number of cases'] == option1) & (alt.datum['Aggregation of number of cases'] == columns[0])
    ).transform_fold(
        c2,
        as_=['Temporal aggregation', 'value2']
    ).transform_filter(
        (alt.datum['Temporal aggregation'] == option2)
    ).transform_aggregate(
        sum_value='sum(value)',
        groupby=['value2', 'DISEASE']
    ).mark_point(filled=True, size=s).encode(
        x=alt.X('value2:N', axis=alt.Axis(labelAngle=0), title=""),
        y=alt.Y('sum_value:Q', title="Number of Cases"),
        color=alt.Color('DISEASE:N', title="Diseases", legend = None, scale=alt.Scale(domain=list(COLORS.keys()), range=list(COLORS.values()))),
        tooltip=[
            alt.Tooltip('value2:N', title='Time:'),
            alt.Tooltip('DISEASE:N', title='Disease:'),
            alt.Tooltip('sum_value:Q', title='Total cases:', format=',')
        ],
        opacity=alt.condition(selector, alt.value(1), alt.value(op))
    )

points_cumulative = alt.Chart(df_disease_temporal).transform_fold(
        columns,
        as_=["Aggregation of number of cases", 'value']
    ).transform_filter(
        (alt.datum['Aggregation of number of cases'] == option1) & (alt.datum['Aggregation of number of cases'] == columns[1])
    ).transform_fold(
        c2,
        as_=['Temporal aggregation', 'value2']
    ).transform_filter(
        (alt.datum['Temporal aggregation'] == option2)
    ).transform_aggregate(
        max_value='max(value)',
        groupby=['value2', 'DISEASE']
    ).mark_point(filled=True, size=s).encode(
        x=alt.X('value2:N', axis=alt.Axis(labelAngle=0), title=""),
        y=alt.Y('max_value:Q', title="Number of Cases"),
        color=alt.Color('DISEASE:N', title="Diseases", legend = None, scale=alt.Scale(domain=list(COLORS.keys()), range=list(COLORS.values()))),
        tooltip=[
            alt.Tooltip('value2:N', title='Time:'),
            alt.Tooltip('DISEASE:N', title='Disease:'),
            alt.Tooltip('max_value:Q', title='Total cases:', format=',')
        ],
        opacity=alt.condition(selector, alt.value(1), alt.value(op))
    )

lines_counts = alt.Chart(df_disease_temporal).transform_fold(
        columns,
        as_=["Aggregation of number of cases", 'value']
    ).transform_filter(
        (alt.datum['Aggregation of number of cases'] == option1) & (alt.datum['Aggregation of number of cases'] == columns[0])
    ).transform_fold(
        c2,
        as_=['Temporal aggregation', 'value2']
    ).transform_filter(
        (alt.datum['Temporal aggregation'] == option2)
    ).transform_aggregate(
        sum_value='sum(value)',
        groupby=['value2', 'DISEASE']
    ).mark_line().encode(
        x=alt.X('value2:N', axis=alt.Axis(labelAngle=0), title=""),
        y=alt.Y('sum_value:Q', title="Number of Cases"),
        color=alt.Color('DISEASE:N', title="Diseases", legend = None, scale=alt.Scale(domain=list(COLORS.keys()), range=list(COLORS.values()))),
        tooltip=[
            alt.Tooltip('value2:N', title='Time:'),
            alt.Tooltip('DISEASE:N', title='Disease:'),
            alt.Tooltip('sum_value:Q', title='Total cases:', format=',')
        ],
        opacity=alt.condition(selector, alt.value(1), alt.value(op))
    ).add_selection(
        selector
    ).transform_filter(
        selector
    )

lines_cumulative = alt.Chart(df_disease_temporal).transform_fold(
        columns,
        as_=["Aggregation of number of cases", 'value']
    ).transform_filter(
        (alt.datum['Aggregation of number of cases'] == option1) & (alt.datum['Aggregation of number of cases'] == columns[1])
    ).transform_fold(
        c2,
        as_=['Temporal aggregation', 'value2']
    ).transform_filter(
        (alt.datum['Temporal aggregation'] == option2)
    ).transform_aggregate(
        max_value='max(value)',
        groupby=['value2', 'DISEASE']
    ).mark_line().encode(
        x=alt.X('value2:N', axis=alt.Axis(labelAngle=0), title=""),
        y=alt.Y('max_value:Q', title="Number of Cases"),
        color=alt.Color('DISEASE:N', title="Diseases", legend = None, scale=alt.Scale(domain=list(COLORS.keys()), range=list(COLORS.values()))),
        tooltip=[
            alt.Tooltip('value2:N', title='Time:'),
            alt.Tooltip('DISEASE:N', title='Disease:'),
            alt.Tooltip('max_value:Q', title='Total cases:', format=',')
        ],
        opacity=alt.condition(selector, alt.value(1), alt.value(op))
    ).add_selection(
        selector
    ).transform_filter(
        selector
    )

points_chart = alt.layer(points_counts, points_cumulative).properties(width=1170, height=400)
lines_chart = alt.layer(lines_counts, lines_cumulative).properties(width=1170, height=400)
combined_chart = (lines_chart + points_chart).properties(title=alt.TitleParams("Evolution of Total Cases per Disease", anchor='middle', frame='bounds'))

# Population plot
chart = alt.Chart(df_population).mark_line(color='brown').encode(
    x=alt.X('Year:N', axis=alt.Axis(labelAngle=0), title=""),
    y=alt.Y('Population:Q', axis=alt.Axis(title=''))
)
point_chart = alt.Chart(df_population).mark_point(filled=True, color='brown').encode(
    x=alt.X('Year:N', axis=alt.Axis(title='')),
    y=alt.Y('Population:Q', axis=alt.Axis(title=''))
)
chart = chart.encode(
    tooltip=[
        alt.Tooltip('Year:N', title='Year:'),
        alt.Tooltip('Population:Q', title='Population:', format=',')
    ]
)
point_chart = point_chart.encode(
    tooltip=[
        alt.Tooltip('Year:N', title='Year:'),
        alt.Tooltip('Population:Q', title='Population:', format=',')
    ]
)
population_plot = (chart + point_chart).properties(
    title=alt.TitleParams("Population Growth", anchor='middle', frame='bounds'), width=1170, height=200
)

#Combinations df
palette = ["#3c9a8e", "#4ea69f", "#6eb9b3", "#8bcbc5", "#a9dada"]

base_com = alt.Chart(df_combinations.head(5)).encode(
    alt.Theta("COUNTS:Q").stack(True),
    alt.Color('COMBINED_DIAGS_CODES', sort=None, scale = alt.Scale(range = palette), title = "Clusters"),
    tooltip = [
        alt.Tooltip("COMBINED_DIAGS", title="Clusters"),
        alt.Tooltip("COUNTS", title="Counts", format=',')
    ]
)

pie_com = base_com.mark_arc(outerRadius = 150, innerRadius = 50)
text_com = base_com.mark_text(radius=185, size=15, fontWeight='bold').encode(text=alt.Text("PERCENTAGE:Q", format=".0%"))

combinations = (pie_com + text_com).properties(title = alt.TitleParams("Dominant Comorbidity Clusters", anchor='middle', frame='bounds'))
part1 = (((pie_diseases | combinations).resolve_scale(color="independent") & combined_chart & population_plot & diseases_age_group)).configure(
    concat=alt.CompositionConfig(spacing=75)
)
part1
st.button("Export Data", type="primary")

if st.sidebar.button("Log out"):
    st.session_state.logged_in == False
    st.switch_page("auth.py")