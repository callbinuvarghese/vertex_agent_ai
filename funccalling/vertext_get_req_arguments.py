import streamlit as st
import re
from loguru import logger
import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
# ... other imports

import os
from dotenv import load_dotenv

load_dotenv()

# ... (function definitions, get_tools, etc.)


params_data_types = {
    "user_id": {"type": "integer", "maxlength": 4,"description":"The user's unique identification number."},  # Assuming max 10 digits for user ID
    "order_id": {"type": "integer", "maxlength": 4,"description":"The order's unique identification number."},  # Assuming max 12 digits for order ID
    "current_date": {"type": "date", "maxlength": 10,"description":"The current date in YYYY-MM-DD format."},  # YYYY-MM-DD format is always 10 characters
    "action": {"type": "string", "maxlength": 6,"description":"The action the user wants to perform which is one of: 'status', 'cancel', 'return'."},  # Longest possible action is 'return' (6 chars)
}
REQUIRED_PARAMS = params_data_types.keys()
#REQUIRED_PARAMS = ["user_id", "order_id", "current_date", "action"]  # Your four required parameters
system_instruction =f"""You are a store support API assistant. You will collect the following information from the user to perform tasks:
                      params in {params_data_types} 
                      The user will provide the information in natural language.
                      """
                      
params_prompts = {
    "user_id": "Please provide your user ID (a whole number):",
    "order_id": "Please provide your order ID (a whole number):",
    "current_date": "Please provide the current date (in YYYY-MM-DD format):",
    "action": "Please specify the action you want to perform ('status', 'cancel', or 'return'):",
    }

# Initialize Vertex AI
vertexai.init()
# Initialize Gemini model
#model_name='gemini-2.0-flash-exp'
model_name="gemini-pro"
#model_name='gemini-1.5-flash-001'
#model = GenerativeModel(model_name, system_instruction=system_instruction)
model = GenerativeModel(model_name)


def your_api_function(params):
    logger.info("Calling your API with parameters: %s", params)
    return "API response"
def missing_params_to_csv(missing_params):
    """Convert missing parameters array to quoted CSV string"""
    return ','.join([f'"{param}"' for param in missing_params])
def get_missing_params(extracted_params):
     missing_params = [param for param in REQUIRED_PARAMS if param not in extracted_params]
     return missing_params
def get_user_prompt_for_missing_params(missing_params):
    prompt = f"I need the following information to proceed:\n" + "\n".join([params_prompts[param] for param in missing_params])
    return prompt

def process_user_input(user_prompt, message_history):
    logger.info(f"Processing user input: {user_prompt}")
    user_prompt_content = Content(role="user", parts=[Part.from_text(user_prompt)])
    message_history.append(user_prompt_content)

    extracted_params = st.session_state.get("extracted_params", {})  # Get existing params

# Updated regex patterns for natural language extraction
    param_patterns = {
        "user_id": r"(?:user(?:\s+)?id(?:\s+)?(?:is|:)?(?:\s+)?|uid(?:\s+)?(?:is|:)?(?:\s+)?)([A-Za-z0-9]+)",
        "order_id": r"(?:order(?:\s+)?(?:id|number)(?:\s+)?(?:is|:)?(?:\s+)?|oid(?:\s+)?(?:is|:)?(?:\s+)?)([A-Za-z0-9]+)",
        "current_date": r"(?:date(?:\s+)?(?:is|:)?(?:\s+)?|current(?:\s+)?date(?:\s+)?(?:is|:)?(?:\s+)?)(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})",
        "action": r"(?:action(?:\s+)?(?:is|:)?(?:\s+)?|i(?:\s+)?want(?:\s+)?to(?:\s+)?)(\b(?:cancel|refund|check status)\b)"
    }

    # Extract parameters using the new patterns
    for param_name, pattern in param_patterns.items():
        if param_name not in extracted_params:  # Only extract if not already present
            match = re.search(pattern, user_prompt, re.IGNORECASE)
            if match:
                extracted_params[param_name] = match.group(1).strip()

    logger.info(f"extracted_params: {extracted_params}")
    st.session_state.extracted_params = extracted_params
    message_history.append(Content(role="user", parts=[Part.from_text(f"Extracted parameters: {extracted_params}")]))

    #message_history.append(Content(role="system", parts=[Part.from_text(f"Extracted parameters: {extracted_params}")]))

    if all(param in extracted_params for param in REQUIRED_PARAMS):
        # All required parameters are collected! Call the API.
        logger.info("All parameters collected. Calling API...")
        try:
            # Instead of adding system message, include API response in user message
            user_context = f"API call made with parameters: {extracted_params}"
            message_history.append(Content(role="user", parts=[Part.from_text(user_context)]))
            response = model.generate_content(message_history, generation_config=GenerationConfig(temperature=0))
            final_response = response.text
            st.session_state.extracted_params = {}
        except Exception as e:
            logger.error(f"API Error: {e}")
            final_response = f"An error occurred: {e}"
    else:
        logger.info("Not all required parameters are collected. Prompting user for missing parameters.")
        # Prompt for missing parameters
        missing_params = get_missing_params(extracted_params)
        prompt = f"I need the following information to proceed: {missing_params_to_csv(missing_params)}."
        message_history.append(Content(role="model", parts=[Part.from_text(prompt)]))
        logger.info("Current message history:")
        for idx, message in enumerate(message_history):
            logger.info(f"Message {idx}: Role={message.role}, Content={message.parts[0].text}")

        #response = model.generate_content(message_history, generation_config=GenerationConfig(temperature=0), tools=[support_tool])
       
        response = model.generate_content(message_history, generation_config=GenerationConfig(temperature=0))
        final_response = response.text

    return final_response, message_history

def get_user_input(extracted_params):
    """
    Gets user input from the Streamlit interface
    """
    #user_prompt = st.text_input("I am going to help you with your API call. Please provide the necessary information.")
    # Prompt for missing parameters
    missing_params = get_missing_params(extracted_params)
    prompt = f"I need the following information to proceed: {', '.join(missing_params)}."
    user_prompt = get_user_prompt_for_missing_params(missing_params)

    return user_prompt

def main():
    st.title("API Task Chatbot")

    # Initialize session state
    if "message_history" not in st.session_state:
        #st.session_state.message_history = [Content(role="user", parts=[Part.from_text("You are a helpful assistant to collect parameters for API calls."), Part.from_text(system_instruction)])]
        st.session_state.message_history = [Content(role="user", parts=[
            Part.from_text(system_instruction)
        ])]
    if "extracted_params" not in st.session_state:
        st.session_state.extracted_params = {}

    # Get missing parameters
    missing_params = get_missing_params(st.session_state.extracted_params)
    
    # Create the text input for user
    user_input = st.text_input(st.session_state.message_history[-1].parts[0].text, key="user_input")

    # Process user input when submitted
    if user_input:
        response, st.session_state.message_history = process_user_input(user_input, st.session_state.message_history)
        st.write("Assistant:", response)

    # Display chat history
    st.write("Chat History:")
    for msg in st.session_state.message_history:
        st.write(f"{msg.role.capitalize()}: {msg.parts[0].text}")

if __name__ == "__main__":
    main()