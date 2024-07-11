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

np.random.seed(42)

COLORS = {
"All Diseases":"#2D7A6E",
"CKD": "#0068C9",
"Diabetes":"#83C9FF" ,
"Dyslipidemia": "#FF2B2B" ,
"Heart Disease":"#FFABAB" ,
"Hypertension": "#29B09D" ,
"Nash": "#7DEFA1" ,
"Obesity":"#FF8700" 
}

SOFT_COLORS = {'All Diseases': '#96bcb6',
 'CKD': '#7fb3e4',
 'Diabetes': '#c1e4ff',
 'Dyslipidemia': '#ff9595',
 'Heart Disease': '#ffd5d5',
 'Hypertension': '#94d7ce',
 'Nash': '#bef7d0',
 'Obesity': '#ffc37f'}


col1, col7 = st.columns([6, 1])
with col1:
    st.markdown('# Disease Risk Prediction')
with col7:
    st.image("flag_EUA.png", width=100)

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
    if int(year) % 2 == 0:
        return f"{int(year)}-{int(year)+1}"
    else:
        return f"{int(year)-1}-{int(year)}"

new_nat = "Emirati"
factor = 12

#Read csv files
df_agg_diseases = pd.read_csv("DEFINITIVE_TABLES/DIS_NAT_GEN_AGE.csv")
df_diagnosed_risk = pd.read_csv("DEFINITIVE_TABLES/DIAGNOSED_ATRISK.csv")
df_ratios = pd.read_csv("DEFINITIVE_TABLES/DISEASES_RATIOS.csv")
df_disease_temporal = pd.read_csv("DEFINITIVE_TABLES/MONTH_YEAR_MONTHYEAR_YEARQUARTER_BIANUAL_DISEASE_GEND_NAT_AGE_DETECTED.csv")

# Adapt code
df_agg_diseases['DISEASE'] = df_agg_diseases['DISEASE'].replace('Heart disease', 'Heart Disease')
df_diagnosed_risk['DISEASE'] = df_diagnosed_risk['DISEASE'].replace('Heart disease', 'Heart Disease')
df_ratios['DISEASE'] = df_ratios['DISEASE'].replace('Heart disease', 'Heart Disease')
df_disease_temporal['DISEASE'] = df_disease_temporal['DISEASE'].replace('Heart disease', 'Heart Disease')
df_diagnosed_risk["Diagnosed"] = df_diagnosed_risk["Diagnosed"] * factor
df_diagnosed_risk["At Risk"] = df_diagnosed_risk["At Risk"] * factor
df_disease_temporal.rename(columns={'Detected Cases': 'Count'}, inplace=True)
df_disease_temporal["Count"] = df_disease_temporal["Count"] * factor
df_disease_temporal = df_disease_temporal[~df_disease_temporal['Year'].isin([2006, 2007, 2008])]
df_disease_temporal['Year'] = df_disease_temporal['Year'].apply(lambda x: str(x + 2))


df_diagnosed_risk["NATIONALITY"] = df_diagnosed_risk["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_disease_temporal["NATIONALITY"] = df_disease_temporal["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_agg_diseases["NATIONALITY"] = df_agg_diseases["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
#Set options of selectors
nationalities = sorted(list(set(df_agg_diseases["NATIONALITY"].values)))
nationalities.insert(0, "All Nationalities")

genders = sorted(list(set(df_agg_diseases["GENDER"].values)))
genders.insert(0, "All Genders")

ages_groups = sorted(list(set(df_agg_diseases["AGE_GROUP"].values)))
ages_groups.insert(0, "All Ages")

diseases = sorted(list(set(df_agg_diseases["DISEASE"].values)))
diseases.insert(0, "All Diseases")

#Selectors
Nationality = st.sidebar.selectbox("Nationality:", nationalities)
Gender = st.sidebar.selectbox("Gender:", genders)
Age_group = st.sidebar.selectbox("Age:", ages_groups)
Disease = st.sidebar.selectbox("Disease:", diseases)

reshaped_df = df_diagnosed_risk.melt(id_vars=['DISEASE', 'GENDER', 'NATIONALITY', 'AGE_GROUP'], value_vars=['Diagnosed', 'At Risk'], var_name='CATEGORY', value_name='VALUE')
result_df = pd.merge(reshaped_df, df_diagnosed_risk[['DISEASE', 'GENDER', 'NATIONALITY', 'AGE_GROUP']],
                     on=['DISEASE', 'GENDER', 'NATIONALITY', 'AGE_GROUP'], 
                     how='inner')
df_diagnosed_risk = result_df

#Filtering 
filtered_dataframes = {
    'df_diagnosed_risk': df_diagnosed_risk,
    'df_disease_temporal': df_disease_temporal,

}

# Apply filters based on the sidebar selections
for key in filtered_dataframes:
    if Nationality != "All Nationalities":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["NATIONALITY"] == Nationality]
    if Gender != "All Genders":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["GENDER"] == Gender]
    if Age_group != "All Ages":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["AGE_GROUP"] == Age_group]

