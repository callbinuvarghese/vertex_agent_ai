#!pip install vertexai
#!pip install yfinance
#!pip install --upgrade --user --quiet google-cloud-aiplatform

import os
from dotenv import load_dotenv

load_dotenv()

import requests
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

get_product_info = FunctionDeclaration(
    name="get_product_info",
    description="Get the stock amount and identifier for a given product",
    parameters={
        "type": "object",
        "properties": {
            "product_name": {"type": "string", "description": "Product name"}
        },
    },
)

get_store_location = FunctionDeclaration(
    name="get_store_location",
    description="Get the location of the closest store",
    parameters={
        "type": "object",
        "properties": {"location": {"type": "string", "description": "Location"}},
    },
)

place_order = FunctionDeclaration(
    name="place_order",
    description="Place an order",
    parameters={
        "type": "object",
        "properties": {
            "product": {"type": "string", "description": "Product name"},
            "address": {"type": "string", "description": "Shipping address"},
        },
    },
)