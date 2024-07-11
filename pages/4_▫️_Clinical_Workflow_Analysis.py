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

new_nat = "Emirati"
factor = 12

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

col1, col7 = st.columns([6, 1])
with col1:
    st.markdown('# Clinical Workflow Analysis ')
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

#Read csv files
df_data_times = pd.read_csv("DEFINITIVE_TABLES/DATA_TIMES.csv")
df_encounters = pd.read_csv("DEFINITIVE_TABLES/DATA_ENCOUNTERS.csv")
df_proc_hosp = pd.read_csv("DEFINITIVE_TABLES/PROCEDURES_HOSP.csv")
df_counts_detections = pd.read_csv("DEFINITIVE_TABLES/DAYS_COUNTS_DETECTIONS_EXTRA.csv")

#Adapt code
df_data_times["NATIONALITY"] = df_data_times["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_encounters["NATIONALITY"] = df_encounters["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_proc_hosp["NATIONALITY"] = df_proc_hosp["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_counts_detections["NATIONALITY"] = df_counts_detections["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)

df_data_times = df_data_times[df_data_times["DURATION"] >= 90]

df_counts_detections = df_counts_detections[~df_counts_detections['YEAR'].isin([2006, 2007, 2008])]
df_counts_detections['YEAR'] = df_counts_detections['YEAR'].apply(lambda x: x + 2)
df_counts_detections["COUNTS"] = df_counts_detections["COUNTS"] * factor
df_counts_detections["DAYS_DETECTION_DIAGNOSTIC"] = df_counts_detections["DAYS_DETECTION_DIAGNOSTIC"] * factor
df_counts_detections["VISITS_DETECTION_DIAGNOSTIC"] = df_counts_detections["VISITS_DETECTION_DIAGNOSTIC"] * factor
df_counts_detections["EXTRA_HOSP"] = df_counts_detections["EXTRA_HOSP"] * factor
df_counts_detections["EXTRA_PROC"] = df_counts_detections["EXTRA_PROC"] * factor

#Set options of selectors
nationalities = sorted(list(set(df_data_times["NATIONALITY"].values)))
nationalities.insert(0, "All Nationalities")

genders = sorted(list(set(df_data_times["GENDER"].values)))
genders.insert(0, "All Genders")

ages_groups = sorted(list(set(df_data_times["AGE_GROUP"].values)))
ages_groups.insert(0, "All Ages")

diseases = sorted(list(set(df_data_times["DISEASE"].values)))
diseases.insert(0, "All Diseases")

#Selectors
Nationality = st.sidebar.selectbox("Nationality:", nationalities)
Gender = st.sidebar.selectbox("Gender:", genders)
Age_group = st.sidebar.selectbox("Age:", ages_groups)
Disease = st.sidebar.selectbox("Disease:", diseases)

def intervals(num):
    if num > 2500:
        return "2500+"
    elif num > 500:
        inicio_intervalo = 500 + ((num - 500) // 250) * 250
        fin_intervalo = min(inicio_intervalo + 250, 2500)
        intervalo = f"{inicio_intervalo}-{fin_intervalo}"
        return intervalo
    elif num > 250:
        return "250-500"
    elif num > 90:
        return "90-250"
    
def intervals_enc(num):
    if num > 50:
        return "50+"
    else:
        inicio_intervalo = 0 + ((num - 0) // 5) * 5
        fin_intervalo = min(inicio_intervalo + 5, 50)
        intervalo = f"{inicio_intervalo}-{fin_intervalo}"
        return intervalo
    
def calculate_ratio(row, df):
    if row['TIMING'] == 'later':
        on_time_row = df[(df['DISEASE'] == row['DISEASE']) & (df['TYPE'] == row['TYPE']) & (df['TIMING'] == 'on time')]
        if not on_time_row.empty:
            return row['VALUE'] / on_time_row['VALUE'].values[0]
    return None

filtered_dataframes = {
    'df_data_times': df_data_times,
    'df_encounters': df_encounters,
    'df_proc_hosp': df_proc_hosp,
    'df_counts_detections': df_counts_detections
}

for key in filtered_dataframes:
    if Nationality != "All Nationalities":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["NATIONALITY"] == Nationality]
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["NATIONALITY"])
    else:
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["NATIONALITY"])
    if Gender != "All Genders":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["GENDER"] == Gender]
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["GENDER"])
    else:
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["GENDER"])
    if Age_group != "All Ages":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["AGE_GROUP"] == Age_group]
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["AGE_GROUP"])
    else:
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["AGE_GROUP"])
    if Disease != "All Diseases" and key != "df_proc_hosp":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["DISEASE"] == Disease]
    else:
        if key != "df_proc_hosp":
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["DISEASE"])
df_data_times, df_encounters, df_proc_hosp, df_counts_detections = (
    filtered_dataframes['df_data_times'],
    filtered_dataframes['df_encounters'],
    filtered_dataframes['df_proc_hosp'],
    filtered_dataframes['df_counts_detections']
)

