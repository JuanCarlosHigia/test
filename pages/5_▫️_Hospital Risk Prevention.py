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
    st.markdown('# Risk Prevention Strategy Assessment ')
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
df_counts_detections = pd.read_csv("DEFINITIVE_TABLES/DAYS_COUNTS_DETECTIONS_HOSP.csv")
df_quantifications = pd.read_csv("DEFINITIVE_TABLES/DAYS_COUNTS_DETECTIONS_HOSP.csv")
#df_counts_detections = pd.read_csv("DEFINITIVE_TABLES/ARABIA_HOSP_CLUSTERS_WITH_DETECTIONS.csv")
#df_unique_rows = pd.read_csv("DEFINITIVE_TABLES/DIAGS_UNIQUE_ROW.csv")
df_lat_lon = pd.read_csv("DEFINITIVE_TABLES/LAT_LON.csv")
#Adapt code
#df_unique_rows["DOCTOR"] = df_unique_rows["DOCTOR"].replace("niyas ebrahim kunju", "Niyas Ebrahim Kunju")
df_counts_detections["DOCTOR"] = df_counts_detections["DOCTOR"].replace("niyas ebrahim kunju", "Niyas Ebrahim Kunju")


#df_unique_rows = pd.concat([df_unique_rows]*factor, ignore_index=True)
df_data_times["NATIONALITY"] = df_data_times["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_encounters["NATIONALITY"] = df_encounters["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_proc_hosp["NATIONALITY"] = df_proc_hosp["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
df_counts_detections["NATIONALITY"] = df_counts_detections["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)
#df_unique_rows["NATIONALITY"] = df_unique_rows["NATIONALITY"].apply(lambda x : new_nat if x == "Israeli" else x)

df_data_times = df_data_times[df_data_times["DURATION"] >= 90]

df_counts_detections = df_counts_detections[~df_counts_detections['YEAR'].isin([2006, 2007, 2008])]
df_counts_detections['YEAR'] = df_counts_detections['YEAR'].apply(lambda x: x + 2)
df_counts_detections['MONTH'] = df_counts_detections['MONTH'].apply(lambda x: f"{x:02d}")
df_counts_detections['YEAR-MONTH'] = df_counts_detections.apply(lambda x: f"{x['YEAR']}-{x['MONTH']}", axis=1)
df_counts_detections["COUNTS"] = df_counts_detections["COUNTS"] * factor
df_counts_detections["DAYS_DETECTION_DIAGNOSTIC"] = df_counts_detections["DAYS_DETECTION_DIAGNOSTIC"] * factor
df_counts_detections["VISITS_DETECTION_DIAGNOSTIC"] = df_counts_detections["VISITS_DETECTION_DIAGNOSTIC"] * factor
df_counts_detections["EXTRA_HOSP"] = df_counts_detections["EXTRA_HOSP"] * factor
df_counts_detections["EXTRA_PROC"] = df_counts_detections["EXTRA_PROC"] * factor

#Set options of selectors
nationalities = sorted(list(set(df_counts_detections["NATIONALITY"].values)))
nationalities.insert(0, "All Nationalities")

genders = sorted(list(set(df_counts_detections["GENDER"].values)))
genders.insert(0, "All Genders")

ages_groups = sorted(list(set(df_counts_detections["AGE_GROUP"].values)))
ages_groups.insert(0, "All Ages")

diseases = sorted(list(set(df_counts_detections["DISEASE"].values)))
diseases.insert(0, "All Diseases")

#Selectors
Nationality = st.sidebar.selectbox("Nationality:", nationalities)
Gender = st.sidebar.selectbox("Gender:", genders)
Age_group = st.sidebar.selectbox("Age:", ages_groups)
Disease = st.sidebar.selectbox("Disease:", diseases)

# Filtrado por Region
region = sorted(list(set(df_counts_detections["REGION"].values)))
region.insert(0, "All Regions")
Region = st.sidebar.selectbox("Region:", region)

if Region != "All Regions":
    df_counts_detections = df_counts_detections[df_counts_detections["REGION"] == Region]

# Filtrado por Hospital
hospital = sorted(list(set(df_counts_detections["HOSPITAL"].values)))
hospital.insert(0, "All Hospitals")
Hospital = st.sidebar.selectbox("Hospital:", hospital)

if Hospital != "All Hospitals":
    df_counts_detections = df_counts_detections[df_counts_detections["HOSPITAL"] == Hospital]

# Filtrado por Speciality
speciality = sorted(list(set(df_counts_detections["SPECIALITY"].values)))
speciality.insert(0, "All Specialities")
Speciality = st.sidebar.selectbox("Speciality:", speciality)

if Speciality != "All Specialities":
    df_counts_detections = df_counts_detections[df_counts_detections["SPECIALITY"] == Speciality]

# Filtrado por Doctor
doctor = sorted(list(set(df_counts_detections["DOCTOR"].values)))
doctor.insert(0, "All Doctors")
Doctor = st.sidebar.selectbox("Doctor:", doctor)

if Doctor != "All Doctors":
    df_counts_detections = df_counts_detections[df_counts_detections["DOCTOR"] == Doctor]

filtered_dataframes = {
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
    if Disease != "All Diseases":
        filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["DISEASE"] == Disease]
        if key != "df_counts_detections":
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["DISEASE"])
    else:
        filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["DISEASE"])
    if key != "df_unique_rows":
        if Hospital != "All Hospitals":
            filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["HOSPITAL"] == Hospital]
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["HOSPITAL"])
        else:
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["HOSPITAL"])
        if Region != "All Regions":
            filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["REGION"] == Region]
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["REGION"])
        else:
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["REGION"])
        if Doctor != "All Doctors":
            filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["DOCTOR"] == Doctor]
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["DOCTOR"])
        else:
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["DOCTOR"])
        if Speciality != "All Specialities":
            filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]["SPECIALITY"] == Speciality]
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["SPECIALITY"])
        else:
            filtered_dataframes[key] = filtered_dataframes[key].drop(columns=["SPECIALITY"])
        
