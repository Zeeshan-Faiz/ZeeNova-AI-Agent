from langchain_core.tools import Tool, StructuredTool
from tools.tool_functions import (
    get_current_time,
    search_wikipedia,
    serpapi_search,
    get_stock_price,
    get_weather,
    convert_currency,
    search_youtube_videos,
    e_commerce_search,
    lookup_indian_holidays,
    get_train_live_status,
    get_pnr_status,
    TrainStatusInput,
    get_flight_status,
    get_fd_rates,
    search_recharge_plans
)

tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when you need to know the current time.",
    ),
    Tool(
        name="Wikipedia",
        func=search_wikipedia,
        description="Use this tool to look up general knowledge or facts about people, places or topics using Wikipedia.",
    ),
    Tool(
        name="Google Search",
        func=serpapi_search,
        description="Use this tool for general web searches, news, events, or when no specific product listing is needed or anything that Wikipedia cannot answer.",
    ),
    Tool(
        name="Stock Price Checker",
        func=get_stock_price,
        description="Use this tool to get real-time stock prices. Input should be a company ticker symbol like 'TSLA' or 'AAPL'.",
    ),
    Tool(
        name="Weather",
        func=get_weather,
        description="Use this tool to check the current weather of a city. Input should be a city name like 'Mumbai' or 'New York' or using the IP of the user to detect location automatically.",
    ),
    Tool(
        name="Currency Converter",
        func=convert_currency,
        description="Use this to convert between currencies, like '100 USD to INR'."
    ),
    Tool(
        name="YouTube Video Search",
        func=search_youtube_videos,
        description="Use this to find recent YouTube videos about a topic or person."
    ),
    Tool(
        name="E-commerce Product Search",
        func=e_commerce_search,
        description="Use this tool to find and recommend actual products and listings (like phones, earbuds, laptops, etc.) from Amazon and Flipkart. "
        "Always prefer this tool for any product-related questions."
        "Include the tool output directly in your final answer instead of paraphrasing."
    ),
    Tool(
        name="Indian Holiday Lookup",
        func=lookup_indian_holidays,
        description="Use this to check if a specific date is a public holiday in India, or to see upcoming Indian holidays.",
    ),
    StructuredTool.from_function(
        name="Train Live Status Checker",
        description="Use this tool to get the live running status of a train. Input should include 'train_number' and optional 'start_day' (default is 1).",
        func=get_train_live_status,
        args_schema=TrainStatusInput,
    ),
    Tool(
        name="PNR Status Checker",
        func=get_pnr_status,
        description="Check Indian Railways PNR status using a 10-digit PNR number like '1234567890'."
    ),
    Tool(
        name="Flight Status Checker",
        func=get_flight_status,
        description="Get current status of a flight using its IATA flight code, e.g. 'AI101' or 'UA246'."
    ),
    Tool(
        name="FD Rates Checker",
        func=get_fd_rates,
        description=(
            "Fetch latest fixed deposit interest rates from BankBazaar. Always show rates from other banks as well if available"
        )
    ),
    Tool(
    name="Recharge Plan Search",
    func=search_recharge_plans,
    description="Fetch real-time prepaid recharge plans for telecom operators like Airtel, Jio, VI via trusted sources."
),


]