# Update the original dataframes after filtering
df_diagnosed_risk, df_disease_temporal = (
    filtered_dataframes['df_diagnosed_risk'], 
    filtered_dataframes['df_disease_temporal']
)

# Define group columns for aggregation
group_columns = {
    'df_diagnosed_risk': ["NATIONALITY", "GENDER", "DISEASE", "AGE_GROUP"],  # Added group columns for df_diagnosed_risk
    'df_disease_temporal': ["MONTH", "Year", "NATIONALITY", "GENDER", "DISEASE", "AGE_GROUP"],

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
        if 'Diagnosed' in filtered_dataframes[key].columns or 'At Risk' in filtered_dataframes[key].columns:
            filtered_dataframes[key] = filtered_dataframes[key].groupby(group_columns[key]).agg({'Diagnosed': 'sum', 'At Risk': 'sum'}).reset_index()

# Update the original dataframes after grouping
df_diagnosed_risk, df_disease_temporal = (
    filtered_dataframes['df_diagnosed_risk'],
    filtered_dataframes['df_disease_temporal']
)

category_mapping = {
"Diagnosed": 1,
"At Risk" : 2
}

df_disease_temporal = pd.merge(df_disease_temporal, df_ratios, on='DISEASE', how='left')
df_disease_temporal['MONTH_YEAR'] = pd.to_datetime(df_disease_temporal['Year'].astype(str) + '-' + df_disease_temporal['MONTH'].astype(str))
df_disease_temporal['Year-Quarter'] = df_disease_temporal['MONTH_YEAR'].dt.year.astype(str) + ' ' + df_disease_temporal['MONTH_YEAR'].dt.month.apply(to_quarter)
df_disease_temporal['Bianual'] = df_disease_temporal['Year'].apply(get_biannual_range)

#Total case
df_total_cases_temporal = df_disease_temporal
df_total_cases_temporal['Predicted Cases'] = df_total_cases_temporal['Count'] + (df_total_cases_temporal['Count'] * df_disease_temporal['RISK_TO_DIAGNOSED_RATIO'] + np.random.randint(0, 100, df_total_cases_temporal.shape[0])).astype(int)
df_total_cases_temporal = df_total_cases_temporal.drop(columns=['DISEASE', 'RISK_TO_DIAGNOSED_RATIO', 'MONTH_YEAR', 'Year-Quarter', 'Bianual'], axis=1)
df_total_cases_temporal = df_total_cases_temporal.groupby(['MONTH', 'Year']).agg({'Count': 'sum', 'Predicted Cases': 'sum'}).reset_index()
df_total_cases_temporal = df_total_cases_temporal.sort_values(by=['Year', 'MONTH'])

# Initialize 'Count' and 'Predicted Cases' with zeros for future data
years_of_interest = ["2012", "2013", "2014", "2015", "2016"]
new_vals = df_total_cases_temporal[df_total_cases_temporal['Year'].isin(years_of_interest)]
new_vals = new_vals[new_vals['Year'] != "2023"]
new_vals['Year'] = new_vals['Year'].replace({"2012": "2023", "2013": "2024", "2014": "2025", "2015": "2026", "2016": "2027"})
new_vals['Count'] += np.random.randint(0, 100, size=new_vals.shape[0])
new_vals['Predicted Cases'] += np.random.randint(0, 100, size=new_vals.shape[0])

df_total_cases_temporal = pd.concat([df_total_cases_temporal, new_vals], ignore_index=True)
df_total_cases_temporal['Sum'] = df_total_cases_temporal['Count'].cumsum()
df_total_cases_temporal['Acumulated Predicted Cases'] = df_total_cases_temporal['Predicted Cases'].cumsum()
df_total_cases_temporal['MONTH_YEAR'] = pd.to_datetime(df_total_cases_temporal['Year'].astype(str) + '-' + df_total_cases_temporal['MONTH'].astype(str))
df_total_cases_temporal['Year-Quarter'] = df_total_cases_temporal['MONTH_YEAR'].dt.year.astype(str) + ' ' + df_total_cases_temporal['MONTH_YEAR'].dt.month.apply(to_quarter)
df_total_cases_temporal['Bianual'] = df_total_cases_temporal['Year'].apply(get_biannual_range)
df_total_cases_temporal.drop(columns = ["MONTH_YEAR"], inplace=True)
df_total_area_diseases = df_total_cases_temporal
#Per disease
df_diseases_cases_temporal = df_disease_temporal[df_disease_temporal['DISEASE'] == Disease]
df_diseases_cases_temporal['Predicted Cases'] = df_diseases_cases_temporal['Count'] + (df_diseases_cases_temporal['Count'] * df_diseases_cases_temporal['RISK_TO_DIAGNOSED_RATIO'] + np.random.randint(0, 100, df_diseases_cases_temporal.shape[0])).astype(int)
df_diseases_cases_temporal = df_diseases_cases_temporal.drop(columns=['RISK_TO_DIAGNOSED_RATIO', 'MONTH_YEAR', 'Year-Quarter', 'Bianual'], axis=1)
df_diseases_cases_temporal = df_diseases_cases_temporal.sort_values(by=['DISEASE', 'Year', 'MONTH'])

years_of_interest = ["2012", "2013", "2014", "2015", "2016"]
new_vals = df_diseases_cases_temporal[df_diseases_cases_temporal['Year'].isin(years_of_interest)]
new_vals = new_vals[new_vals['Year'] != "2023"]
new_vals['Year'] = new_vals['Year'].replace({"2012": "2023", "2013": "2024", "2014": "2025", "2015": "2026", "2016": "2027"})
new_vals['Count'] += np.random.randint(0, 100, size=new_vals.shape[0])
new_vals['Predicted Cases'] += np.random.randint(0, 100, size=new_vals.shape[0])
df_diseases_cases_temporal = pd.concat([df_diseases_cases_temporal, new_vals], ignore_index=True)

df_diseases_cases_temporal['Sum'] = df_diseases_cases_temporal.groupby(['DISEASE'])['Count'].cumsum()
df_diseases_cases_temporal['Acumulated Predicted Cases'] = df_diseases_cases_temporal.groupby(['DISEASE'])['Predicted Cases'].cumsum()
df_diseases_cases_temporal['MONTH_YEAR'] = pd.to_datetime(df_diseases_cases_temporal['Year'].astype(str) + '-' + df_diseases_cases_temporal['MONTH'].astype(str))
df_diseases_cases_temporal['Year-Quarter'] = df_diseases_cases_temporal['MONTH_YEAR'].dt.year.astype(str) + ' ' + df_diseases_cases_temporal['MONTH_YEAR'].dt.month.apply(to_quarter)
df_diseases_cases_temporal['Bianual'] = df_diseases_cases_temporal['Year'].apply(get_biannual_range)
df_diseases_cases_temporal.drop(columns = ["MONTH_YEAR"], inplace=True)
df_area_individual_diseases = df_diseases_cases_temporal


columns_to_remove = ['NATIONALITY', 'GENDER', 'AGE_GROUP']
for column in columns_to_remove:
    if column in df_diagnosed_risk.columns:
        df_diagnosed_risk = df_diagnosed_risk.drop(column, axis=1)
df_diagnosed_risk = df_diagnosed_risk.groupby(['CATEGORY', 'DISEASE']).agg({'VALUE': 'sum'}).reset_index()

df_diagnosed_risk['RANK'] = df_diagnosed_risk['CATEGORY'].map(category_mapping)
risk_df = df_diagnosed_risk[df_diagnosed_risk['CATEGORY'] == 'At Risk']
diagnosed_df = df_diagnosed_risk[df_diagnosed_risk['CATEGORY'] == 'Diagnosed']
risk_grouped = risk_df.groupby('DISEASE')['VALUE'].sum().reset_index()
diagnosed_grouped = diagnosed_df.groupby('DISEASE')['VALUE'].sum().reset_index()
merged_df = pd.merge(risk_grouped, diagnosed_grouped, on='DISEASE', suffixes=('_Risk', '_Diagnosed'))
merged_df['RISK_TO_DIAGNOSED_RATIO'] = merged_df['VALUE_Risk'] / merged_df['VALUE_Diagnosed']
merged_df['POSITION'] = (merged_df['VALUE_Diagnosed'] + merged_df['VALUE_Risk'] / 2)
merged_df = merged_df[["DISEASE", "POSITION", "RISK_TO_DIAGNOSED_RATIO"]]
df_diagnosed_risk = pd.merge(merged_df, df_diagnosed_risk, on='DISEASE', how='inner')
df_diagnosed_risk = df_diagnosed_risk[["DISEASE", "CATEGORY", "RANK", "POSITION", "VALUE", "RISK_TO_DIAGNOSED_RATIO"]]

#Risk Bar Plot
h = 300
w = 500
order3 = ["Diagnosed", "At Risk"]
blue = "#0557b5"
red = "#C1121F"
palette3 = [blue, red]

transf_risks = alt.Chart(df_diagnosed_risk)
bar_risks = transf_risks.mark_bar(filled=True, size=70).encode(
x=alt.X('DISEASE:N', title=" ", axis=alt.Axis(labelAngle=0, labelFontSize=16)),
y=alt.Y('VALUE:Q', title="Case Count"),
color=alt.Color("CATEGORY:N", title=" ", sort=order3, scale=alt.Scale(range=palette3), legend=alt.Legend(orient='none', legendX=950, legendY=-65, direction='horizontal')),
order=alt.Order('RANK:N'),
tooltip=[alt.Tooltip('DISEASE:N', title='Disease:'),
alt.Tooltip('CATEGORY:N', title='Status:'),
alt.Tooltip("VALUE:Q", title = "Number of Cases:", format=',')])

text_risks = transf_risks.transform_filter(alt.datum.CATEGORY != "Diagnosed").mark_text(align='center',
baseline='middle', color = 'white', fontWeight = "bold", size = 18).encode(x=alt.X('DISEASE:N', title='', axis=alt.Axis(labelAngle=0)).stack('zero'),
y=alt.Y('POSITION:Q'), text = alt.Text('RISK_TO_DIAGNOSED_RATIO', format=".0%"), tooltip=alt.value(None))

stacked_bar_diseases_RISKS = (bar_risks + text_risks).properties(title="Diagnosed Population vs At Risk Population", width = 200, height = 650).configure_legend(symbolType='circle')
stacked_bar_diseases_RISKS = stacked_bar_diseases_RISKS.configure_title(anchor = "middle")

#Temporal views diagnostic
s = 50
op = 0.05
f=12
h = 300
w= 500
colors = ["#F8D800", "#0396FF"]

columns = ["Count", "Sum"]
c2 = ["Year", "Year-Quarter", "Bianual"]
columns2 = ["Predicted Cases", "Acumulated Predicted Cases"]
option1 = st.sidebar.selectbox('Count Method:', columns, index = 1)
option2 = st.sidebar.selectbox("Time Filter: ", c2)
option3 = ""
if option1 == columns[0]:
    option3 = columns2[0]
else:
    option3 = columns2[1]

if Disease == "All Diseases":
    area_df = df_total_area_diseases
else:
    area_df = df_area_individual_diseases
    area_df.drop(columns=["DISEASE"], inplace=True)

area_df = area_df.drop(columns=["MONTH"])

if option1 == "Count":
    area_df.drop(columns=["Sum", "Acumulated Predicted Cases"], inplace=True)
elif option1 == "Sum":
    area_df.drop(columns=["Count", "Predicted Cases"], inplace=True)
if option2 == "Year":
    area_df.drop(columns=["Year-Quarter", "Bianual"], inplace=True)
elif option2 == "Year-Quarter":
    area_df.drop(columns=["Year", "Bianual"], inplace=True)
elif option2 == "Bianual":
    area_df.drop(columns=["Year", "Year-Quarter"], inplace=True)

if option1 == "Count":
    area_df = area_df.groupby([option2]).agg({
            'Count': 'sum',
            'Predicted Cases': 'sum'
        }).reset_index()
elif option1 == "Sum":
    area_df = area_df.groupby([option2]).agg({
            'Sum': 'max',
            'Acumulated Predicted Cases': 'max'
        }).reset_index()

area_df.columns = ["TEMPORAL", "CASES", "AI"]
# Filter rows where 'TEMPORAL' contains any of the years 2024, 2025, 2026, or 2027
area_df_new_predictions = area_df[area_df['TEMPORAL'].str.contains('2024|2025|2026|2027')]
area_df = area_df[~area_df['TEMPORAL'].str.contains('2025|2026|2027')]

area_chart_total = alt.Chart(area_df).mark_area(
    color=SOFT_COLORS[Disease]
    ).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('CASES:Q'),
    y2=alt.Y2('AI:Q'),
    tooltip=alt.value(None)
).properties(
    width=w,
    height=h
)