df_counts_detections = (
    filtered_dataframes['df_counts_detections']
)

if Disease == "All Diseases":
    df_counts_detections = df_counts_detections.groupby(["YEAR-MONTH"]).agg({'DAYS_DETECTION_DIAGNOSTIC': 'sum', 'COUNTS': 'sum', 'VISITS_DETECTION_DIAGNOSTIC':'sum', 'EXTRA_HOSP':'sum', 'EXTRA_PROC':'sum'}).reset_index()
    df_counts_detections = df_counts_detections.sort_values(by=['YEAR-MONTH'])
    df_counts_detections['CUMULATIVE_DAYS'] = df_counts_detections['DAYS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_COUNTS'] = df_counts_detections['COUNTS'].cumsum()
    df_counts_detections['CUMULATIVE_VISITS'] = df_counts_detections['VISITS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_HOSP'] = df_counts_detections['EXTRA_HOSP'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_PROC'] = df_counts_detections['EXTRA_PROC'].cumsum()

else:
    df_counts_detections = df_counts_detections.groupby(['DISEASE', "YEAR-MONTH"]).agg({'DAYS_DETECTION_DIAGNOSTIC': 'sum', 'COUNTS': 'sum', 'VISITS_DETECTION_DIAGNOSTIC':'sum', 'EXTRA_HOSP':'sum', 'EXTRA_PROC':'sum'}).reset_index()
    df_counts_detections = df_counts_detections.sort_values(by=['YEAR-MONTH'])
    df_counts_detections['CUMULATIVE_DAYS'] = df_counts_detections.groupby('DISEASE')['DAYS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_COUNTS'] = df_counts_detections.groupby('DISEASE')['COUNTS'].cumsum()
    df_counts_detections['CUMULATIVE_VISITS'] = df_counts_detections.groupby('DISEASE')['VISITS_DETECTION_DIAGNOSTIC'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_HOSP'] = df_counts_detections.groupby('DISEASE')['EXTRA_HOSP'].cumsum()
    df_counts_detections['CUMULATIVE_EXTRA_PROC'] = df_counts_detections.groupby('DISEASE')['EXTRA_PROC'].cumsum()

#df_unique_rows = df_unique_rows.drop(columns=["REGION", "DOCTOR", "SPECIALITY"])
#df_unique_rows = df_unique_rows.groupby('HOSPITAL').size().reset_index(name='COUNT')
#df_lat_lon['COORDINATES'] = df_lat_lon.apply(lambda row: [row['lon'], row['lat']], axis=1)
#hospital_location_data = pd.merge(df_unique_rows, df_lat_lon, on='HOSPITAL', how='inner')
size = df_counts_detections["COUNTS"].sum()
#size_hosp = df_unique_rows["COUNT"].sum()
start_date, end_date = st.select_slider(
    "Select a time interval",
    options=list(df_counts_detections["YEAR-MONTH"].values),
    value=(list(df_counts_detections["YEAR-MONTH"].values)[len(df_counts_detections["YEAR-MONTH"].values)//3], list(df_counts_detections["YEAR-MONTH"].values)[len(df_counts_detections["YEAR-MONTH"].values)*2//3]))
df_counts_detections = df_counts_detections[(df_counts_detections['YEAR-MONTH'] >= start_date) & (df_counts_detections['YEAR-MONTH'] <= end_date)]


#Counts of delayed visits per year
base = alt.Chart(df_counts_detections).mark_area(opacity=0.3, color=COLORS[Disease]).encode(
    x=alt.X('YEAR-MONTH:O', title="", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_VISITS:Q', title="Total Appointments"),
    tooltip=alt.value(None)
)

points = alt.Chart(df_counts_detections).mark_point(filled=True, size=100, color=COLORS[Disease]).encode(
    x=alt.X('YEAR-MONTH:O', title="", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_VISITS:Q', title=""),
    size=alt.Size('CUMULATIVE_VISITS:Q', legend=None),
    tooltip=[alt.Tooltip('YEAR-MONTH:O', title='Year'), alt.Tooltip('CUMULATIVE_VISITS:Q', title='Counts:', format=",")]
)

chart_delayed_visits = (points + base).properties(
    title=alt.TitleParams("Total Missed Opportunities per Year", anchor='middle'),height = 360)

#Counts of delayed days per year
chart_delayed_days = alt.Chart(df_counts_detections).mark_area(opacity=0.3, color=COLORS[Disease]).encode(
    x=alt.X('YEAR-MONTH:O', title="", axis=alt.Axis(labelAngle=90)),
    y=alt.Y('CUMULATIVE_DAYS:Q', title="Delayed Days"),
    tooltip=alt.value(None)
).properties(title=alt.TitleParams("Total Delayed Days per Year", anchor='middle'))

points_delayed_days = alt.Chart(df_counts_detections).mark_point(color=COLORS[Disease], filled=True, size=125).encode(
    x=alt.X('YEAR-MONTH:O', title="", axis=alt.Axis(labelAngle=90)),
    y='CUMULATIVE_DAYS:Q',
    size=alt.Size('CUMULATIVE_DAYS:Q', legend=None),
    tooltip=[alt.Tooltip('YEAR-MONTH:O', title='Year'), alt.Tooltip('CUMULATIVE_DAYS:Q', title='Counts:', format=",")]
)
chart_delayed_days = (points_delayed_days + chart_delayed_days).properties(height = 360)

col1, col2 = st.columns(2)
with col1:
    st.altair_chart(chart_delayed_days.configure_view(strokeWidth=0).properties(width='container'), use_container_width=True)
with col2:
    st.altair_chart(chart_delayed_visits.configure_view(strokeWidth=0).properties(width='container'), use_container_width=True)
df_patients = pd.read_csv("DEFINITIVE_TABLES/SIMULATED_PATIENTS.csv")
df_patients.columns = ["Patient ID", "Is At Risk", "Has Been Contacted"]
df_patients = df_patients.sample(frac=1, random_state=size).reset_index(drop=True)

if Disease == "All Diseases":
    np.random.seed(size)
    diseases_list = diseases[1:]
    df_patients['Disease'] = np.random.choice(diseases_list, size=len(df_patients))
    df_patients = df_patients[["Patient ID", "Disease", "Is At Risk", "Has Been Contacted"]]
    col1, col2, col3 = st.columns(3)
    with col1:
        at_risk_filter = st.multiselect("Filter by At Risk:", options=df_patients['Is At Risk'].unique())
    with col2:
        contacted_filter = st.multiselect("Filter by Contacted:", options=df_patients['Has Been Contacted'].unique())
    with col3:
        diseases_all_filter = st.multiselect("Filter by Disease:", options=df_patients['Disease'].unique())
    filtered_data = df_patients.copy()
    if at_risk_filter:
        filtered_data = filtered_data[filtered_data['Is At Risk'].isin(at_risk_filter)]
    if contacted_filter:
        filtered_data = filtered_data[filtered_data['Has Been Contacted'].isin(contacted_filter)]
    if diseases_all_filter:
        filtered_data = filtered_data[filtered_data['Disease'].isin(diseases_all_filter)]

else:
    col1, col2 = st.columns(2)
    with col1:
        at_risk_filter = st.multiselect("Filter by At Risk:", options=df_patients['Is At Risk'].unique())
    with col2:
        contacted_filter = st.multiselect("Filter by Contacted:", options=df_patients['Has Been Contacted'].unique())
    filtered_data = df_patients.copy()
    if at_risk_filter:
        filtered_data = filtered_data[filtered_data['Is At Risk'].isin(at_risk_filter)]
    if contacted_filter:
        filtered_data = filtered_data[filtered_data['Has Been Contacted'].isin(contacted_filter)]    



st.dataframe(filtered_data, use_container_width=True, hide_index=True)

st.button("Export Data", type="primary")

if st.sidebar.button("Log out"):
    st.session_state.logged_in == False
    st.switch_page("auth.py")