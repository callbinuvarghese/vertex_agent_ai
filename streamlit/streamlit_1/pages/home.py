import streamlit as st
import utils  # If you use utility functions
import pages.data_entry as data_entry

def app():
    st.title("Home Page")
    st.write("Welcome to the home page!")

    if st.button("Do something"):
        result = utils.some_utility_function("some input")
        st.write(f"Result from utility function: {result}")

    if st.button("Go to Data Entry"):
        data_entry.app()
