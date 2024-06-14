import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import time
import base64
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


st.set_page_config(page_title="HIGIA", layout = "wide")
st.markdown('# Introduction')

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

new_nat = "Israeli"
factor = 1

#Read csv files
df_uniques = pd.read_csv("DEFINITIVE_TABLES/DIAGS_UNIQUE_ROW.csv")
df_combinations = pd.read_csv("DEFINITIVE_TABLES/COMBINATIONS.csv")
df_uniques["NATIONALITY"] = df_uniques["NATIONALITY"].apply(lambda x : "Local" if x == "Israeli" else "Foreigner")
df_uniques.drop(["SWITCHDATE", "HOSPITAL", "DOCTOR", "SPECIALITY"], axis = 1, inplace = True)
df_uniques["DISEASE"] = df_uniques["DISEASE"].apply(lambda x : "Heart Disease" if x == "Heart disease" else x)

df_combinations['COUNTS'] = df_combinations['COMBINED_DIAGS'].apply(lambda x: len(x.split(',')))
df_combinations.loc[df_combinations['COMBINED_DIAGS'] == 'No diags', 'COUNTS'] = 0
df_combinations["COUNTS"] = df_combinations["COUNTS"].apply(lambda x : "3+" if x > 3 else x)
counts_combis = pd.DataFrame(df_combinations.groupby('COUNTS').size().reset_index())
counts_combis.columns = ["COMBINATIONS", "COUNTS"]
total_counts = counts_combis['COUNTS'].sum()
counts_combis['PERCENTAGE'] = (counts_combis['COUNTS'] / total_counts)

# Calculate the cumulative counts and positions
counts_combis['POSITION'] = 0
for i in range(len(counts_combis)):
    if i == 0:
        counts_combis.loc[i, 'POSITION'] = counts_combis.loc[i, 'COUNTS'] / 2
    else:
        counts_combis.loc[i, 'POSITION'] = counts_combis.loc[i - 1, 'POSITION'] + counts_combis.loc[i-1, 'COUNTS'] / 2 + counts_combis.loc[i, 'COUNTS'] / 2

genders = df_uniques.drop_duplicates(subset=['GENDER', 'ID'])
gender_count = genders['GENDER'].value_counts()

regions = df_uniques.drop_duplicates(subset=['REGION', 'ID'])
region_count = regions['REGION'].value_counts()

ages = df_uniques.drop_duplicates(subset=['AGE_GROUP', 'ID'])
ages_count = ages['AGE_GROUP'].value_counts()

diseases_count = df_uniques["DISEASE"].value_counts()

locals = df_uniques.drop_duplicates(subset=['NATIONALITY', 'ID'])
locals_count = locals['NATIONALITY'].value_counts()

df_uniques["DISEASE"] = df_uniques["DISEASE"].replace("No Diseases", float("NaN"))
disease_count_per_id = pd.DataFrame(pd.DataFrame(df_uniques[df_uniques["DISEASE"] != "No Diseases"].groupby('ID')['DISEASE'].count()).reset_index()["DISEASE"].value_counts()).reset_index()

c1, c2 = st.columns(2)

s=25

gender = alt.Chart(gender_count.reset_index()).mark_bar(size = s).encode(
    y=alt.Y("GENDER", title=""), 
    x=alt.X("count", title="", scale=alt.Scale(domain=[0, 240000])), 
    color=alt.Color("GENDER", legend=None, scale=alt.Scale(domain=["Female", "Male"], range=["#9f5a99", "#999f5a"]), title=""),
    tooltip=[alt.Tooltip('count:Q', title='Counts', format = ",")])

local = alt.Chart(locals_count.reset_index()).mark_bar(size = s).encode(
    y=alt.Y("NATIONALITY", title=""), 
    x=alt.X("count", title="", scale=alt.Scale(domain=[0, 240000])), 	
    color=alt.Color("NATIONALITY", legend=None, title="", scale=alt.Scale(domain=["Local", "Foreigner"], range=["#5a9f83", "#5a779f"])),
    tooltip=[alt.Tooltip('count:Q', title='Counts', format = ",")])
