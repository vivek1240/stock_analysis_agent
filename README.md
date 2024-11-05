# Stock Analysis Agentic Tool

## Overview
This Stock Analysis Tool provides an end-to-end solution for identifying, analyzing, and evaluating the top-performing stocks in the market. Leveraging a combination of custom AI agents powered by OpenAI’s API and data from Yahoo Finance and Google Custom Search, this tool systematically performs detailed stock analysis and generates comprehensive reports. The tool is designed for modular and extensible use through FastAPI endpoints, making it suitable for integration into larger applications.

## Primary Goals
- Identify the top-performing stocks in the market.
- Extract and analyze detailed data for each selected stock.
- Save and archive the analysis and reports in CSV format.
- Evaluate and determine the best-performing stock over a specified period (1–3 months) using AI-assisted analysis.

## Agents Overview
This tool does not rely on any external framework for its generative AI functionality. Instead, it defines custom agents directly through OpenAI API function calling, ensuring a tailored and controlled workflow. Each agent serves a specific purpose in the analysis pipeline.

## FastAPI Endpoints
The Stock Analysis Tool has three main endpoints:

### 1. Identify Top-Performing Stocks Endpoint
- **Purpose**: Identifies the top-performing stocks by querying Google Custom Search and using BeautifulSoup to scrape data from relevant pages.
- **Process**:
  - Executes a Google search query to fetch top-performing stocks.
  - Uses BeautifulSoup to parse HTML data from search results.
  - A custom agent interprets the data, using internal knowledge to assign ticker symbols to the company names.
  
Example agent setup:
```python
{
    "role": "system",
    "content": "You are a helpful financial assistant."
},
{
    "role": "user",
    "content": (
        "For the top 10 stocks of the day, provide a dictionary where the key is the company name "
        "and the value is its ticker symbol. Use your internal knowledge to assign ticker symbols "
        "to the company names from the scraped content."
    )
}
```
- **Output**: Provides a list of ticker symbols for the top-performing stocks.

### 2. Analyze Stock Data Endpoint
- **Purpose**: Performs detailed financial analysis on each identified stock by calling several custom agents for data gathering, analysis, and reporting.
- **Process**:
  - Collects essential data using Yahoo Finance.
  - Uses custom analysis functions, including fundamental, technical, and risk assessments.

#### Agents and Functions
- **Stock Researcher**: Gathers basic stock info.
- **Financial Analyst**: Conducts in-depth fundamental and technical analyses.
- **News Analyst**: Gathers recent news articles related to each stock.
- **Financial Report Writer**: Synthesizes data into a structured report.

Example functions used:
- `get_basic_stock_info`: Retrieves general stock information.
- `calculate_rsi(series, period=14)`: Calculates the Relative Strength Index.
- `get_technical_analysis`: Provides a summary of technical indicators.

- **Output Data Storage**:
  - `basic_info.csv`: Fundamental company details.
  - `fundamental_analysis.csv`: Financial metrics and ratios.
  - `technical_analysis.csv`: Technical indicators and trends.
  - `risk_assessment.csv`: Risk metrics.
  - `recent_news.csv`: News articles related to stocks.

### 3. Identify Best-Performing Stock Endpoint
- **Purpose**: Identifies the best-performing stock based on the analyses over the past 1–3 months.
- **Agent Definition**:
```python
{
    "role": "system",
    "content": "You are a financial analyst with expertise in stock performance evaluation."
},
{
    "role": "user",
    "content": "Based on the analyzed reports, determine the best-performing stock over the last 30 days and provide reasoning for your choice."
}
```
- **Process**: Analyzes performance indicators, risk metrics, and recent news to determine the top stock.

## Usage Example
1. Use the first endpoint to retrieve the top-performing stocks.
2. Call the second endpoint to perform in-depth analysis on each stock.
3. Use the third endpoint to identify the best stock among the analyzed ones.

### Example:
```python
company_to_ticker = {
    "Yahoo": "YHOO",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Netflix": "NFLX",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN"
}
```

## Security Considerations
- **API Key Management**: Ensure API keys for OpenAI and Google Custom Search are stored securely.
- **Data Privacy**: Adheres to privacy protocols, storing only stock-related information.

## Conclusion
This Stock Analysis Tool, powered by custom AI agents and external data sources, offers a structured and comprehensive approach to stock market analysis. With its modular endpoints covering stock identification, detailed analysis, and selection of the top stock, it provides a powerful tool for generating actionable market insights.
