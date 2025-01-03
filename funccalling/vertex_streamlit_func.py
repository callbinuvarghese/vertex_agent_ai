import streamlit as st

# Import libraries from the original code
import requests
import vertexai
import loguru as logger

from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

import os
from dotenv import load_dotenv

load_dotenv()

def get_my_orders(args):    
    user_id = args.get("user_id")
    logger.info("get_my_orders:User ID: {user_id}")
    # Simulated response
    return {
        "user_id": user_id,
        "orders": [
            {
                "order_id": "1234",
                "status": "Shipped",
                "expected_delivery": "Next Friday"
            },
            {
                "order_id": "5678",
                "status": "Active",
                "expected_delivery": "Two weeks from now"
            },
            {
                "order_id": "9876",
                "status": "Cancelled by user",
                "expected_delivery": "Two weeks from now"
            },
            {
                "order_id": "5432",
                "status": "Fullfilled",
                "expected_delivery": "Delivered"
            },
        ]
    }

# Define dummy functions for each operation
def get_order_status(args):
    order_id = args.get("order_id")
    logger.info("get_order_status:Order ID: {order_id}")
    # Simulated response
    if order_id == "1234":
        return {
            "order_id": order_id,
            "shipping_status": "Shipped",
            "expected_delivery": "Next Friday",
            "status": "InProgress"
        }
    else:
        return {
            "order_id": order_id,
            "shipping_status": "Not Shipped",
            "expected_delivery": "Two weeks from now",
            "status": "Active"
        }

def initiate_return(args):
    order_id = args.get("order_id")
    reason = args.get("reason", "No reason provided")
    logger.info("initiate_return:Order ID: {order_id}, Reason: {reason}")
    
    if get_order_status(order_id)["shipping_status"] == "Shipped":   
        return {
            "order_id": order_id,
            "return_status": "Cannot initiate return as the order is already shipped"
        }
    else:
        # Simulated response
        return {
            "order_id": order_id,
            "return_status": "Return initiated successfully.",
            "return_label": "You will receive a return label shortly."
        }

def cancel_order(args):
    order_id = args.get("order_id")
    # Simulated response
    logger.info("initiate_return:Order ID: {order_id}")
    if get_order_status(order_id)["shipping_status"] == "Shipped":   
        return {
            "order_id": order_id,
            "status": "Cannot cancel the order as it is already shipped."
        }
    else:
        return {
            "order_id": order_id,
            "status": "Cancelled"
        }

def get_tools():

    
    # Define the function declarations
    get_my_orders_func = FunctionDeclaration(
        name="get_my_orders",
        description="Retrieve the current order details for the giver user ID. List of all the orders for the given user ID is returned. Returns all the orders and the latest list of order for user ID along with status of order. It lists the orders for the provided user ID. The order list contains the  order ID, status of the order and the expected delivery date.",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The unique identifier User ID of the user."
                }
            },
            "required": ["user_id"]
        },
    )

    # Define the function declarations
    get_order_status_func = FunctionDeclaration(
        name="get_order_status",
        description="Retrieve the current status of an order by its order ID.",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The unique identifier of the order."
                }
            },
            "required": ["order_id"]
        },
    )

    initiate_return_func = FunctionDeclaration(
        name="initiate_return",
        description="Initiate a return process for a given order ID.",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The unique identifier of the order to be returned."
                }
            },
            "required": ["order_id"]
        },
    )

    cancel_order_func = FunctionDeclaration(
        name="cancel_order",
        description="Cancel the order if the order exists by its order ID and if the order is not shipped yet.",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The unique identifier of the order."
                }
            },
            "required": ["order_id"]
        },
    )
    # Define the tools that include the above functions
    support_tool = Tool(
        function_declarations=[get_order_status_func, initiate_return_func, cancel_order_func],
    )

    function_handlers = {
        "get_my_orders_func": get_my_orders,
        "get_order_status": get_order_status,
        "initiate_return": initiate_return,
        "cancel_order": cancel_order,
    }
    return support_tool, function_handlers


def get_model_response(model, api_response, user_prompt_content, function_call, resp_content):
     # Return the dummy API response to Gemini so it can generate a model response or request another function call
    print(f"get_model_response; API Response: {api_response}")
    print(f"get_model_response; User Prompt: {user_prompt_content}")
    print(f"get_model_response; Function Call: {function_call.name}")
    print(f"get_model_response; Response Content: {resp_content}")

    response = model.generate_content(
        [
            user_prompt_content,  # User prompt
            resp_content,  # Function call response
            Content(
                parts=[
                    Part.from_function_response(
                        name=function_call.name,
                        response={"content": api_response},  # Return the dummy API response to Gemini
                    ),
                ],
            ),
        ],
        tools=[support_tool],
    )
    
    print(f"get_model_response; response: {response}")
    return response

support_tool, function_handlers = get_tools()
# Initialize Vertex AI
vertexai.init()
# Initialize Gemini model
model = GenerativeModel("gemini-1.5-flash-001",
                        system_instruction=["""You are a store support API assistant to help with online orders. Ask the user to provide their user ID to get started. Ask them to provide the order identifier to get order status. Ask for the order id, if they need to cancel or refund the order""",])



def get_user_input():
    """
    Gets user input from the Streamlit interface
    """
    user_prompt = st.text_input("Ask me anything about your orders:")
    return user_prompt

def process_user_input(user_prompt):
    """
    Processes the user input and calls the relevant function
    """
    user_prompt_content = Content(
        role="user",
        parts=[Part.from_text(user_prompt)],
    )
    
    # Send the prompt and instruct the model to generate content
    response = model.generate_content(
        user_prompt_content,
        generation_config=GenerationConfig(temperature=0),
        tools=[support_tool],
    )
    print(f"Response: {response}")
    
    # Process function calls and generate response
    final_response = ""
    if (response.candidates[0].function_calls):
        for function_call in response.candidates[0].function_calls:

            function_name = function_call.name
            print(f"Function Name: {function_name}")
            args = {key: value for key, value in function_call.args.items()}
            print(f"Arguments: {args}")

            if function_name in function_handlers:
                # Call the appropriate function with the extracted arguments
                try:
                    print(f"API Calling..: {function_name}")
                    api_response = function_handlers[function_name](args)
                    print(f"API Response: {api_response}")
                    resp_content=response.candidates[0].content
                    response=get_model_response(model, api_response, user_prompt_content, function_call, resp_content)   # Get the model response and print it
                    print(f"Model Response: {response.text}")
                    final_response += response.text
                except Exception as e:
                    print(f"API Error: {e}")
            else:
                final_response += f"Unknown function {function_name}"
    else:
        final_response += response.text
    return final_response


def main():
  """
  Main function for the Streamlit app
  """
  st.title("Store Support Chatbot")
  user_prompt = get_user_input()

  
  if user_prompt:
    response = process_user_input(user_prompt)
    st.write(response)

if __name__ == "__main__":
  main()