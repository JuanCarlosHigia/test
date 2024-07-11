import streamlit as st
import base64
from st_pages import hide_pages, Page, Section, show_pages, add_page_title
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
hide_pages(["Auth", "Introduction", "Disease Incidence & Prevalence", "Disease Risk Prediction", "Clinical Workflow Analysis", "Hospital Risk Prevention"])

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


# Inicializar estado de sesión si no está presente
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if username == "higiauser1" and password == "higia2024":
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
    else:
        st.error("Incorrect username or password")

# Botón de login
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in", type="primary"):
        login()
        st.switch_page("pages/1_▫️_Introduction.py")