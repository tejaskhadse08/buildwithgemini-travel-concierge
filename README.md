# Travel Concierge AI Agent

An intelligent, multi-modal travel assistant built with Google's **Agent Development Kit (ADK)**, deployed to **Vertex AI Agent Engine (Agent Runtime)** with an **A2A (Agent-to-Agent)** interface and a modern, responsive web chat frontend featuring **A2UI** card rendering.

![Travel Concierge Agent Demo](demo.gif)

---

## Architecture & Wired Google Cloud Services

This repository implements a production agent architecture leveraging native Google Cloud services:

* **Vertex AI Agent Engine (Agent Runtime):** Serverless runtime environment hosting the ADK agent over the A2A protocol (`acli_version: 1.1.0`).
* **Vertex AI Memory Bank (`VertexAiMemoryBankService`):** Long-term session memory for cross-session facts (e.g., user dietary restrictions, allergies, and travel preferences) integrated via `PreloadMemoryTool` and post-turn callbacks.
* **Google Cloud Firestore (`google-cloud-firestore`):** Managed NoSQL database storing destination catalogs, ratings, trip costs, and popular activities in the `destinations` collection.
* **Google Cloud Storage (GCS):** Public bucket (`travel-concierge-assets-...`) storing in-memory generated media bytes for instant public HTTPS URL serving.
* **Vertex AI Image Generation (`gemini-3.1-flash-lite-image`):** Multi-modal image generation via the `google-genai` SDK in the global region.
* **Vertex AI Omni Video Model (`gemini-omni-flash-preview`):** Video generation model generating short destination video clips saved to GCS and ADK artifacts.
* **Agent Engine Sandbox Code Executor (`AgentEngineSandboxCodeExecutor`):** Isolated execution sandbox for Python calculations and dynamic data processing.
* **Google Maps & Places API:** Geocoding addresses and discovering nearby points of interest (attractions, restaurants, hotels) via the Google Places API (New).

---

## Agent Capabilities & Tools

The agent is equipped with the following active tools defined in `app/tools.py` and `app/agent.py`:

| Tool | Capability / Source |
| --- | --- |
| `list_destinations` | Queries Firestore `destinations` collection with optional country filtering |
| `get_destination` | Retrieves specific destination details by ID or city name from Firestore |
| `add_destination` | Adds a new destination catalog entry with activities, climate, cost, and rating to Firestore |
| `generate_destination_image` | Generates scenic travel photographs with `gemini-3.1-flash-lite-image`, uploads bytes to GCS, and registers ADK session artifacts |
| `generate_destination_video` | Generates short destination video clips using `gemini-omni-flash-preview`, uploads to GCS, and saves ADK artifacts |
| `geocode_address` | Converts addresses or landmarks into latitude/longitude coordinates via Google Maps Geocoding API |
| `find_nearby_places` | Searches for nearby attractions, restaurants, or hotels around coordinates using Google Places API |
| `convert_travel_currency` | Fetches live currency exchange rates and calculates trip conversions via Frankfurter API |
| `fetch_live_destination_info` | Fetches real-time Wikipedia destination summaries and links |
| `PreloadMemoryTool` | Preloads past session memories from Vertex AI Memory Bank |

---

## User Interface & A2UI Renderer

The project includes a lightweight, zero-framework web frontend located in `frontend/`:

* **A2UI Protocol (`application/json+a2ui`):** Agent responses automatically emit structured A2UI cards rendered natively in the chat web interface.
* **FastAPI A2A Proxy (`frontend/main.py`):** Acts as a secure, same-origin proxy using Application Default Credentials (ADC) to stream A2A messages to the deployed Agent Engine runtime.
* **Modern Ocean Theme:** Responsive chat UI featuring a Light/Dark theme switcher, clickable prompt suggestion chips, and structured card layouts.

---

## Local Development & Setup

### Prerequisites
* Python 3.11+
* `uv` or `pip`
* Google Cloud SDK (`gcloud`) authenticated with project access

### Environment Variables
Set the following environment variables before running:

```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-number>/locations/us-east1/reasoningEngines/<engine-id>"
export AGENT_DIRECTORY="app"
```

### Running the Agent & Web Frontend Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   cd frontend && pip install -r requirements.txt
   ```

2. **Start the local FastAPI proxy server:**
   ```bash
   cd frontend
   python main.py
   ```

3. **Access the Chat Interface:**
   Open your browser to port `8080` on localhost to interact with your agent.

### Deploying to Cloud Run

To deploy the frontend proxy service to Google Cloud Run:

```bash
cd frontend
gcloud run deploy travel-concierge-frontend \
  --source . \
  --region us-east1 \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="$AGENT_ENGINE_RESOURCE_NAME",AGENT_DIRECTORY="app" \
  --allow-unauthenticated
```
