# 🧠 AI Travel Agent
An AI-powered travel assistant with React frontend and Python backend.
Users input travel plans, backend calls AI and tools, frontend displays results.

# 🚀 Setup & Run
Clone repository

git clone git@github.com:TinyZhen/Travel_Agent.git
cd Travel_Agent

Backend Setup (Python)
Requires Python 3.8+ and pip.

cd backend
python3 -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt

Create a .env file in backend folder with content:

OPENROUTER_API_KEY=your_api_key_here
TICKETMASTER_API_KEY=your_api_key_here
GOOGLE_API_KEY=your_api_key_here
AMADEUS_API_KEY=your_api_key_here
AMADEUS_SECRET=your_api_secret_here

Start backend server:

uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Backend runs on http://localhost:8000

Frontend Setup (React + Vite)
Requires Node.js (v16+) and npm.

cd frontend
npm install
npm run dev

Frontend runs on http://localhost:5173

Usage
Open browser at http://localhost:5173
Input travel prompt like: "I want to visit New York from May 1st for 3 days."
Click Send and wait for AI travel plan.

# 🔑 How to Obtain API Keys
OPENROUTER_API_KEY

Visit https://openrouter.ai/

Sign up, create API key

Add to .env

TICKETMASTER_API_KEY

Visit https://developer.ticketmaster.com/

Sign up, create app, get key

Add to .env

GOOGLE_API_KEY

Visit https://console.cloud.google.com/apis/credentials

Enable needed APIs, create key

Add to .env

AMADEUS_API_KEY and AMADEUS_SECRET

Visit https://developers.amadeus.com/self-service-api

Register, create app, get key and secret

Add to .env
