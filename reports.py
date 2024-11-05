# reports.py
import openai
import os
import pandas as pd
import json

# 5. Additional Functions for CSV Saving

def create_reports_directory(directory_name: str = "stock_reports"):
    """Creates a directory to store CSV reports."""
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    return directory_name

def load_reports_from_json():
    # Load the JSON file as a dictionary
    with open("stock_reports/reports.json", "r") as json_file:
        reports = json.load(json_file)
    return reports

def save_reports_as_csv(reports: dict, directory: str):
    """
    Saves different sections of stock reports into separate CSV files.
    
    Args:
        reports (dict): Dictionary containing reports for each ticker.
        directory (str): Directory where CSV files will be saved.
    """
    # Save the combined reports
    with open(f"{directory}/reports.json", "w") as json_file:
        json.dump(reports, json_file, indent=4)  # indent=4 for pretty-printing

    # Initialize dictionaries to hold data for each CSV
    basic_info_dict = {}
    fundamental_analysis_dict = {}
    technical_analysis_dict = {}
    risk_assessment_dict = {}
    recent_news_list = []

    for ticker, data in reports.items():
        # Basic Information
        basic_info = data.get('basic_info', {})
        if basic_info:
            basic_info['Ticker'] = ticker
            basic_info_dict[ticker] = basic_info

        # Fundamental Analysis
        fundamental = data.get('fundamental_analysis', {})
        if fundamental:
            fundamental['Ticker'] = ticker
            fundamental_analysis_dict[ticker] = fundamental

        # Technical Analysis
        technical = data.get('technical_analysis', {})
        if technical:
            technical['Ticker'] = ticker
            technical_analysis_dict[ticker] = technical

        # Risk Assessment
        risk = data.get('risk_assessment', {})
        if risk:
            risk['Ticker'] = ticker
            risk_assessment_dict[ticker] = risk

        # Recent News
        news = data.get('news', [])
        for article in news:
            news_entry = {
                'Ticker': ticker,
                'Published': article.get('Published', 'N/A'),
                'Title': article.get('Title', 'N/A'),
                'Publisher': article.get('Publisher', 'N/A'),
                'Link': article.get('Link', 'N/A')
            }
            recent_news_list.append(news_entry)

    # Convert dictionaries to DataFrames and save as CSV
    if basic_info_dict:
        basic_info_df = pd.DataFrame.from_dict(basic_info_dict, orient='index')
        basic_info_df.to_csv(os.path.join(directory, 'basic_info.csv'), index=False)

    if fundamental_analysis_dict:
        fundamental_df = pd.DataFrame.from_dict(fundamental_analysis_dict, orient='index')
        fundamental_df.to_csv(os.path.join(directory, 'fundamental_analysis.csv'), index=False)

    if technical_analysis_dict:
        technical_df = pd.DataFrame.from_dict(technical_analysis_dict, orient='index')
        technical_df.to_csv(os.path.join(directory, 'technical_analysis.csv'), index=False)

    if risk_assessment_dict:
        risk_df = pd.DataFrame.from_dict(risk_assessment_dict, orient='index')
        risk_df.to_csv(os.path.join(directory, 'risk_assessment.csv'), index=False)

    if recent_news_list:
        news_df = pd.DataFrame(recent_news_list)
        news_df.to_csv(os.path.join(directory, 'recent_news.csv'), index=False)

def generate_stock_report(ticker: str, data: dict) -> str:
    """Generates a stock report using all gathered information."""
    report = f"# Stock Report for {data['basic_info'].get('Name', 'N/A')} ({ticker})\n\n"

    report += "## Basic Information:\n"
    for key, value in data['basic_info'].items():
        report += f"- **{key}**: {value}\n"
    report += "\n"

    report += "## Fundamental Analysis:\n"
    for key, value in data['fundamental_analysis'].items():
        report += f"- **{key}**: {value}\n"
    report += "\n"

    report += "## Technical Analysis:\n"
    for key, value in data['technical_analysis'].items():
        report += f"- **{key}**: {value}\n"
    report += "\n"

    report += "## Risk Assessment:\n"
    for key, value in data['risk_assessment'].items():
        report += f"- **{key}**: {value}\n"
    report += "\n"

    report += "## Recent News:\n"
    if data['news']:
        for article in data['news']:
            report += f"- **{article['Published']}** - {article['Title']} ({article['Publisher']})\n"
            report += f"  [Read more]({article['Link']})\n"
    else:
        report += "No recent news available.\n"
    report += "\n"

    return report

def identify_best_stock_with_llm(reports: dict) -> str:
    """Uses OpenAI's LLM to determine the best performing stock based on reports."""
    # Compile the reports into a readable format
    compiled_reports = ""
    for ticker, data in reports.items():
        compiled_reports += f"### {ticker} - {data['basic_info'].get('Name', 'N/A')}\n\n"
        compiled_reports += f"**Basic Information:**\n"
        for key, value in data['basic_info'].items():
            compiled_reports += f"- {key}: {value}\n"
        compiled_reports += "\n"

        compiled_reports += f"**Fundamental Analysis:**\n"
        for key, value in data['fundamental_analysis'].items():
            compiled_reports += f"- {key}: {value}\n"
        compiled_reports += "\n"

        compiled_reports += f"**Technical Analysis:**\n"
        for key, value in data['technical_analysis'].items():
            compiled_reports += f"- {key}: {value}\n"
        compiled_reports += "\n"

        compiled_reports += f"**Risk Assessment:**\n"
        for key, value in data['risk_assessment'].items():
            compiled_reports += f"- {key}: {value}\n"
        compiled_reports += "\n"

        compiled_reports += f"**Recent News:**\n"
        if data['news']:
            for article in data['news']:
                compiled_reports += f"- {article['Published']} - {article['Title']} ({article['Publisher']})\n"
                compiled_reports += f"  [Read more]({article['Link']})\n"
        else:
            compiled_reports += "No recent news available.\n"
        compiled_reports += "\n\n"

    # Prepare the prompt for the LLM
    prompt = f"""
            Based on the following stock reports, determine which stock is the best performing over the last 30 days. Provide a detailed reasoning for your choice.

            {compiled_reports}

            Please specify:
            1. The best performing stock among the specified stocks; you need to strictly choose one stock from the given tickers.
            2. The reasons supporting your decision, referencing relevant data from the reports.
            """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst with expertise in stock performance evaluation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=500  # Adjust as needed
        )

        llm_response = response.choices[0].message.content.strip()
        # reports_directory = create_reports_directory()

        # Save reports as CSV files
        # save_reports_as_csv(reports, reports_directory)
        # print(f"\nAll reports have been saved to the '{reports_directory}' directory.")
        return llm_response

    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        return None
