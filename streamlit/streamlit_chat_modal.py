import streamlit as st
import re
from vertexai.generative_models import Content, Part
# ... other imports

# ... (model initialization, other functions)

REQUIRED_PARAMS = ["user_id", "order_id", "current_date", "action"]

def process_user_input(user_prompt, message_history):
    # ... (Existing prompt handling)

    if st.session_state.get("show_modal", False): #Check if modal is already open
        return process_modal_input(user_prompt, message_history)

    match = re.search(r"\bcapture\b", user_prompt, re.IGNORECASE) #Check if the user is asking to capture information
    if match:
        st.session_state.show_modal = True
        st.session_state.modal_message_history = message_history.copy() #Store the current message history
        st.session_state.extracted_params = {} #Reset the extracted parameters
        return "Please fill out the form.", message_history
    
    # ... (rest of the prompt handling)

def process_modal_input(user_prompt, message_history):
    extracted_params = st.session_state.get("extracted_params", {})

    for param_name in REQUIRED_PARAMS:
        if param_name not in extracted_params:
            match = re.search(rf"\b{param_name}\s*(.+)", user_prompt, re.IGNORECASE)
            if match:
                extracted_params[param_name] = match.group(1).strip()

    st.session_state.extracted_params = extracted_params

    if all(param in extracted_params for param in REQUIRED_PARAMS):
        st.session_state.show_modal = False
        message_history = st.session_state.modal_message_history #Restore the message history
        message_history.append(Content(role="model", parts=[Part.from_text(f"Collected information: {extracted_params}")]))
        st.session_state.extracted_params = {}
        return "Information collected. Returning to chat.", message_history
    else:
        missing_params = [param for param in REQUIRED_PARAMS if param not in extracted_params]
        prompt = f"Please provide the following: {', '.join(missing_params)}"
        return prompt, message_history

def main():
    st.title("Streamlit Chatbot with Modal")

    if "message_history" not in st.session_state:
        st.session_state.message_history = [Content(role="system", parts=[Part.from_text("You are a helpful assistant.")])]
    if "extracted_params" not in st.session_state:
        st.session_state.extracted_params = {}
    if "modal_message_history" not in st.session_state:
        st.session_state.modal_message_history = []

    user_prompt = st.text_input("Enter your message:")

    if user_prompt:
        response, st.session_state.message_history = process_user_input(user_prompt, st.session_state.message_history)
        st.write(response)

        if st.session_state.get("show_modal", False): #Show the modal after the model response
            with st.form(key='input_form'):
                for param in REQUIRED_PARAMS:
                    st.text_input(param, key=param)
                submit_button = st.form_submit_button(label='Submit')
            if submit_button:
                user_prompt = " ".join([f"{param} {st.session_state[param]}" for param in REQUIRED_PARAMS])
                response, st.session_state.message_history = process_modal_input(user_prompt, st.session_state.message_history)
                st.experimental_rerun() #Rerun the script to close the modal
        for message in st.session_state.message_history:
            st.write(f"{message.role}: {message.parts[0].text}")

if __name__ == "__main__":
    main()