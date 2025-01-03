
import os
from dotenv import load_dotenv

load_dotenv()

# ... (function definitions as before)
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Define functions as dictionaries
# Define functions using the Tool class with function_declarations
tools = Tool(function_declarations=[
    FunctionDeclaration(
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. 'San Francisco, CA'"
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    ),
    FunctionDeclaration(
        "name": "get_latest_news",
        "description": "Get the latest news headlines about a specific topic",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to search for news about"
                }
            },
            "required": ["topic"],
        },
    ),
    FunctionDeclaration(
        "name": "perform_calculation",
        "description": "Performs a simple arithmetic calculation",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The operation to perform (+, -, *, /)"
                },
                "num1": {
                    "type": "number",
                    "description": "The first number"
                },
                "num2": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["operation", "num1", "num2"],
        },
    ),
])

# Placeholder implementations
def get_current_weather(location, unit="fahrenheit"):
    """Placeholder implementation for get_current_weather."""
    return f"The weather in {location} is currently sunny and 70 {unit} (This is a fake result)"

def get_latest_news(topic):
    """Placeholder implementation for get_latest_news."""
    return f"Here are the latest headlines about {topic}: (These are fake news)"

def perform_calculation(operation, num1, num2):
    """Placeholder implementation for perform_calculation."""
    try:
        num1 = float(num1)
        num2 = float(num2)
        if operation == "+":
            result = num1 + num2
        elif operation == "-":
            result = num1 - num2
        elif operation == "*":
            result = num1 * num2
        elif operation == "/":
            result = num1 / num2
        else:
            return "Invalid operator"
        return str(result)
    except ValueError:
        return "Invalid number input"
    except ZeroDivisionError:
        return "Division by zero is not allowed"

# Model Initialization
model = GenerativeModel("gemini-pro", 
                        generation_config={"temperature": 0},
                        tools=[tools])
chat = model.start_chat()
# Send a prompt to the chat
prompt = "What's the weather like in London and give me news about AI and what is 5 times 7?"
response = chat.send_message(prompt)
print("Chat Response:", response)


# Parse function calls
if ai_message.additional_kwargs and "function_call" in ai_message.additional_kwargs:
    function_calls = [ai_message.additional_kwargs["function_call"]]
    while "function_call" in function_calls[-1]:
        messages.append(ai_message)
        arguments = json.loads(ai_message.additional_kwargs["function_call"]["arguments"])
        function_name = ai_message.additional_kwargs["function_call"]["name"]
        if function_name == "get_current_weather":
            function_result = get_current_weather(**arguments)
        elif function_name == "get_latest_news":
            function_result = get_latest_news(**arguments)
        elif function_name == "perform_calculation":
            function_result = perform_calculation(**arguments)
        else:
            function_result = f"Unknown function {function_name}"
        messages.append(SystemMessage(content=function_result))
        ai_message = llm.invoke(messages, functions=functions)
        function_calls.append(ai_message.additional_kwargs["function_call"])
        print(ai_message)
        if "function_call" not in ai_message.additional_kwargs:
            print(ai_message.content)
            break
else:
    print(ai_message.content)