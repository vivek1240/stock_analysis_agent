# agents.py

import openai
import json

# 3. Function Definitions for OpenAI

functions = [
    {
        "name": "get_basic_stock_info",
        "description": "Retrieves basic information about a single stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol."
                }
            },
            "required": ["ticker"],
            "additionalProperties": False
        }
    },
    {
        "name": "get_fundamental_analysis",
        "description": "Performs fundamental analysis on a given stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol."
                }
            },
            "required": ["ticker"],
            "additionalProperties": False
        }
    },
    {
        "name": "get_technical_analysis",
        "description": "Performs technical analysis on a given stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol."
                },
                "period": {
                    "type": "string",
                    "description": "Optional. The period over which to perform the analysis (e.g., '1mo', '2y'). Defaults to '2y'.",
                    "enum": ["1mo", "2y", "5y", "10y"],
                    "default": "2y"
                }
            },
            "required": ["ticker"],
            "additionalProperties": False
        }
    },
    {
        "name": "get_stock_risk_assessment",
        "description": "Performs a risk assessment on a given stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol."
                },
                "period": {
                    "type": "string",
                    "description": "Optional. The period over which to perform the risk assessment (e.g., '1mo', '1y'). Defaults to '1y'.",
                    "enum": ["1mo", "1y", "2y", "5y", "10y"],
                    "default": "1y"
                }
            },
            "required": ["ticker"],
            "additionalProperties": False
        }
    },
    {
        "name": "get_stock_news",
        "description": "Fetches recent news articles related to a specific stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol."
                },
                "limit": {
                    "type": "integer",
                    "description": "The number of news articles to fetch.",
                    "default": 5
                }
            },
            "required": ["ticker"],
            "additionalProperties": False
        }
    }
]

# Define the function schema for function calling
function_descriptions = [
    {
        "name": "get_top_performing_stocks",
        "description": "Retrieves the top 10 best-performing stocks for today and returns a list of their company names.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    }
]

# 4. Agent Roles and Prompts

def create_agent_prompt(agent_role, goal, backstory):
    return f"""
            You are acting as a {agent_role}.
            Your goal is to {goal}.
            Backstory: {backstory}.
            """
