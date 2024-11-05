# main.py

import os
import openai
import json
import re

from fastapi import FastAPI, Body, HTTPException
from typing import Dict
import uvicorn

from pydantic import BaseModel

from tools import get_top_performing_stocks
from Bgents import function_descriptions

from tools import (
    get_basic_stock_info,
    get_fundamental_analysis,
    get_technical_analysis,
    get_stock_risk_assessment,
    get_stock_news
)
from Bgents import functions, create_agent_prompt
from reports import (
    create_reports_directory,
    save_reports_as_csv,
    generate_stock_report,
    identify_best_stock_with_llm,
    load_reports_from_json  # Ensure this function is defined in reports.py
)

# Initialize FastAPI app
app = FastAPI()

# Set your OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise Exception("OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")

# Modify the extract_tickers function to accept a dictionary
def extract_tickers(company_to_ticker):
    # Directly return ticker symbols from the dictionary
    return list(company_to_ticker.values())

# Pydantic model for the response
class TickerMapping(BaseModel):
    company_name: str
    ticker_symbol: str

@app.get("/top-stocks", response_model=dict)
async def get_top_stocks():
    # Set up the messages
    messages = [
        {"role": "system", "content": "You are a helpful financial assistant."},
        {
            "role": "user",
            "content": (
                "For the top 10 stocks of the day, provide a dictionary where the key is the company name "
                "and the value is its ticker symbol. Use your internal knowledge to assign ticker symbols "
                "to the company names from the scraped content."
            ),
        },
    ]

    # Make the initial OpenAI API call using the updated method
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        functions=function_descriptions,
        function_call={"name": "get_top_performing_stocks"},  # Force the model to call the function
    )

    # Get the function call
    function_call = response.choices[0].message.function_call

    if function_call and function_call.name == 'get_top_performing_stocks':
        # Execute the function
        top_companies = get_top_performing_stocks()

        # Convert the result to a JSON string
        function_response = json.dumps(top_companies)

        # Add the assistant's message and the function response to the conversation
        messages.append({
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_call.name,
                "arguments": function_call.arguments,
            }
        })
        messages.append({
            "role": "function",
            "name": function_call.name,
            "content": function_response,
        })

        # Prepare the prompt
        mapping_prompt = (
                        f"Given the following list of company names: {top_companies}, "
                        "please provide their corresponding ticker symbols. "
                        "Output the result strictly in the format of a JSON dictionary, "
                        "where the key is the company name and the value is its ticker symbol. "
                        "Do not include any code block markers or Markdown syntax. "
                        "Only output the JSON dictionary, without any additional text or comments."
                    )


        # Add the mapping prompt to the messages
        messages.append({
            "role": "user",
            "content": mapping_prompt
        })

        # Get the final response from the model
        final_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        # Extract the assistant's reply
        assistant_reply = final_response.choices[0].message.content

        try:
            # Parse the assistant's reply as a dictionary
            ticker_mapping = json.loads(assistant_reply)
            return ticker_mapping
            # return assistant_reply
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse assistant's response.")
    else:
        # Handle the case where the model does not call the function
        assistant_reply = response.choices[0].message.content
        raise HTTPException(status_code=500, detail=f"Assistant did not call the function as expected. Response: {assistant_reply}")



# Endpoint 2: Process Stocks and Generate Reports
@app.post("/process_stocks")
def process_stocks(company_to_ticker: Dict[str, str] = Body(...)):
    # Extract tickers from the dictionary
    tickers = extract_tickers(company_to_ticker)
    if not tickers:
        return {"error": "No valid tickers found."}
    
    # Initialize storage for reports
    reports = {}
    
    # Process each ticker
    for ticker in tickers:
        print(f"\nProcessing {ticker}...")
        # Agent 1: Stock Researcher
        basic_info = get_basic_stock_info(ticker)
        if not basic_info or basic_info.get('Name') == 'N/A':
            print(f"Skipping {ticker} due to missing basic information.")
            continue
        reports[ticker] = {'basic_info': basic_info}
    
        # Agent 2: Financial Analyst
        fundamental = get_fundamental_analysis(ticker)
        technical = get_technical_analysis(ticker)
        risk = get_stock_risk_assessment(ticker)
        reports[ticker].update({
            'fundamental_analysis': fundamental,
            'technical_analysis': technical,
            'risk_assessment': risk
        })
    
        # Agent 3: News Analyst
        news = get_stock_news(ticker)
        reports[ticker]['news'] = news
    
        # Agent 4: Financial Report Writer
        report = generate_stock_report(ticker, reports[ticker])
        print(f"Report for {ticker}:\n{report}\n")
    
    reports_directory = create_reports_directory()
    # Save reports as CSV files
    save_reports_as_csv(reports, reports_directory)
    print(f"\nAll reports have been saved to the '{reports_directory}' directory.")
    
    return reports  # Return the report details for each ticker symbol

# Endpoint 3: Analyze Reports and Identify Best-Performing Stock
@app.post("/analyze_reports")
def analyze_reports():
    # Read reports from the reports directory
    # reports_directory = create_reports_directory()
    reports = load_reports_from_json()
    if not reports:
        return {"error": "No reports found in the directory."}
    
    best_stock_reasoning = identify_best_stock_with_llm(reports)
    return {"best_stock_reasoning": best_stock_reasoning}

# Main Workflow remains unchanged for backward compatibility
def main():
    # Define a mapping from company names to tickers
    # These Hard Coded values are just to test the main
    # We don't utilise these when we execute the endpoints -- Take it Just as a sample demo 
    company_to_ticker = {
       "Yahoo": "YHOO",
       "Apple": "AAPL",
       "Tesla": "TSLA",
       "Netflix": "NFLX",
       "NVIDIA": "NVDA",
       "Amazon": "AMZN"
   }

    # Extract tickers from the dictionary
    tickers = extract_tickers(company_to_ticker)
    if not tickers:
        print("No valid tickers found.")
        return
    
    # Initialize storage for reports
    reports = {}
    
    # Process each ticker
    for ticker in tickers:
        print(f"\nProcessing {ticker}...")
        # Agent 1: Stock Researcher
        basic_info = get_basic_stock_info(ticker)
        if not basic_info or basic_info.get('Name') == 'N/A':
            print(f"Skipping {ticker} due to missing basic information.")
            continue
        reports[ticker] = {'basic_info': basic_info}
    
        # Agent 2: Financial Analyst
        fundamental = get_fundamental_analysis(ticker)
        technical = get_technical_analysis(ticker)
        risk = get_stock_risk_assessment(ticker)
        reports[ticker].update({
            'fundamental_analysis': fundamental,
            'technical_analysis': technical,
            'risk_assessment': risk
        })
    
        # Agent 3: News Analyst
        news = get_stock_news(ticker)
        reports[ticker]['news'] = news
    
        # Agent 4: Financial Report Writer
        report = generate_stock_report(ticker, reports[ticker])
        print(f"Report for {ticker}:\n{report}\n")
    
    reports_directory = create_reports_directory()
    # Save reports as CSV files
    save_reports_as_csv(reports, reports_directory)
    print(f"\nAll reports have been saved to the '{reports_directory}' directory.")
    
    # Identify the best stock using LLM
    best_stock_reasoning = identify_best_stock_with_llm(reports)
    print(best_stock_reasoning)

if __name__ == "__main__":
    # Uncomment the following line to run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)        
    main()  # Or comment this line if you are running the FastAPI app