from wikipedia import summary, exceptions
from serpapi import GoogleSearch
import yfinance as yf
import os, requests, re, datetime, json
import holidays
from dotenv import load_dotenv
from pydantic import BaseModel
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Tool: Get current time
def get_current_time(*args, **kwargs):
    import datetime
    return datetime.datetime.now().strftime("%I:%M %p")

# Tool: Search Wikipedia
def search_wikipedia(query: str) -> str:
    """Searches Wikipedia and returns the summary of the first result."""

    try:
        return summary(query, sentences=2)
    except exceptions.DisambiguationError as e:
        return f"The query was too broad. Possible options: {', '.join(e.options[:5])}"
    except exceptions.PageError:
        return "I couldn't find any information on that topic."
    except Exception as e:
        return f"Something went wrong: {str(e)}"

# Tool: Web Search using SerpAPI
def serpapi_search(query: str) -> str:
    search = GoogleSearch({
        "q": query,
        "api_key": os.environ["SERPAPI_API_KEY"],
        "num": 3
    })
    results = search.get_dict()
    try:
        return "\n".join([r["snippet"] for r in results["organic_results"][:3]])
    except:
        return "No relevant results found."

# Tool: Get stock price using yfinance
def get_stock_price(query: str) -> str:
    """Fetches real-time stock price for a given ticker or company name."""
    try:
        ticker = yf.Ticker(query)
        price = ticker.info.get("regularMarketPrice", None)
        name = ticker.info.get("shortName", query)
        if price:
            return f"The current stock price of {name} ({query.upper()}) is ${price:.2f}."
        else:
            return "I couldn't retrieve the stock price. Please check the ticker symbol."
    except Exception as e:
        return f"Error fetching stock price: {str(e)}"
    
# Tool: Get weather information
def detect_location_from_ip() -> str:
    """Returns city name based on IP address."""
    try:
        ipinfo_token = os.getenv("IPINFO_TOKEN", None)
        url = "https://ipinfo.io/json"
        if ipinfo_token:
            url += f"?token={ipinfo_token}"

        response = requests.get(url, timeout=3)
        data = response.json()
        return data.get("city", "")
    except Exception as e:
        return ""

def get_weather(city: str = "") -> str:
    """Returns current weather info for a given or detected city."""
    if not city:
        city = detect_location_from_ip()
        if not city:
            return "I couldn't determine your location. Please provide a city name."

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather service is not configured properly, please check your API key."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200:
            return f"⚠️ Weather API Error: {data.get('message', 'Unknown error')}"

        if "weather" not in data or "main" not in data:
            return "⚠️ Unexpected response format. Please try again later."

        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        return (
            f"The weather in {city.title()} is {weather}, "
            f"{temp}°C (feels like {feels_like}°C), "
            f"with {humidity}% humidity."
        )

    except Exception as e:
        return f"Error retrieving weather: {str(e)}"

# Tool: Convert currency using exchangerate-api.com
def convert_currency(query: str) -> str:
    """
    Converts currency using exchangerate-api.com
    Format: '100 USD to INR'
    """
    match = re.search(r"(\d+(?:\.\d+)?)\s*([A-Za-z]{3})\s+(?:to|in)\s+([A-Za-z]{3})", query)
    if not match:
        return "Please format your query like '100 USD to INR'."

    amount, from_curr, to_curr = match.groups()
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY")

    if not api_key:
        return "Currency API key not set. Please configure EXCHANGE_RATE_API_KEY."

    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}/{amount}"
        response = requests.get(url)
        data = response.json()

        if data["result"] == "success":
            converted = data["conversion_result"]
            return f"As of today's exchange rates,{amount} {from_curr} is approximately {converted:.2f} {to_curr}."
        else:
            return f"Failed to convert from {from_curr} to {to_curr}. Error: {data.get('error-type', 'Unknown error')}"

    except Exception as e:
        return f"Error during currency conversion: {str(e)}"

# Tool: Search YouTube videos using SerpAPI  
def search_youtube_videos(query: str) -> str:
    """Uses SerpAPI to search YouTube and return top 2–3 recent videos."""
    from serpapi import GoogleSearch
    import os

    search = GoogleSearch({
        "q": f"{query} site:youtube.com",
        "api_key": os.environ["SERPAPI_API_KEY"]
    })

    try:
        results = search.get_dict()
        video_links = []
        for result in results.get("organic_results", [])[:3]:
            title = result.get("title")
            link = result.get("link")
            snippet = result.get("snippet", "")
            video_links.append(f"**{title}**\n{snippet}\n🔗 {link}\n")
        
        return "\n".join(video_links) if video_links else "No videos found."
    except Exception as e:
        return f"Error fetching YouTube videos: {str(e)}"
    
