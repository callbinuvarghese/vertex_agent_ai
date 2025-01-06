import streamlit as st
import pages.home as home
import pages.data_entry as data_entry
import pages.analysis as analysis
import pages.order_status as order_status
import utils  # If you have utility functions

PAGES = {
    "Home": home,
    "Data Entry": data_entry,
    "Order Status": order_status,
    "Analysis": analysis,
}

def main():
    st.set_page_config(page_title="My Streamlit App")

    # Sidebar navigation
    #selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    selection = st.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]
    page.app()  # Call the app() function of the selected page

if __name__ == "__main__":
    main()