# app.py
import streamlit as st
import json
import os
from serpapi import GoogleSearch
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from datetime import datetime
from dotenv import load_dotenv

# Load .env
load_dotenv()

# -----------------------
# Basic config & checks
# -----------------------
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Put keys into environment for any library that expects them
if SERPAPI_KEY:
    os.environ["SERPAPI_KEY"] = SERPAPI_KEY
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Streamlit page config
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")

# If missing keys — show friendly message and stop
if not SERPAPI_KEY or not GOOGLE_API_KEY:
    st.markdown(
        """
        <div style="padding:16px;border-radius:8px;background:#ffe6e6;">
        <h3>❗ API keys missing</h3>
        <p>Please set <strong>SERPAPI_KEY</strong> and <strong>GOOGLE_API_KEY</strong> in your environment or in a <code>.env</code> file.</p>
        <p>Example <code>.env</code>:</p>
        <pre>SERPAPI_KEY=your_serpapi_key_here
GOOGLE_API_KEY=your_google_gemini_key_here</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# -----------------------
# UI: Header & Inputs
# -----------------------
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

st.markdown("### 🌍 Where are you headed?")
source = st.text_input("🛫 Departure City (IATA Code):", "BOM")
destination = st.text_input("🛬 Destination (IATA Code):", "DEL")

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
)

st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center;padding:15px;background-color:#ffecd1;border-radius:10px;">
        <h3>🌟 Your {travel_theme} to {destination} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except Exception:
        return "N/A"

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
    "Relaxing on the beach, exploring historical sites"
)
departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

# Sidebar
st.sidebar.title("🌎 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")
budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

# -----------------------
# SerpAPI flight params helper
# -----------------------
def build_flight_params(src, dst, outbound, inbound):
    return {
        "engine": "google_flights",
        "departure_id": src,
        "arrival_id": dst,
        "outbound_date": str(outbound),
        "return_date": str(inbound),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

# Function to fetch flight data (defensive)
def fetch_flights(source, destination, departure_date, return_date):
    params = build_flight_params(source, destination, departure_date, return_date)
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results or {}
    except Exception as e:
        st.error(f"Error fetching flights: {e}")
        return {}

# Function to extract top 3 cheapest flights
def extract_cheapest_flights(flight_data):
    try:
        best_flights = flight_data.get("best_flights", []) or []
        sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]
        return sorted_flights
    except Exception:
        return []

# -----------------------
# AI Agents (agno) — cleaned
# -----------------------
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

# Note: some agno versions may expect different args; we keep only widely supported args.
researcher = Agent(
    name="Researcher",
    instructions=[
        f"Current system time: {current_time}.",
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user’s interests and travel style.",
        "Prioritize information from reliable sources and official travel guides.",
        "Provide well-structured summaries with key insights and recommendations."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

planner = Agent(
    name="Planner",
    instructions=[
        f"Current system time: {current_time}.",
        "Gather details about the user's travel preferences and budget.",
        "Create a detailed itinerary with scheduled activities and estimated costs.",
        "Ensure the itinerary includes transportation options and travel time estimates.",
        "Optimize the schedule for convenience and enjoyment.",
        "Present the itinerary in a structured format."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
)

hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        f"Current system time: {current_time}.",
        "Identify key locations in the user's travel itinerary.",
        "Search for highly rated hotels near those locations.",
        "Search for top-rated restaurants based on cuisine preferences and proximity.",
        "Prioritize results based on user preferences, ratings, and availability.",
        "Provide direct booking links or reservation options where possible."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# -----------------------
# Generate Travel Plan
# -----------------------
if st.button("🚀 Generate Travel Plan"):
    # 1) Flights
    with st.spinner("✈️ Fetching best flight options..."):
        flight_data = fetch_flights(source, destination, departure_date, return_date)
        cheapest_flights = extract_cheapest_flights(flight_data)

    # 2) Research (AI)
    with st.spinner("🔍 Researching best attractions & activities..."):
        research_prompt = (
            f"Research the best attractions and activities in {destination} for a {num_days}-day {travel_theme.lower()} trip. "
            f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. "
            f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}."
        )
        try:
            research_results = researcher.run(research_prompt, stream=False)
        except Exception as e:
            st.error(f"Research agent error: {e}")
            research_results = type("Empty", (), {"content": "No research results due to error."})()

    # 3) Hotels & Restaurants (AI)
    with st.spinner("🏨 Searching for hotels & restaurants..."):
        hotel_restaurant_prompt = (
            f"Find the best hotels and restaurants near popular attractions in {destination} for a {num_days}-day {travel_theme.lower()} trip. "
            f"Budget: {budget}. Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}."
        )
        try:
            hotel_restaurant_results = hotel_restaurant_finder.run(hotel_restaurant_prompt, stream=False)
        except Exception as e:
            st.error(f"Hotel & Restaurant agent error: {e}")
            hotel_restaurant_results = type("Empty", (), {"content": "No hotels/restaurants found due to error."})()

    # 4) Itinerary (AI Planner)
    with st.spinner("🗺️ Creating your personalized itinerary..."):
        try:
            planning_prompt = (
                f"Based on the following data, create a {num_days}-day itinerary for a {travel_theme.lower()} trip to {destination}. "
                f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
                f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. Research: {getattr(research_results, 'content', '')}. "
                f"Flights: {json.dumps(cheapest_flights)}. Hotels & Restaurants: {getattr(hotel_restaurant_results, 'content', '')}."
            )
            itinerary = planner.run(planning_prompt, stream=False)
        except Exception as e:
            st.error(f"Planner agent error: {e}")
            itinerary = type("Empty", (), {"content": "No itinerary generated due to error."})()

    # -----------------------
    # Display Flights
    # -----------------------
    st.subheader("✈️ Cheapest Flight Options")
    if cheapest_flights:
        cols = st.columns(len(cheapest_flights))
        for idx, flight in enumerate(cheapest_flights):
            with cols[idx]:
                airline_logo = flight.get("airline_logo", "")
                price = flight.get("price", "Not Available")
                total_duration = flight.get("total_duration", "N/A")

                flights_info = flight.get("flights", [{}])
                departure = flights_info[0].get("departure_airport", {}) if flights_info else {}
                arrival = flights_info[-1].get("arrival_airport", {}) if flights_info else {}
                airline_name = flights_info[0].get("airline", "Unknown Airline") if flights_info else flight.get("airline", "Unknown Airline")

                departure_time = format_datetime(departure.get("time", "N/A"))
                arrival_time = format_datetime(arrival.get("time", "N/A"))

                departure_token = flight.get("departure_token", "") or None
                booking_options = None

                if departure_token:
                    # Defensive call — if it fails, we continue gracefully
                    try:
                        params_with_token = build_flight_params(source, destination, departure_date, return_date)
                        params_with_token["departure_token"] = departure_token
                        search_with_token = GoogleSearch(params_with_token)
                        results_with_booking = search_with_token.get_dict() or {}
                        # guard indexes/keys
                        best_flights_list = results_with_booking.get("best_flights", [])
                        if len(best_flights_list) > idx:
                            booking_options = best_flights_list[idx].get("booking_token")
                        else:
                            # fallback: try first entry
                            if best_flights_list:
                                booking_options = best_flights_list[0].get("booking_token")
                    except Exception as e:
                        # Non-fatal: we will show book button disabled or #
                        st.warning(f"Could not fetch booking link for flight #{idx+1}: {e}")
                        booking_options = None

                booking_link = f"https://www.google.com/travel/flights?tfs={booking_options}" if booking_options else "#"

                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid #ddd;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                        background-color: #f9f9f9;
                        margin-bottom: 20px;
                    ">
                        {f'<img src="{airline_logo}" width="100" alt="Flight Logo" />' if airline_logo else ""}
                        <h3 style="margin: 10px 0;">{airline_name}</h3>
                        <p><strong>Departure:</strong> {departure_time}</p>
                        <p><strong>Arrival:</strong> {arrival_time}</p>
                        <p><strong>Duration:</strong> {total_duration} min</p>
                        <h2 style="color: #008000;">💰 {price}</h2>
                        <a href="{booking_link}" target="_blank" style="
                            display: inline-block;
                            padding: 10px 20px;
                            font-size: 16px;
                            font-weight: bold;
                            color: #fff;
                            background-color: #007bff;
                            text-decoration: none;
                            border-radius: 5px;
                            margin-top: 10px;
                        ">{'🔗 Book Now' if booking_options else '🔗 No booking link available'}</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("⚠️ No flight data available.")

    # -----------------------
    # Hotels & Restaurants
    # -----------------------
    st.subheader("🏨 Hotels & Restaurants")
    try:
        st.write(getattr(hotel_restaurant_results, "content", "No hotel/restaurant info available."))
    except Exception:
        st.write("No hotel/restaurant info available.")

    # -----------------------
    # Itinerary
    # -----------------------
    st.subheader("🗺️ Your Personalized Itinerary")
    try:
        st.write(getattr(itinerary, "content", "No itinerary available."))
    except Exception:
        st.write("No itinerary available.")

    st.success("✅ Travel plan generated successfully!")