age = alt.Chart(ages_count.reset_index()).mark_bar().encode(
    x=alt.X("AGE_GROUP", title="", axis=alt.Axis(labelAngle=0)), 
    y=alt.Y("count", title=""), 
    color=alt.Color("AGE_GROUP", legend=None, title="", scale=alt.Scale(range=["#89b8bc", "#79aeb3", "#69a4aa", "#5a999f", "#51898f", "#487a7e", "#3e6a6e"])),
    tooltip=[alt.Tooltip('count:Q', title='Counts', format = ",")])
with c1:
    st.altair_chart(gender.properties(title=alt.TitleParams("Gender Distribution of Population", anchor='middle'), width='container', height=150), use_container_width=True)
    st.altair_chart(local.properties(title=alt.TitleParams("Nativity Distribution of Population", anchor='middle'), width='container', height=150), use_container_width=True)
with c2:
    st.altair_chart(age.properties(title=alt.TitleParams("Age Distribution of Population", anchor = "middle"), width='container', height=325), use_container_width=True)

combis_chart = alt.Chart(counts_combis).mark_bar(size = s).encode(
            x=alt.X('COUNTS', title = ""),
            color=alt.Color('COMBINATIONS:N', legend = None),
            tooltip=[alt.Tooltip('COUNTS:Q', title='Counts', format = ",")]
            )

text =  alt.Chart(counts_combis).mark_text(align='center', baseline='middle', color="white", fontWeight='bold', fontSize=16).encode(
            text=alt.Text('COMBINATIONS:N'), x="POSITION:Q", tooltip = alt.value(None)
        )
st.altair_chart((combis_chart + text).properties(title=alt.TitleParams("Distribution of Individuals by Number of Diagnosed Diseases", anchor = "middle"), height = 100), use_container_width = True)
ckd, diabetes, dyslipidemia, heartdisease, hypertension, nash, obesity = st.tabs(["CKD", "Diabetes", "Dyslipidemia", "Heart Disease", "Hypertension", "Nash", "Obesity"])

with ckd:
    c1, c2 = st.columns([1, 2])
    with c1:
        genders_disease = df_uniques[df_uniques["DISEASE"] == "CKD"]['GENDER'].value_counts().reset_index()

        male = int(genders_disease[genders_disease["GENDER"] == "Male"]["count"])
        female = int(genders_disease[genders_disease["GENDER"] == "Female"]["count"])

        local_diseases = df_uniques[df_uniques["DISEASE"] == "CKD"]["NATIONALITY"].value_counts().reset_index()

        local = int(local_diseases[local_diseases["NATIONALITY"] == "Local"]["count"])
        foreigner = int(local_diseases[local_diseases["NATIONALITY"] == "Foreigner"]["count"])

        age_diseases = df_uniques[df_uniques["DISEASE"] == "CKD"][["AGE_GROUP"]]
        age_diseases["AGE_GROUP"] = age_diseases["AGE_GROUP"].apply(lambda x : "Underage" if x == "10-19" else "Adult")
        age_diseases = age_diseases.value_counts().reset_index()

        underage = int(age_diseases[age_diseases["AGE_GROUP"] == "Underage"]["count"])
        adult = int(age_diseases[age_diseases["AGE_GROUP"] == "Adult"]["count"])

        data = {
            "Category": ["Male", "Female", "Local", "Foreigner", "Underage", "Adult"],
            "Value": [male, female, local, foreigner, underage, adult]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)


    with c2:
        a=df_uniques[df_uniques["DISEASE"] == "CKD"].groupby(['GENDER', 'AGE_GROUP']).size().reset_index()
        a.columns = ["GENDER", "AGE_GROUP", "COUNT"]
        a['RANK'] = a['COUNT'].rank(method='min', ascending=False)

            # Creating a tree map with a hot scale color
        tree_map = alt.Chart(a).mark_rect().encode(
        y=alt.Y('GENDER:N', title=''),
        x=alt.X('AGE_GROUP:N', title='', axis=alt.Axis(labelAngle=0)),
        color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Count', legend=None),
        size='COUNT:Q',
        tooltip=[alt.Tooltip('COUNT:Q', title='Counts', format = ",")]).properties(
        height=500,
    )
        
        txt = alt.Chart(a).mark_text(fontSize=30, fontWeight='bold', color='white').transform_filter(alt.datum.RANK <= 5).encode(
            y=alt.Y('GENDER:N', title=''),
            x=alt.X('AGE_GROUP:N', title=''),
            text=alt.Text('RANK:N')
        )

        st.altair_chart((tree_map+txt).properties(width='container', height=290), use_container_width=True)

