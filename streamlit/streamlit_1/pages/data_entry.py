import streamlit as st

def app():
    st.title("Data Entry")
    st.write("Enter your data here:")

    name = st.text_input("Name:")
    age = st.number_input("Age:", min_value=0)

    if st.button("Submit"):
        if name and age:
            st.write(f"Name: {name}, Age: {age}")
        else:
            st.warning("Please fill in all fields.")