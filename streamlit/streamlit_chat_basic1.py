import streamlit as st


def build_form(message):
    body = message["body"]
    params = message["content"]
    with st.chat_message("assistant"):
            with st.form(key="form"):
                for name, value in params.items():
                    params[name] = st.text_input(label=name, value=value, key=name)
                st.form_submit_button("Submit", on_click=save_form, args=[params, body])

def save_form(params, body):
    {key: st.session_state[key] for key in params.keys()}
    with st.chat_message("user"):
        st.write(f"Form submitted with data: {params}")

# Display a chat message
with st.chat_message("user"):
    st.write("Hello, world!")

# Capture user input
prompt = st.chat_input("Your message:")
if prompt:
    if prompt.lower() == "show form":
    # Process and display the input message
        message = {
            "body": "This is the body of the request",
            "content": {
                "name": "John Doe",
                "email": "john@gmail.com"
            }
        }
        build_form(message)
    else:
        with st.chat_message("assistant"):
            st.write(f"You said: {prompt}")