area_chart_total_new_predictions = alt.Chart(area_df_new_predictions).mark_area(
    color=alt.Gradient(
        gradient='linear',
        stops=[alt.GradientStop(color='#991f17', offset=0),
               alt.GradientStop(color='#991f17', offset=1)],
        x1=1, x2=1, y1=1, y2=0
    )
).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('CASES:Q'),
    y2=alt.Y2('AI:Q'),
    tooltip=alt.value(None)).properties(
    width=w,
    height=h
)

# New area chart from 0 to CASES:Q with a different color
area_chart_base_to_cases = alt.Chart(area_df).mark_area(
    color=alt.Gradient(
        gradient='linear',
        stops=[alt.GradientStop(color='#cbd6e4', offset=0),
               alt.GradientStop(color='#cbd6e4', offset=1)],
        x1=1, x2=1, y1=1, y2=0
    )
).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('CASES:Q'),
    tooltip=alt.value(None)
).properties(
    width=w,
    height=h
)

area_chart_base_to_cases_predicted = alt.Chart(area_df_new_predictions).mark_area(
    color=alt.Gradient(
        gradient='linear',
        stops=[alt.GradientStop(color='#c86558', offset=0),
               alt.GradientStop(color='#c86558', offset=1)],
        x1=1, x2=1, y1=1, y2=0
    )
).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('CASES:Q'),
    tooltip=alt.value(None)).properties(
    width=w,
    height=h
)