with diabetes:
    c1, c2 = st.columns([1, 2])
    with c1:
        genders_disease = df_uniques[df_uniques["DISEASE"] == "Diabetes"]['GENDER'].value_counts().reset_index()

        male = int(genders_disease[genders_disease["GENDER"] == "Male"]["count"])
        female = int(genders_disease[genders_disease["GENDER"] == "Female"]["count"])

        local_diseases = df_uniques[df_uniques["DISEASE"] == "Diabetes"]["NATIONALITY"].value_counts().reset_index()

        local = int(local_diseases[local_diseases["NATIONALITY"] == "Local"]["count"])
        foreigner = int(local_diseases[local_diseases["NATIONALITY"] == "Foreigner"]["count"])

        age_diseases = df_uniques[df_uniques["DISEASE"] == "Diabetes"][["AGE_GROUP"]]
        age_diseases["AGE_GROUP"] = age_diseases["AGE_GROUP"].apply(lambda x : "Underage" if x == "10-19" else "Adult")
        age_diseases = age_diseases.value_counts().reset_index()

        underage = int(age_diseases[age_diseases["AGE_GROUP"] == "Underage"]["count"])
        adult = int(age_diseases[age_diseases["AGE_GROUP"] == "Adult"]["count"])

        data = {
            "Category": ["Male", "Female", "Local", "Foreigner", "Underage", "Adult"],
            "Value": [male, female, local, foreigner, underage, adult]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with c2:
        a=df_uniques[df_uniques["DISEASE"] == "Diabetes"].groupby(['GENDER', 'AGE_GROUP']).size().reset_index()
        a.columns = ["GENDER", "AGE_GROUP", "COUNT"]
        a['RANK'] = a['COUNT'].rank(method='min', ascending=False)

            # Creating a tree map with a hot scale color
        tree_map = alt.Chart(a).mark_rect().encode(
        y=alt.Y('GENDER:N', title=''),
        x=alt.X('AGE_GROUP:N', title='', axis=alt.Axis(labelAngle=0)),
        color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Count', legend=None),
        size='COUNT:Q',
        tooltip=[alt.Tooltip('COUNT:Q', title='Counts', format = ",")]).properties(
        height=500,
    )
        
        txt = alt.Chart(a).mark_text(fontSize=30, fontWeight='bold', color='white').transform_filter(alt.datum.RANK <= 5).encode(
            y=alt.Y('GENDER:N', title=''),
            x=alt.X('AGE_GROUP:N', title=''),
            text=alt.Text('RANK:N')
        )

        st.altair_chart((tree_map+txt).properties(width='container', height=290), use_container_width=True)

with dyslipidemia:
    c1, c2 = st.columns([1, 2])
    with c1:
        genders_disease = df_uniques[df_uniques["DISEASE"] == "Dyslipidemia"]['GENDER'].value_counts().reset_index()

        male = int(genders_disease[genders_disease["GENDER"] == "Male"]["count"])
        female = int(genders_disease[genders_disease["GENDER"] == "Female"]["count"])

        local_diseases = df_uniques[df_uniques["DISEASE"] == "Dyslipidemia"]["NATIONALITY"].value_counts().reset_index()

        local = int(local_diseases[local_diseases["NATIONALITY"] == "Local"]["count"])
        foreigner = int(local_diseases[local_diseases["NATIONALITY"] == "Foreigner"]["count"])

        age_diseases = df_uniques[df_uniques["DISEASE"] == "Dyslipidemia"][["AGE_GROUP"]]
        age_diseases["AGE_GROUP"] = age_diseases["AGE_GROUP"].apply(lambda x : "Underage" if x == "10-19" else "Adult")
        age_diseases = age_diseases.value_counts().reset_index()

        underage = int(age_diseases[age_diseases["AGE_GROUP"] == "Underage"]["count"])
        adult = int(age_diseases[age_diseases["AGE_GROUP"] == "Adult"]["count"])

        data = {
            "Category": ["Male", "Female", "Local", "Foreigner", "Underage", "Adult"],
            "Value": [male, female, local, foreigner, underage, adult]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)



    with c2:
        a=df_uniques[df_uniques["DISEASE"] == "Dyslipidemia"].groupby(['GENDER', 'AGE_GROUP']).size().reset_index()
        a.columns = ["GENDER", "AGE_GROUP", "COUNT"]
        a['RANK'] = a['COUNT'].rank(method='min', ascending=False)

            # Creating a tree map with a hot scale color
        tree_map = alt.Chart(a).mark_rect().encode(
        y=alt.Y('GENDER:N', title=''),
        x=alt.X('AGE_GROUP:N', title='', axis=alt.Axis(labelAngle=0)),
        color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Count', legend=None),
        size='COUNT:Q',
        tooltip=[alt.Tooltip('COUNT:Q', title='Counts', format = ",")]).properties(
        height=500,
    )
        
        txt = alt.Chart(a).mark_text(fontSize=30, fontWeight='bold', color='white').transform_filter(alt.datum.RANK <= 5).encode(
            y=alt.Y('GENDER:N', title=''),
            x=alt.X('AGE_GROUP:N', title=''),
            text=alt.Text('RANK:N')
        )

        st.altair_chart((tree_map+txt).properties(width='container', height=290), use_container_width=True)

with heartdisease:
    c1, c2 = st.columns([1, 2])
    with c1:
        genders_disease = df_uniques[df_uniques["DISEASE"] == "Heart Disease"]['GENDER'].value_counts().reset_index()

        male = int(genders_disease[genders_disease["GENDER"] == "Male"]["count"])
        female = int(genders_disease[genders_disease["GENDER"] == "Female"]["count"])

        local_diseases = df_uniques[df_uniques["DISEASE"] == "Heart Disease"]["NATIONALITY"].value_counts().reset_index()

        local = int(local_diseases[local_diseases["NATIONALITY"] == "Local"]["count"])
        foreigner = int(local_diseases[local_diseases["NATIONALITY"] == "Foreigner"]["count"])

        age_diseases = df_uniques[df_uniques["DISEASE"] == "Heart Disease"][["AGE_GROUP"]]
        age_diseases["AGE_GROUP"] = age_diseases["AGE_GROUP"].apply(lambda x : "Underage" if x == "10-19" else "Adult")
        age_diseases = age_diseases.value_counts().reset_index()

        underage = int(age_diseases[age_diseases["AGE_GROUP"] == "Underage"]["count"])
        adult = int(age_diseases[age_diseases["AGE_GROUP"] == "Adult"]["count"])

        data = {
            "Category": ["Male", "Female", "Local", "Foreigner", "Underage", "Adult"],
            "Value": [male, female, local, foreigner, underage, adult]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)



    with c2:
        a=df_uniques[df_uniques["DISEASE"] == "Heart Disease"].groupby(['GENDER', 'AGE_GROUP']).size().reset_index()
        a.columns = ["GENDER", "AGE_GROUP", "COUNT"]
        a['RANK'] = a['COUNT'].rank(method='min', ascending=False)

            # Creating a tree map with a hot scale color
        tree_map = alt.Chart(a).mark_rect().encode(
        y=alt.Y('GENDER:N', title=''),
        x=alt.X('AGE_GROUP:N', title='', axis=alt.Axis(labelAngle=0)),
        color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Count', legend=None),
        size='COUNT:Q',
        tooltip=[alt.Tooltip('COUNT:Q', title='Counts', format = ",")]).properties(
        height=500,
    )
        
        txt = alt.Chart(a).mark_text(fontSize=30, fontWeight='bold', color='white').transform_filter(alt.datum.RANK <= 5).encode(
            y=alt.Y('GENDER:N', title=''),
            x=alt.X('AGE_GROUP:N', title=''),
            text=alt.Text('RANK:N')
        )

        st.altair_chart((tree_map+txt).properties(width='container', height=290), use_container_width=True)

with hypertension:
    c1, c2 = st.columns([1, 2])
    with c1:
        genders_disease = df_uniques[df_uniques["DISEASE"] == "Hypertension"]['GENDER'].value_counts().reset_index()

        male = int(genders_disease[genders_disease["GENDER"] == "Male"]["count"])
        female = int(genders_disease[genders_disease["GENDER"] == "Female"]["count"])

        local_diseases = df_uniques[df_uniques["DISEASE"] == "Hypertension"]["NATIONALITY"].value_counts().reset_index()

        local = int(local_diseases[local_diseases["NATIONALITY"] == "Local"]["count"])
        foreigner = int(local_diseases[local_diseases["NATIONALITY"] == "Foreigner"]["count"])

        age_diseases = df_uniques[df_uniques["DISEASE"] == "Hypertension"][["AGE_GROUP"]]
        age_diseases["AGE_GROUP"] = age_diseases["AGE_GROUP"].apply(lambda x : "Underage" if x == "10-19" else "Adult")
        age_diseases = age_diseases.value_counts().reset_index()

        underage = int(age_diseases[age_diseases["AGE_GROUP"] == "Underage"]["count"])
        adult = int(age_diseases[age_diseases["AGE_GROUP"] == "Adult"]["count"])

        data = {
            "Category": ["Male", "Female", "Local", "Foreigner", "Underage", "Adult"],
            "Value": [male, female, local, foreigner, underage, adult]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)



    with c2:
        a=df_uniques[df_uniques["DISEASE"] == "Hypertension"].groupby(['GENDER', 'AGE_GROUP']).size().reset_index()
        a.columns = ["GENDER", "AGE_GROUP", "COUNT"]
        a['RANK'] = a['COUNT'].rank(method='min', ascending=False)

            # Creating a tree map with a hot scale color
        tree_map = alt.Chart(a).mark_rect().encode(
        y=alt.Y('GENDER:N', title=''),
        x=alt.X('AGE_GROUP:N', title='', axis=alt.Axis(labelAngle=0)),
        color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Count', legend=None),
        size='COUNT:Q',
        tooltip=[alt.Tooltip('COUNT:Q', title='Counts', format = ",")]).properties(
        height=500,
    )
        
        txt = alt.Chart(a).mark_text(fontSize=30, fontWeight='bold', color='white').transform_filter(alt.datum.RANK <= 5).encode(
            y=alt.Y('GENDER:N', title=''),
            x=alt.X('AGE_GROUP:N', title=''),
            text=alt.Text('RANK:N')
        )

        st.altair_chart((tree_map+txt).properties(width='container', height=290), use_container_width=True)

with nash:
    c1, c2 = st.columns([1, 2])
    with c1:
        genders_disease = df_uniques[df_uniques["DISEASE"] == "Nash"]['GENDER'].value_counts().reset_index()

        male = int(genders_disease[genders_disease["GENDER"] == "Male"]["count"])
        female = int(genders_disease[genders_disease["GENDER"] == "Female"]["count"])

        local_diseases = df_uniques[df_uniques["DISEASE"] == "Nash"]["NATIONALITY"].value_counts().reset_index()

        local = int(local_diseases[local_diseases["NATIONALITY"] == "Local"]["count"])
        foreigner = int(local_diseases[local_diseases["NATIONALITY"] == "Foreigner"]["count"])

        age_diseases = df_uniques[df_uniques["DISEASE"] == "Nash"][["AGE_GROUP"]]
        age_diseases["AGE_GROUP"] = age_diseases["AGE_GROUP"].apply(lambda x : "Underage" if x == "10-19" else "Adult")
        age_diseases = age_diseases.value_counts().reset_index()

        underage = int(age_diseases[age_diseases["AGE_GROUP"] == "Underage"]["count"])
        adult = int(age_diseases[age_diseases["AGE_GROUP"] == "Adult"]["count"])

        data = {
            "Category": ["Male", "Female", "Local", "Foreigner", "Underage", "Adult"],
            "Value": [male, female, local, foreigner, underage, adult]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)



    with c2:
        a=df_uniques[df_uniques["DISEASE"] == "Nash"].groupby(['GENDER', 'AGE_GROUP']).size().reset_index()
        a.columns = ["GENDER", "AGE_GROUP", "COUNT"]
        a['RANK'] = a['COUNT'].rank(method='min', ascending=False)

            # Creating a tree map with a hot scale color
        tree_map = alt.Chart(a).mark_rect().encode(
        y=alt.Y('GENDER:N', title=''),
        x=alt.X('AGE_GROUP:N', title='', axis=alt.Axis(labelAngle=0)),
        color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Count', legend=None),
        size='COUNT:Q',
        tooltip=[alt.Tooltip('COUNT:Q', title='Counts', format = ",")]).properties(
        height=500,
    )
        
        txt = alt.Chart(a).mark_text(fontSize=30, fontWeight='bold', color='white').transform_filter(alt.datum.RANK <= 5).encode(
            y=alt.Y('GENDER:N', title=''),
            x=alt.X('AGE_GROUP:N', title=''),
            text=alt.Text('RANK:N')
        )

        st.altair_chart((tree_map+txt).properties(width='container', height=290), use_container_width=True)

with obesity:
    c1, c2 = st.columns([1, 2])
    with c1:
        genders_disease = df_uniques[df_uniques["DISEASE"] == "Obesity"]['GENDER'].value_counts().reset_index()

        male = int(genders_disease[genders_disease["GENDER"] == "Male"]["count"])
        female = int(genders_disease[genders_disease["GENDER"] == "Female"]["count"])

        local_diseases = df_uniques[df_uniques["DISEASE"] == "Obesity"]["NATIONALITY"].value_counts().reset_index()

        local = int(local_diseases[local_diseases["NATIONALITY"] == "Local"]["count"])
        foreigner = int(local_diseases[local_diseases["NATIONALITY"] == "Foreigner"]["count"])

        age_diseases = df_uniques[df_uniques["DISEASE"] == "Obesity"][["AGE_GROUP"]]
        age_diseases["AGE_GROUP"] = age_diseases["AGE_GROUP"].apply(lambda x : "Underage" if x == "10-19" else "Adult")
        age_diseases = age_diseases.value_counts().reset_index()

        underage = int(age_diseases[age_diseases["AGE_GROUP"] == "Underage"]["count"])
        adult = int(age_diseases[age_diseases["AGE_GROUP"] == "Adult"]["count"])

        data = {
            "Category": ["Male", "Female", "Local", "Foreigner", "Underage", "Adult"],
            "Value": [male, female, local, foreigner, underage, adult]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)



    with c2:
        a=df_uniques[df_uniques["DISEASE"] == "Obesity"].groupby(['GENDER', 'AGE_GROUP']).size().reset_index()
        a.columns = ["GENDER", "AGE_GROUP", "COUNT"]
        a['RANK'] = a['COUNT'].rank(method='min', ascending=False)

            # Creating a tree map with a hot scale color
        tree_map = alt.Chart(a).mark_rect().encode(
        y=alt.Y('GENDER:N', title=''),
        x=alt.X('AGE_GROUP:N', title='', axis=alt.Axis(labelAngle=0)),
        color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Count', legend=None),
        size='COUNT:Q',
        tooltip=[alt.Tooltip('COUNT:Q', title='Counts', format = ",")]).properties(
        height=500,
    )
        
        txt = alt.Chart(a).mark_text(fontSize=30, fontWeight='bold', color='white').transform_filter(alt.datum.RANK <= 5).encode(
            y=alt.Y('GENDER:N', title=''),
            x=alt.X('AGE_GROUP:N', title=''),
            text=alt.Text('RANK:N')
        )

        st.altair_chart((tree_map+txt).properties(width='container', height=290), use_container_width=True)
    
# Adapt code
st.button("Export Data", type="primary")

