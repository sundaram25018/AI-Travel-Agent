# ✈️ AI Travel Agent  

An AI-powered travel assistant built with **Streamlit**, **Gemini AI**, and **SerpAPI/Amadeus APIs**.  
It helps users plan trips, find flights, explore destinations, and get smart travel recommendations — all in one place.  

---

## 🌟 Features  
- 🔍 **Smart Search** – Find travel information using Google Search (SerpAPI).  
- 🧠 **AI Trip Planner** – Personalized itineraries powered by **Google Gemini**.  
- ✈️ **Flight Finder** – Fetches cheapest flights via **SerpAPI (Google Flights)** and **Amadeus API**.  
- 🗓️ **Itinerary Suggestions** – AI-generated day-by-day travel plans.  
- 🌍 **Destination Insights** – Best time to travel, popular attractions, and travel tips.  
- 🖥️ **Interactive UI** – Simple and responsive **Streamlit interface**.  

---

## 🛠️ Tech Stack  
- **Frontend**: [Streamlit](https://streamlit.io/)  
- **LLM**: [Google Gemini](https://ai.google.dev/) via `agno`  
- **Search**: [SerpAPI](https://serpapi.com/) (Google Search / Flights)  
- **Flights API**: [Amadeus](https://developers.amadeus.com/) (flight offers)  
- **Utilities**: `isodate`, `requests`, `python-dotenv`  

---

## 📂 Project Structure  
AI-Travel-Agent/
│── app.py # Main Streamlit app
│── requirements.txt # Dependencies
│── .env.example # Example environment variables
│── README.md # Project documentation
│── /venv # Virtual environment (not pushed to GitHub)


---

## ⚙️ Setup Instructions  

### 1️⃣ Clone Repo  
```bash
git clone https://github.com/your-username/AI-Travel-Agent.git
cd AI-Travel-Agent
```

2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

4️⃣ Setup Environment Variables
```bash
SERPAPI_API_KEY=your_serpapi_api_key
GOOGLE_API_KEY=your_gemini_api_key
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
```

👉 Get API keys here:

https://serpapi.com/manage-api-key
https://ai.google.dev/gemini-api/docs/api-key
https://developers.amadeus.com/get-started

5️⃣ Run the App
```bash
streamlit run app.py
```
🎯 Usage

Enter your source city, destination, and dates
The AI agent will:
    Suggest the best travel plan
    Show cheapest available flights (SerpAPI + Amadeus)
    Provide travel insights and recommendations

📸 Screenshots


🚀 Future Improvements

🏨 Hotel booking integration (Booking.com / Expedia API)
🚗 Car rental search
🌦️ Weather forecasts
📍 Maps integration (Google Maps API)
💾 User profile + saved trips

📜 License

MIT License © 2025 sundaram