# Combine all area charts into one and fill the area between them with different colors based on the year
combined_area_chart = alt.layer(
    area_chart_total,
    area_chart_total_new_predictions,
    area_chart_base_to_cases,
    area_chart_base_to_cases_predicted,
).resolve_scale(
    x='shared',
    y='shared'
)

# Create combined line and point charts for AI predictions
combined_top_line = alt.Chart(pd.concat([area_df, area_df_new_predictions])).mark_line(
    color=COLORS[Disease],
    size=5
).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y='AI:Q'
)

combined_top_points = alt.Chart(pd.concat([area_df, area_df_new_predictions])).mark_point(
    filled=True,
    color=COLORS[Disease],
    size=95
).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y='AI:Q',
    tooltip=[alt.Tooltip('AI:Q', title="AI Prediction:", format=','),
             alt.Tooltip('TEMPORAL:N', title="Time:")]
)

# Create combined line and point charts for Medical Diagnostic
combined_bottom_line = alt.Chart(pd.concat([area_df, area_df_new_predictions])).mark_line(
    color='black',
    size=5
).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y='CASES:Q'
)

combined_bottom_points = alt.Chart(pd.concat([area_df, area_df_new_predictions])).mark_point(
    filled=True,
    color='black',
    size=95
).encode(
    x=alt.X('TEMPORAL:N', title='', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('CASES:Q', title="Diagnosed vs At Risk"),
    tooltip=[alt.Tooltip('CASES:Q', title="Medical Diagnostic:", format=','),
             alt.Tooltip('TEMPORAL:N', title="Time:")]
)

# Layer all components into a final chart
definitive = alt.layer(combined_area_chart, combined_top_line, combined_top_points, combined_bottom_line, combined_bottom_points).properties(height=500, title = "Diagnosed vs At Risk Population in 2023")

st.altair_chart(definitive.configure_title(anchor = "middle"), use_container_width=True)
st.altair_chart(stacked_bar_diseases_RISKS.configure_title(anchor = "middle"), use_container_width=True)
st.button("Export Data", type="primary")

if st.sidebar.button("Log out"):
    st.session_state.logged_in == False
    st.switch_page("auth.py")