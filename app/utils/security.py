import streamlit as st
from PIL import Image

def password_entered():
    """Checks whether a password entered by the user is correct."""

    if st.session_state["password"] == st.secrets["login"]["LOGIN_PASSWORD"]: #error point to this line!
        st.session_state["password_correct"] = True
        del st.session_state["password"]  # don't store password
    else:
        st.session_state["password_correct"] = False

#adding a login page
def check_password():
    """Returns `True` if the user had the correct password."""

    if "password_correct" not in st.session_state:

        st.header(":green[*Analytics*] Survey Automation Tools")
        image = Image.open('module/photos/invoke_logo.png')
        st.image(image)
        st.text_input(
        "Please enter your password", type="password", on_change=password_entered, key="password"
        )
        return False
    
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Please enter your password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False

    else:
        # Password correct.
        return True