if Disease == "All Diseases":
    df_counts_detections = df_counts_detections.groupby(['YEAR']).agg({'DAYS_DETECTION_DIAGNOSTIC': 'sum', 'COUNTS': 'sum', 'VISITS_DETECTION_DIAGNOSTIC':'sum', 'EXTRA_HOSP':'sum', 'EXTRA_PROC':'sum'}).reset_index()
    df_counts_detections = df_counts_detections.sort_values(by='YEAR')
    df_counts_detections['CUMULATIVE_DAYS'] = df_counts_detections['DAYS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_COUNTS'] = df_counts_detections['COUNTS'].cumsum()
    df_counts_detections['CUMULATIVE_VISITS'] = df_counts_detections['VISITS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_HOSP'] = df_counts_detections['EXTRA_HOSP'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_PROC'] = df_counts_detections['EXTRA_PROC'].cumsum()
    mean_duration = df_data_times["DURATION"].mean()
    mean_duration = pd.DataFrame({
    'DURATION': [mean_duration]
    })
    mean_duration["MEAN_GROUPED"] = mean_duration["DURATION"].apply(lambda x : intervals(round(x)))

    mean_duration_enc = df_encounters["DURATION"].mean()
    mean_duration_enc = pd.DataFrame({
    'DURATION': [mean_duration_enc]
    })
    mean_duration_enc["MEAN_GROUPED"] = mean_duration_enc["DURATION"].apply(lambda x : intervals_enc(round(x)))

    df_data_times["COUNTS_GROUPED"] = df_data_times["DURATION"].apply(lambda x : intervals(x))
    df_encounters["COUNTS_GROUPED"] = df_encounters["DURATION"].apply(lambda x : intervals_enc(x))

    df_data_times = df_data_times.groupby(['COUNTS_GROUPED']).size().reset_index(name='FREQUENCY')
    df_data_times = df_data_times[df_data_times["COUNTS_GROUPED"] != "2500-2500"]
    df_data_times = pd.merge(mean_duration, df_data_times, left_on = ["MEAN_GROUPED"], right_on = ["COUNTS_GROUPED"],  how='outer')
    df_data_times["NO_MEAN"] = df_data_times.apply(lambda x : "No" if (pd.isnull(x["DURATION"]) and pd.isnull(x["MEAN_GROUPED"])) else "Average", axis=1)
    df_data_times = df_data_times.drop(["DURATION", "MEAN_GROUPED"], axis = 1)
    total_frequency_per_disease = df_data_times['FREQUENCY'].sum()
    df_data_times["PERCENTAGE"] = df_data_times.apply(lambda row: row['FREQUENCY'] / total_frequency_per_disease, axis=1)

    df_encounters = df_encounters.groupby(['COUNTS_GROUPED']).size().reset_index(name='FREQUENCY')
    df_encounters = df_encounters[df_encounters["COUNTS_GROUPED"] != "50-50"]
    df_encounters = pd.merge(mean_duration_enc, df_encounters, left_on = ["MEAN_GROUPED"], right_on = ["COUNTS_GROUPED"],  how='outer')
    df_encounters["NO_MEAN"] = df_encounters.apply(lambda x : "No" if (pd.isnull(x["DURATION"]) and pd.isnull(x["MEAN_GROUPED"])) else "Average", axis=1)
    df_encounters = df_encounters.drop(["DURATION", "MEAN_GROUPED"], axis = 1)
    total_frequency_per_disease = df_encounters['FREQUENCY'].sum()
    df_encounters["PERCENTAGE"] = df_encounters.apply(lambda row: row['FREQUENCY'] / total_frequency_per_disease, axis=1)

else:
    df_counts_detections = df_counts_detections.groupby(['DISEASE', 'YEAR']).agg({'DAYS_DETECTION_DIAGNOSTIC': 'sum', 'COUNTS': 'sum', 'VISITS_DETECTION_DIAGNOSTIC':'sum', 'EXTRA_HOSP':'sum', 'EXTRA_PROC':'sum'}).reset_index()
    df_counts_detections = df_counts_detections.sort_values(by='YEAR')
    df_counts_detections['CUMULATIVE_DAYS'] = df_counts_detections.groupby('DISEASE')['DAYS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_COUNTS'] = df_counts_detections.groupby('DISEASE')['COUNTS'].cumsum()
    df_counts_detections['CUMULATIVE_VISITS'] = df_counts_detections.groupby('DISEASE')['VISITS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_HOSP'] = df_counts_detections.groupby('DISEASE')['EXTRA_HOSP'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_PROC'] = df_counts_detections.groupby('DISEASE')['EXTRA_PROC'].cumsum()
    mean_duration = pd.DataFrame(df_data_times.groupby(["DISEASE"])["DURATION"].mean())
    mean_duration["MEAN_GROUPED"] = mean_duration["DURATION"].apply(lambda x : intervals(round(x)))
    mean_duration = mean_duration.reset_index()

    mean_duration_enc = pd.DataFrame(df_encounters.groupby(["DISEASE"])["DURATION"].mean())
    mean_duration_enc["MEAN_GROUPED"] = mean_duration_enc["DURATION"].apply(lambda x : intervals_enc(round(x)))
    mean_duration_enc = mean_duration_enc.reset_index()

    df_data_times["COUNTS_GROUPED"] = df_data_times["DURATION"].apply(lambda x : intervals(x))
    df_encounters["COUNTS_GROUPED"] = df_encounters["DURATION"].apply(lambda x : intervals_enc(x))

    df_data_times = df_data_times.groupby(['DISEASE', 'COUNTS_GROUPED']).size().reset_index(name='FREQUENCY')
    df_data_times = df_data_times[df_data_times["COUNTS_GROUPED"] != "2500-2500"]
    df_data_times = pd.merge(mean_duration, df_data_times, left_on = ["DISEASE", "MEAN_GROUPED"], right_on = ["DISEASE", "COUNTS_GROUPED"],  how='outer')
    df_data_times["NO_MEAN"] = df_data_times.apply(lambda x : "No" if (pd.isnull(x["DURATION"]) and pd.isnull(x["MEAN_GROUPED"])) else "Average", axis=1)
    df_data_times = df_data_times.drop(["DURATION", "MEAN_GROUPED"], axis = 1)
    total_frequency_per_disease = df_data_times.groupby('DISEASE')['FREQUENCY'].sum()
    df_data_times["PERCENTAGE"] = df_data_times.apply(lambda row: row['FREQUENCY'] / total_frequency_per_disease[row['DISEASE']], axis=1)

    df_encounters = df_encounters.groupby(['DISEASE', 'COUNTS_GROUPED']).size().reset_index(name='FREQUENCY')
    df_encounters = df_encounters[df_encounters["COUNTS_GROUPED"] != "50-50"]
    df_encounters = pd.merge(mean_duration_enc, df_encounters, left_on = ["DISEASE", "MEAN_GROUPED"], right_on = ["DISEASE", "COUNTS_GROUPED"],  how='outer')
    df_encounters["NO_MEAN"] = df_encounters.apply(lambda x : "No" if (pd.isnull(x["DURATION"]) and pd.isnull(x["MEAN_GROUPED"])) else "Average", axis=1)
    df_encounters = df_encounters.drop(["DURATION", "MEAN_GROUPED"], axis = 1)
    total_frequency_per_disease = df_encounters.groupby('DISEASE')['FREQUENCY'].sum()
    df_encounters["PERCENTAGE"] = df_encounters.apply(lambda row: row['FREQUENCY'] / total_frequency_per_disease[row['DISEASE']], axis=1)

df_data_times["FREQUENCY"] = df_data_times["FREQUENCY"] * factor
df_encounters["FREQUENCY"] = df_encounters["FREQUENCY"] * factor
df_proc_hosp = df_proc_hosp[['DISEASE', 'TYPE','TIMING', 'VALUE']].groupby(['DISEASE', 'TYPE', 'TIMING']).mean().reset_index()
df_proc_hosp["VALUE"] = df_proc_hosp["VALUE"].apply(lambda x : round(x, 2))
pivot_df = df_proc_hosp.pivot_table(index=['DISEASE', 'TYPE'], columns='TIMING', values='VALUE', aggfunc='first').reset_index()
pivot_df['Timing_Value_later'] = pivot_df.get('later', 0)
pivot_df['Timing_Value_time'] = pivot_df.get('on time', 0)
merged_df = df_proc_hosp.merge(pivot_df[['DISEASE', 'TYPE', "Timing_Value_later", 'Timing_Value_time']], on=['DISEASE', 'TYPE'], how='left')
merged_df['Ratio'] = merged_df.apply(lambda row: calculate_ratio(row, merged_df), axis=1)
ratios_df = merged_df[df_proc_hosp['TIMING'] == 'later'][['DISEASE', 'TYPE', "Ratio", 'Timing_Value_later', 'Timing_Value_time']]
ratios_df.reset_index(drop=True,inplace=True)

sorted_list = ['90-250',
'250-500',
'500-750',
'750-1000',
'1000-1250',
'1250-1500',
'1500-1750',
'1750-2000',
'2000-2250',
'2250-2500',
'2500-2500',
'2500+']


base_chart_no_mean = alt.Chart(df_data_times).mark_bar(size = 20, color = "#389889").transform_filter(alt.datum.NO_MEAN != "Average").encode(
y=alt.Y('COUNTS_GROUPED:N', title='Delayed Days', sort=sorted_list),
x=alt.X('FREQUENCY:Q', title='Total Patients'),
tooltip = [alt.Tooltip('FREQUENCY:Q', title = "Counts of delayed days:", format = ",")]
).properties(title=alt.TitleParams("Average Diagnostic Delay per Disease in Days (2011 - 2023)", anchor='middle'), width=500)

base_chart_mean = alt.Chart(df_data_times).mark_bar(size = 20).transform_filter(alt.datum.NO_MEAN == "Average").encode(
y=alt.Y('COUNTS_GROUPED:N', title='Delayed Days', sort=sorted_list),
x=alt.X('FREQUENCY:Q', title='Total Patients'),
tooltip = [alt.Tooltip('FREQUENCY:Q', title = "Counts of delayed days:", format = ",")],
color = alt.Color("NO_MEAN", scale = alt.Scale(range = ["#AB2A3E"]), title = "", legend=None)
).properties(title=alt.TitleParams("Average Diagnostic Delay per Disease in Days (2011 - 2023)", anchor='middle'), width=500)

stacked_text = alt.Chart(df_data_times).mark_text(align='center',baseline='middle', color = 'black', dy = -4, dx = 12).encode(
y=alt.Y('COUNTS_GROUPED:N', sort=sorted_list),
x=alt.X('FREQUENCY:Q'), 
text = alt.Text("PERCENTAGE:N", format = ".0%"),
tooltip=alt.value(None))

final_chart = alt.layer(base_chart_no_mean, base_chart_mean, stacked_text)

sorted_list_enc = ['0-5',
'5-10',
'10-15',
'15-20',
'20-25',
'25-30',
'30-35',
'35-40',
'40-45',
'45-50',
'50+']

base_chart_no_mean_enc = alt.Chart(df_encounters).mark_bar(size = 20, color = "#389889").transform_filter(alt.datum.NO_MEAN != "Average").encode(
x=alt.X('COUNTS_GROUPED:N', title='Delayed Appointments', axis=alt.Axis(labelAngle=90), sort=sorted_list_enc),
y=alt.Y('FREQUENCY:Q', title='Total Appointments'),
tooltip = [alt.Tooltip('FREQUENCY:Q', title = "Counts of delayed visits:")]
).properties(title=alt.TitleParams("Missed Opportunity Appointments per Disease (2011 - 2023)", anchor='middle'), width = 500)

base_chart_mean_enc = alt.Chart(df_encounters).mark_bar(size = 20, color = "#627254").transform_filter(alt.datum.NO_MEAN == "Average").encode(
x=alt.X('COUNTS_GROUPED:N', title='Delayed Appointments', axis=alt.Axis(labelAngle=90), sort=sorted_list_enc),
y=alt.Y('FREQUENCY:Q', title='Total Appointments'),
tooltip = [alt.Tooltip('FREQUENCY:Q', title = "Counts of delayed visits:", format = ",")],
color = alt.Color("NO_MEAN", scale = alt.Scale(range = ["#AB2A3E"]), title = "", legend = None)
).properties(title=alt.TitleParams("Missed Opportunity Appointments per Disease (2011 - 2023)", anchor='middle'), width = 500)

stacked_text_enc = alt.Chart(df_encounters).mark_text(align='center',baseline='middle', color = 'black', dy = -6, dx = 2).encode(
x=alt.X('COUNTS_GROUPED:N', sort=sorted_list_enc),
y=alt.Y('FREQUENCY:Q'), 
text = alt.Text("PERCENTAGE:N", format = ".0%"),
tooltip=alt.value(None))

final_chart_enc = alt.layer(base_chart_no_mean_enc, base_chart_mean_enc, stacked_text_enc)

col1, col2 = st.columns(2)
with col1:
    st.altair_chart(final_chart.configure_view(strokeWidth=0).properties(width='container', height = 450), use_container_width=True)
with col2:
    st.altair_chart(final_chart_enc.configure_view(strokeWidth=0).properties(width='container', height = 450), use_container_width=True)

#Counts of delayed patients
chart_delayed_counts = alt.Chart(df_counts_detections).mark_line(size =4, color = COLORS[Disease]).encode(
    x=alt.X('YEAR:O', title = "", axis=alt.Axis(labelAngle=0)),
    y=alt.Y('CUMULATIVE_COUNTS:Q', title = ""),
    tooltip=alt.value(None)
).properties(title = "Total Number of Diseases with Delayed Diagnosis")

points_delayed_counts = alt.Chart(df_counts_detections).mark_point(filled=True, color = COLORS[Disease]).encode(
    x=alt.X('YEAR:O', title = "", axis=alt.Axis(labelAngle=0)),
    y=alt.Y('CUMULATIVE_COUNTS:Q', title = ""),
    size=alt.Size('CUMULATIVE_COUNTS:Q', legend=None),
    tooltip=[alt.Tooltip('YEAR:O', title='Year'), alt.Tooltip('CUMULATIVE_COUNTS:Q', title='Counts:', format = ",")]
)
chart_delayed_counts = (points_delayed_counts + chart_delayed_counts).properties(width = 500).configure_title(anchor = "middle")

st.altair_chart(chart_delayed_counts, use_container_width=True)

#Ratios plot
chart_h = alt.Chart(ratios_df).mark_rect().transform_filter(alt.datum.TYPE == "Hospitalization").encode(
        x=alt.X('DISEASE:N', axis=alt.Axis(labelAngle=0, labelFontSize=16), title = ""),
        color=alt.Color('Ratio:Q', scale=alt.Scale(scheme='orangered'), legend = None),
        tooltip = [alt.Tooltip("Timing_Value_later:Q", title = "Average Value for delayed Diagnostics:") ,
                alt.Tooltip("Timing_Value_time:Q", title = "Average Value for On time Diagnostics:")]
    ).properties(
        title="Comparing Hospitalization Rates Over Five Years: Delayed Diagnosis vs. Timely Diagnosis", height = 125)
chart_p = alt.Chart(ratios_df).mark_rect().transform_filter(alt.datum.TYPE == "Procedure").encode(
            x=alt.X('DISEASE:N', axis=alt.Axis(labelAngle=0, labelFontSize=16), title = ""),
            color=alt.Color('Ratio:Q', scale=alt.Scale(scheme='orangered'), legend = None),
            tooltip = [alt.Tooltip("Timing_Value_later:Q", title = "Average Value for Delayed Diagnostics:", format = ".2f") ,
                    alt.Tooltip("Timing_Value_time:Q", title = "Average Value for On Time Diagnostics:", format = ".2f")]
        ).properties(
            title="Comparing Procedure Rates Over Five Years: Delayed Diagnosis vs. Timely Diagnosis", height = 125)


        # Adding text marks for the ratios
text_h = chart_h.mark_text(fontWeight="bold", size=25).transform_filter(alt.datum.TYPE == "Hospitalization").transform_calculate(
            text_with_x="format(datum.Ratio, '.2f') + 'x'"
        ).encode(
            text=alt.Text('text_with_x:N'),
            color=alt.value("white")
        )

text_p = chart_p.mark_text(fontWeight="bold", size=25).transform_filter(alt.datum.TYPE == "Procedure").transform_calculate(
            text_with_x="format(datum.Ratio, '.2f') + 'x'"
        ).encode(
            text=alt.Text('text_with_x:N'),
            color=alt.value("white")
        )

combined_chart_h = chart_h + text_h
combined_chart_p = chart_p + text_p


faceted_chart_proc_hosp= (combined_chart_h & combined_chart_p).configure(concat=alt.CompositionConfig(spacing=75))
st.altair_chart(faceted_chart_proc_hosp.configure_title(anchor = "middle"), use_container_width=True)


#Counts of EXTRA HOSP per year
base_hosp = alt.Chart(df_counts_detections).encode(
    x=alt.X('YEAR:O', title = "", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_EXTRA_HOSP:Q', title = "Hospitalizations"),
    tooltip=alt.value(None)
)

points_hosp = base_hosp.mark_point(size=125, color = COLORS[Disease], filled = True).encode(
    tooltip=[alt.Tooltip('YEAR:O', title='Year'), alt.Tooltip('CUMULATIVE_EXTRA_HOSP:Q', title='Counts:', format=",")]
)

line_hosp = base_hosp.mark_rule(color = COLORS[Disease]).encode(
    size=alt.value(6)  
)

chart_delayed_hosp = (points_hosp + line_hosp).properties(
    title=alt.TitleParams("Avoidable Hospitalizations Due to Delayed Diagnosis per Year", anchor='middle'),
    width=500
)

#Counts of EXTRA PROC per year
base_PROC = alt.Chart(df_counts_detections).encode(
    x=alt.X('YEAR:O', title = "", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_EXTRA_PROC:Q', title = "Procedures"),
    tooltip=alt.value(None)
)

points_PROC = base_PROC.mark_point(size=125, color = COLORS[Disease], filled = True).encode(
    tooltip=[alt.Tooltip('YEAR:O', title='Year'), alt.Tooltip('CUMULATIVE_EXTRA_PROC:Q', title='Counts:', format=",")]
)

line_PROC = base_PROC.mark_rule(color = COLORS[Disease]).encode(
    size=alt.value(6)  
)

chart_delayed_PROC = (points_PROC + line_PROC).properties(
    title=alt.TitleParams("Avoidable Procedures Due to Delayed Diagnosis per Year", anchor='middle'),
    width=500
)

col1, col2 = st.columns(2)
with col1:
    st.altair_chart(chart_delayed_hosp.properties(width='container', height=450), use_container_width=True)
with col2:
    st.altair_chart(chart_delayed_PROC.properties(width='container', height=450), use_container_width=True)
    
#Counts of delayed visits per year
base = alt.Chart(df_counts_detections).mark_line(size=4, color = COLORS[Disease]).encode(
    x=alt.X('YEAR:O', title="", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_VISITS:Q', title="Total Appointments"),
    tooltip=alt.value(None)
)

points = alt.Chart(df_counts_detections).mark_point(filled=True, size=100, color = COLORS[Disease]).encode(
    x=alt.X('YEAR:O', title="", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_VISITS:Q', title=""),
    size=alt.Size('CUMULATIVE_VISITS:Q', legend=None),
    tooltip=[alt.Tooltip('YEAR:O', title='Year'), alt.Tooltip('CUMULATIVE_VISITS:Q', title='Counts:', format=",")]
)

chart_delayed_visits = (points + base).properties(
    title=alt.TitleParams("Total Missed Opportunities per Year", anchor='middle'),
    width=500
)

#Counts of delayed days per year
chart_delayed_days = alt.Chart(df_counts_detections).mark_line(size=4, color = COLORS[Disease]).encode(
    x=alt.X('YEAR:O', title = "", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_DAYS:Q', title = "Delayed Days"),
    tooltip=alt.value(None)
)

points_delayed_days = alt.Chart(df_counts_detections).mark_point(color = COLORS[Disease], filled=True, size = 125).encode(
    x=alt.X('YEAR:O', title = "", axis=alt.Axis(labelAngle=90)),
    y='CUMULATIVE_DAYS:Q',
    size=alt.Size('CUMULATIVE_DAYS:Q', legend=None),
    tooltip=[alt.Tooltip('YEAR:O', title='Year'), alt.Tooltip('CUMULATIVE_DAYS:Q', title='Counts:', format = ",")]
)
chart_delayed_days = (points_delayed_days + chart_delayed_days).properties(
    width=500, 
    title=alt.TitleParams("Total Delayed Days per Year", anchor='middle')
)

col1, col2 = st.columns(2)
with col1:
    st.altair_chart(chart_delayed_days.properties(width='container', height=450), use_container_width=True)
with col2:
    st.altair_chart(chart_delayed_visits.properties(width='container', height=450), use_container_width=True)

st.button("Export Data", type="primary")

if st.sidebar.button("Log out"):
    st.session_state.logged_in == False
    st.switch_page("auth.py")