# Tool: Search Amazon products using SerpAPI
def e_commerce_search(query: str) -> str:
    """Searches Amazon and Flipkart via SerpAPI and combines results with product links."""
    from serpapi import GoogleSearch
    import os

    serpapi_key = os.environ["SERPAPI_API_KEY"]

    def fetch_results(site: str):
        search = GoogleSearch({
            "q": f"{query} site:{site}",
            "api_key": serpapi_key
        })
        results = search.get_dict()
        items = []
        for r in results.get("organic_results", [])[:3]:
            title = r.get("title", "No title")
            link = r.get("link", "")
            snippet = r.get("snippet", "")
            
            item_str = (
                f"**{title}**\n"
                f"{snippet}\n"
                f"[🛒 View Product]({link})\n"
                f"---"
            )
            items.append(item_str)
        return items

    try:
        amazon_results = fetch_results("amazon.in")
        flipkart_results = fetch_results("flipkart.com")

        all_results = [
            "### 🛒 Amazon Results:\n",
            *amazon_results,
            "\n### 🛍️ Flipkart Results:\n",
            *flipkart_results
        ]

        return "\n\n".join(all_results)
    
    except Exception as e:
        return f"❌ Error fetching product info: {str(e)}"


# Tool: Lookup Indian holidays using the 'holidays' library
def lookup_indian_holidays(query: str) -> str:
    """Answers questions about Indian holidays using the 'holidays' library."""
    try:
        today = datetime.date.today()
        india_holidays = holidays.country_holidays('IN', years=range(today.year, today.year + 2))

        query_lower = query.lower()

        if "today" in query_lower:
            return f"✅ Today is a holiday: {india_holidays.get(today)}" if today in india_holidays else "❌ Today is not a holiday in India."

        elif "tomorrow" in query_lower:
            tomorrow = today + datetime.timedelta(days=1)
            return f"✅ Tomorrow is a holiday: {india_holidays.get(tomorrow)}" if tomorrow in india_holidays else "❌ Tomorrow is not a holiday in India."

        elif "this month" in query_lower:
            holidays_this_month = {
                date: name for date, name in india_holidays.items()
                if date.month == today.month and date >= today
            }
            if not holidays_this_month:
                return "No holidays remaining this month in India."
            return "📅 Holidays this month:\n" + "\n".join([f"{date.strftime('%d %b %Y')}: {name}" for date, name in holidays_this_month.items()])

        elif any(char.isdigit() for char in query):  # if there's a specific date
            from dateutil import parser
            try:
                target_date = parser.parse(query, fuzzy=True).date()
                if target_date in india_holidays:
                    return f"✅ {target_date.strftime('%d %b %Y')} is a holiday: {india_holidays.get(target_date)}"
                else:
                    return f"❌ {target_date.strftime('%d %b %Y')} is not a public holiday in India."
            except:
                return "Couldn't understand the date. Please rephrase."

        else:
            # Default: show next 5 upcoming holidays
            upcoming = sorted([d for d in india_holidays if d >= today])[:5]
            return "🗓️ Next 5 public holidays in India:\n" + "\n".join(
                [f"{d.strftime('%d %b %Y')}: {india_holidays[d]}" for d in upcoming]
            )

    except Exception as e:
        return f"Error checking holidays: {str(e)}"


# Tool: Get live train status
class TrainStatusInput(BaseModel):
    train_number: str
    start_day: str = "1"

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
RAPIDAPI_HOST = "irctc1.p.rapidapi.com"

# Tool: Get live train status
def get_train_live_status(train_number: str, start_day: str = "1") -> str:
    """Fetches the live running status of a train with enriched details."""
    url = "https://irctc1.p.rapidapi.com/api/v1/liveTrainStatus"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    params = {"trainNo": train_number, "startDay": start_day}

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if not data.get("status", False):
            return f"❌ Could not fetch live status. Reason: {data.get('message', 'Unknown error')}"

        d = data["data"]

        # Format journey time from minutes to "x hrs y mins"
        journey_mins = d.get("journey_time", 0)
        hours = journey_mins // 60
        minutes = journey_mins % 60
        journey_time_str = f"{hours} hrs {minutes} mins"

        # Handle platform and pantry info
        platform = d.get("platform_number")
        platform_str = str(platform) if platform and platform > 0 else "Not assigned"
        pantry = "Yes" if d.get("pantry_available", False) else "No"

        return (
            f"🚆 **Train {d['train_number']} - {d['train_name']}**\n"
            f"📅 Run Days: {d.get('run_days', 'N/A')}\n"
            f"🛤️ Route: {d.get('source_stn_name', 'N/A')} ➝ {d.get('dest_stn_name', 'N/A')}\n"
            f"⏱️ Departure Time: {d.get('std', 'N/A')}\n"
            f"⌛ Journey Time: {journey_time_str}\n"
            f"🍱 Pantry Available: {pantry}\n\n"
            f"📍 **Current Station**: {d.get('current_station_name', 'N/A')}\n"
            f"🕒 ETA: {d.get('eta', 'N/A')} | Scheduled: {d.get('cur_stn_sta', 'N/A')}\n"
            f"🔄 Delay: {d.get('delay', 'N/A')} mins\n"
            f"📏 Ahead Distance: {d.get('ahead_distance_text', 'N/A')}\n"
            f"🛑 Platform: {platform_str}\n"
            f"🕓 Last Updated: {d.get('status_as_of', 'N/A')}"
        )

    except Exception as e:
        return f"⚠️ Error fetching train status: {str(e)}"


