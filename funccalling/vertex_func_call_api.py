#https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/use_case_company_news_and_insights.ipynb

import os
from dotenv import load_dotenv

load_dotenv()

#%pip install --upgrade --quiet google-cloud-aiplatform requests
import vertexai

#vertexai.init(project=PROJECT_ID, location=LOCATION)
vertexai.init()

import requests
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

get_stock_price = FunctionDeclaration(
    name="get_stock_price",
    description="Fetch the current stock price of a given company",
    parameters={
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol for a company",
            }
        },
    },
)

get_company_overview = FunctionDeclaration(
    name="get_company_overview",
    description="Get company details and other financial data",
    parameters={
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol for a company",
            }
        },
    },
)

get_company_news = FunctionDeclaration(
    name="get_company_news",
    description="Get the latest news headlines for a given company.",
    parameters={
        "type": "object",
        "properties": {
            "tickers": {
                "type": "string",
                "description": "Stock ticker symbol for a company",
            }
        },
    },
)

get_news_with_sentiment = FunctionDeclaration(
    name="get_news_with_sentiment",
    description="Gets live and historical market news and sentiment data",
    parameters={
        "type": "object",
        "properties": {
            "news_topic": {
                "type": "string",
                "description": """News topic to learn about. Supported topics
                               include blockchain, earnings, ipo,
                               mergers_and_acquisitions, financial_markets,
                               economy_fiscal, economy_monetary, economy_macro,
                               energy_transportation, finance, life_sciences,
                               manufacturing, real_estate, retail_wholesale,
                               and technology""",
            },
        },
    },
)

company_insights_tool = Tool(
    function_declarations=[
        get_stock_price,
        get_company_overview,
        get_company_news,
        get_news_with_sentiment,
    ],
)



# API key for company and financial information
#https://www.alphavantage.co/support/#api-key
API_KEY = os.getenv("API_KEY")

def get_stock_price_from_api(content):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={content['ticker']}&apikey={API_KEY}"
    api_request = requests.get(url)
    return api_request.text


def get_company_overview_from_api(content):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={content['ticker']}&apikey={API_KEY}"
    api_response = requests.get(url)
    return api_response.text


def get_company_news_from_api(content):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={content['tickers']}&limit=20&sort=RELEVANCE&apikey={API_KEY}"
    api_response = requests.get(url)
    return api_response.text


def get_news_with_sentiment_from_api(content):
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics={content['news_topic']}&limit=20&sort=RELEVANCE&apikey={API_KEY}"
    api_request = requests.get(url)
    return api_request.text

function_handler = {
    "get_stock_price": get_stock_price_from_api,
    "get_company_overview": get_company_overview_from_api,
    "get_company_news": get_company_news_from_api,
    "get_news_with_sentiment": get_news_with_sentiment_from_api,
}

gemini_model = GenerativeModel(
    "gemini-1.5-pro-002",
    generation_config=GenerationConfig(temperature=0),
    tools=[company_insights_tool],
)


chat = gemini_model.start_chat()


from IPython.display import Markdown, display

def send_chat_message(prompt):
    display(Markdown("#### Prompt"))
    print(prompt, "\n")
    prompt += """
    Give a concise, high-level summary. Only use information that you learn from 
    the API responses. 
    """

    # Send a chat message to the Gemini API
    response = chat.send_message(prompt)

    # Handle cases with multiple chained function calls
    function_calling_in_process = True
    while function_calling_in_process:
        # Extract the function call response
        print(response)
        function_call = response.candidates[0].content.parts[0].function_call
        if not function_call:
            break

        print(function_call)

        # Check for a function call or a natural language response
        if function_call.name in function_handler.keys():
            # Extract the function call name
            function_name = function_call.name
            display(Markdown("#### Predicted function name"))
            print(function_name, "\n")

            # Extract the function call parameters
            params = {key: value for key, value in function_call.args.items()}
            display(Markdown("#### Predicted function parameters"))
            print(params, "\n")

            # Invoke a function that calls an external API
            function_api_response = function_handler[function_name](params)[
                :20000
            ]  # Stay within the input token limit
            display(Markdown("#### API response"))
            print(function_api_response[:500], "...", "\n")
            print(f"function_name:{function_name}")

            # Send the API response back to Gemini, which will generate a natural language summary or another function call
            response = chat.send_message(
                Part.from_function_response(
                    name=function_name,
                    response={"content": function_api_response},
                ),
            )
        else:
            function_calling_in_process = False

    # Show the final natural language summary
    display(Markdown("#### Natural language response"))
    display(Markdown(response.text.replace("$", "\\$")))

#send_chat_message("What is the current stock price for Google?")
#send_chat_message("Give me a company overview of Google")
#send_chat_message("What are the latest news headlines for Google?")
#send_chat_message("Give me a company overview of Walmart and The Home Depot")
send_chat_message("Has there been any exciting news related to real estate recently?")