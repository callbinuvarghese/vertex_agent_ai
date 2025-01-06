#pip install streamlit_option_menu
#pip install streamlit

import streamlit as st
from streamlit_option_menu import option_menu

def home_page():
    st.title("Home Page")
    st.write("Welcome to the home page!")

def page2():
    st.title("Page 2")
    st.write("This is page 2.")

def main():
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Page 2"],
        icons=["house", "book"],  # Optional icons
        menu_icon="cast",  # Optional menu icon
        default_index=0,  # Optional default index
        orientation="vertical",
    )

    if selected == "Home":
        home_page()
    elif selected == "Page 2":
        page2()

if __name__ == "__main__":
    main()