# Tool: Get PNR status
def get_pnr_status(pnr_number: str) -> str:
    """Fetches the PNR status using IRCTC1 API."""
    url = "https://irctc1.p.rapidapi.com/api/v3/getPNRStatus"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    params = {"pnrNumber": pnr_number}

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if not data.get("status", False):
            return f"❌ Could not fetch PNR status. Reason: {data.get('message', 'Unknown error')}"

        d = data["data"]
        train_info = f"🚆 {d['train_number']} - {d['train_name']}"
        journey = f"{d['boarding_point']} → {d['reservation_upto']}"
        date = d["journey_date"]
        passengers = "\n".join([
            f"👤 Passenger {p['no']}: {p['booking_status']} ➡ {p['current_status']}"
            for p in d["passengers"]
        ])

        return (
            f"📋 **PNR: {pnr_number}**\n{train_info}\n📅 Date: {date}\n🛤 Route: {journey}\n{passengers}"
        )
    except Exception as e:
        return f"⚠️ Error fetching PNR status: {str(e)}"


AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")

# Tool: Get flight status
def get_flight_status(flight_query: str) -> str:
    """
    Query flight status using Aviationstack.
    Input examples: "UA246", "AI101"
    """
    url = "http://api.aviationstack.com/v1/flights"
    params = {"access_key": AVIATIONSTACK_KEY, "flight_iata": flight_query}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        flights = data.get("data", [])
        if not flights:
            return "No flight found for that code."

        flight = flights[0]
        dep = flight["departure"]
        arr = flight["arrival"]
        return (
            f"✈️ Flight **{flight['flight']['iata']} ({flight['airline']['name']})**\n"
            f"Departure: {dep['airport']} at {dep['scheduled']}\n"
            f"Arrival: {arr['airport']} at {arr['scheduled']}\n"
            f"Status: {flight['flight_status']}"
        )
    except Exception as e:
        return f"Error fetching flight data: {e}"

# Tool: Get FD rates from BankBazaar
def get_fd_rates(bank_name: str = "") -> str:
    """
    Scrape 1-year FD rates from BankBazaar.
    If a bank name is provided, show its rate + 3 more top banks.
    """
    url = "https://www.bankbazaar.com/fixed-deposit/5years-fd-interest-rates.html"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.select_one("table")
        rows = table.select("tr")[1:]  # skip table header

        all_rates = []
        matched_bank = []

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.select("td")]
            bank = cols[0]
            general = cols[1]
            senior = cols[2]
            formatted = f"🏦 {bank}: {general} (General), {senior} (Senior)"
            all_rates.append(formatted)

            if bank_name and bank_name.lower() in bank.lower():
                matched_bank.append(formatted)

        if bank_name and matched_bank:
            others = [r for r in all_rates if r not in matched_bank][:3]
            return "\n".join(matched_bank + ["\n📊 Here are a few other banks:"] + others)
        else:
            return "\n".join(all_rates[:5])  # top 5 fallback

    except Exception as e:
        return f"⚠️ Error fetching FD rates: {str(e)}"

# Tool: Search real-time recharge plans
def search_recharge_plans(operator_and_amount: str) -> str:
    """
    Search real-time recharge plans for telecom operators using SerpAPI.
    e.g., "Airtel prepaid recharge plans under 500"
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    q = f"{operator_and_amount} recharge plans site:paytm.com OR site:airtel.in OR site:jio.com"
    
    search = GoogleSearch({"q": q, "api_key": api_key, "num": 3})
    try:
        results = search.get_dict()
        items = []
        for r in results.get("organic_results", []):
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            items.append(f"**{title}**\n{snippet}\n🔗 {link}")
        return "\n\n".join(items) if items else "No real-time recharge data found."
    except Exception as e:
        return f"Error fetching recharge plans: {e}"


