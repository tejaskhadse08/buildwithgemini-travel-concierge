"""Firestore tools for travel-concierge agent."""

from google.adk.tools import ToolContext
from google.cloud import firestore

# IMPORTANT: Hardcode project ID as explicit string for Firestore client
PROJECT_ID = "qwiklabs-gcp-02-9b87699e22a7"



def _get_firestore_client() -> firestore.Client:
    """Helper to return Firestore client initialized with hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_destinations(country: str = "") -> list[dict]:
    """Retrieves travel destinations from the Firestore database.

    Args:
        country: Optional country name to filter destinations. If empty or not provided, returns all destinations.

    Returns:
        A list of destination dictionaries containing details like name, country, description, rating, cost, and activities.
    """
    db = _get_firestore_client()
    collection_ref = db.collection("destinations")
    docs = collection_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if country:
            if country.lower() in data.get("country", "").lower():
                results.append(data)
        else:
            results.append(data)

    return results


def get_destination(destination_id_or_name: str) -> dict:
    """Gets details for a specific travel destination by ID or name from Firestore.

    Args:
        destination_id_or_name: The document ID (e.g., 'paris', 'tokyo') or city/destination name.

    Returns:
        A dictionary with destination details or an error message if not found.
    """
    db = _get_firestore_client()
    doc_id = destination_id_or_name.lower().replace(" ", "_")

    doc_ref = db.collection("destinations").document(doc_id)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # Fallback to search by name field
    docs = db.collection("destinations").stream()
    for d in docs:
        data = d.to_dict()
        if destination_id_or_name.lower() in data.get("name", "").lower():
            data["id"] = d.id
            return data

    return {"error": f"Destination '{destination_id_or_name}' not found."}


def add_destination(
    name: str,
    country: str,
    description: str,
    climate: str = "Temperate",
    rating: float = 4.5,
    estimated_cost_usd: int = 2000,
    popular_activities: list[str] = None,
) -> dict:
    """Adds a new travel destination to the Firestore database catalog.

    Args:
        name: Name of the destination city or region (e.g., 'Rome', 'Bali').
        country: Country where the destination is located (e.g., 'Italy', 'Indonesia').
        description: Short overview of the destination and key highlights.
        climate: Primary climate type (e.g., 'Tropical', 'Mediterranean', 'Temperate').
        rating: Rating score out of 5.0 (e.g., 4.7).
        estimated_cost_usd: Estimated total trip cost in USD.
        popular_activities: List of popular tourist activities or attractions.

    Returns:
        A dictionary acknowledging successful addition with the saved destination details.
    """
    db = _get_firestore_client()
    doc_id = name.lower().replace(" ", "_")
    activities = popular_activities or []

    data = {
        "name": name,
        "country": country,
        "description": description,
        "climate": climate,
        "rating": float(rating),
        "estimated_cost_usd": int(estimated_cost_usd),
        "popular_activities": activities,
    }

    db.collection("destinations").document(doc_id).set(data)
    data["id"] = doc_id
    return {"status": "success", "message": f"Successfully added {name} to destinations database.", "destination": data}


def fetch_live_destination_info(destination_name: str) -> dict:
    """Fetches live summary background and travel details for a destination from Wikipedia's public API.

    Args:
        destination_name: Name of the city or travel destination (e.g., 'Paris', 'Kyoto', 'Barcelona').

    Returns:
        A dictionary containing title, summary extract, description, and link, or an error message.
    """
    import urllib.parse
    import requests

    encoded_name = urllib.parse.quote(destination_name.strip())
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_name}"
    headers = {"User-Agent": "TravelConciergeAgent/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "summary": data.get("extract"),
                "description": data.get("description"),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
            }
        return {"error": f"Could not find live information for destination '{destination_name}'."}
    except Exception as e:
        return {"error": f"Failed to fetch live destination info: {str(e)}"}


def convert_travel_currency(
    amount: float = 100.0,
    from_currency: str = "USD",
    to_currency: str = "EUR",
) -> dict:
    """Converts money between world currencies for travel budgeting using live exchange rates from Frankfurter API.

    Args:
        amount: The amount of money to convert (e.g., 100.0, 2500.0).
        from_currency: 3-letter currency code converting from (e.g., 'USD', 'EUR', 'GBP').
        to_currency: 3-letter currency code converting to (e.g., 'JPY', 'EUR', 'GBP', 'AUD').

    Returns:
        A dictionary containing the exchange rate, converted total, base currency, target currency, and rate date.
    """
    import os
    import requests

    src = from_currency.upper().strip()
    target = to_currency.upper().strip()

    # Optional API key from environment variable if provided by environment
    api_key = os.getenv("FRANKFURTER_API_KEY", os.getenv("CURRENCY_API_KEY", ""))

    url = f"https://api.frankfurter.dev/v1/latest?base={src}&symbols={target}"
    headers = {"User-Agent": "TravelConciergeAgent/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data.get("rates", {}).get(target)
            if rate is not None:
                converted_amount = round(amount * rate, 2)
                return {
                    "original_amount": amount,
                    "from_currency": src,
                    "converted_amount": converted_amount,
                    "to_currency": target,
                    "exchange_rate": rate,
                    "as_of_date": data.get("date"),
                }
            return {"error": f"Currency code '{target}' not supported or found."}
        return {"error": f"Failed to fetch exchange rates (HTTP {response.status_code})."}
    except Exception as e:
        return {"error": f"Currency conversion error: {str(e)}"}


def geocode_address(address: str) -> dict:
    """Converts an address or location name into geographic coordinates using the Google Maps Geocoding API.

    Args:
        address: Street address, landmark, or city name (e.g., 'Eiffel Tower, Paris', 'Shibuya Crossing, Tokyo').

    Returns:
        A dictionary with key fields: name, address, and location (latitude, longitude).
    """
    import os
    import urllib.parse
    import requests

    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}

    encoded_address = urllib.parse.quote(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            first_result = data["results"][0]
            loc = first_result.get("geometry", {}).get("location", {})
            return {
                "name": address,
                "address": first_result.get("formatted_address"),
                "location": {
                    "latitude": loc.get("lat"),
                    "longitude": loc.get("lng"),
                },
            }
        return {"error": f"Geocoding failed for address '{address}': {data.get('error_message', data.get('status'))}"}
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 1000.0,
) -> list[dict]:
    """Finds nearby points of interest or places around specific coordinates using Google Places API (New).

    Args:
        latitude: Latitude of the center location (e.g., 48.8584).
        longitude: Longitude of the center location (e.g., 2.2945).
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'restaurant', 'museum', 'hotel').
        radius_meters: Search radius in meters (default is 1000.0).

    Returns:
        A list of dictionaries with key fields: name, address, and location for each matching place.
    """
    import os
    import requests

    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return [{"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
    }
    body = {
        "includedTypes": [place_type],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=5)
        data = response.json()

        if "places" in data:
            results = []
            for place in data["places"]:
                results.append({
                    "name": place.get("displayName", {}).get("text"),
                    "address": place.get("formattedAddress"),
                    "location": {
                        "latitude": place.get("location", {}).get("latitude"),
                        "longitude": place.get("location", {}).get("longitude"),
                    },
                })
            return results
        elif "error" in data:
            return [{"error": data["error"].get("message")}]
        return []
    except Exception as e:
        return [{"error": f"Places request failed: {str(e)}"}]



# Hardcode public Cloud Storage bucket name
BUCKET_NAME = "travel-concierge-assets-qwiklabs-gcp-02-9b87699e22a7"


def generate_destination_image(
    prompt: str,
    tool_context: ToolContext = None,
) -> dict:
    """Generates a travel destination image using gemini-3.1-flash-lite-image model in global region.

    Saves the image as an ADK session artifact and uploads bytes directly to public Cloud Storage bucket.

    Args:
        prompt: Description of the travel image to generate (e.g., 'Sunset at Eiffel Tower', 'Cherry blossoms at Kyoto temple').
        tool_context: ADK ToolContext injected automatically by runtime for saving session artifacts.

    Returns:
        A dictionary containing status, public image_url, and filename.
    """
    import uuid
    from google import genai
    from google.cloud import storage
    from google.genai import types

    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=f"Generate a scenic travel photograph of: {prompt}",
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return {"error": "No image data returned from model."}

        ext = "jpg" if "jpeg" in mime_type else "png"
        filename = f"destination_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload image bytes directly to public GCS bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"generated_images/{filename}")
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/generated_images/{filename}"

        return {
            "status": "success",
            "image_url": public_url,
            "filename": filename,
            "prompt": prompt,
        }
    except Exception as e:
        return {"error": f"Image generation failed: {str(e)}"}


def generate_destination_video(
    prompt: str,
    tool_context: ToolContext = None,
) -> dict:
    """Generates a short travel video for a destination or attraction using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video as an ADK session artifact and uploads bytes directly to public Cloud Storage bucket.

    Args:
        prompt: Description of the travel video to generate (e.g., 'Aerial shot of tropical beach waves in Bali', 'Walking tour through Tokyo streets').
        tool_context: ADK ToolContext injected automatically by runtime for saving session artifacts.

    Returns:
        A dictionary containing status, public video_url, and filename.
    """
    import base64
    import uuid
    from google import genai
    from google.cloud import storage
    from google.genai import types

    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=f"Generate a short video of: {prompt}",
        )

        video_bytes = None
        if hasattr(interaction, "output_video") and interaction.output_video:
            data = interaction.output_video.data
            if isinstance(data, str):
                video_bytes = base64.b64decode(data)
            else:
                video_bytes = data
        elif hasattr(interaction, "outputs") and interaction.outputs:
            for out in interaction.outputs:
                if hasattr(out, "video") and out.video:
                    data = out.video.data
                    if isinstance(data, str):
                        video_bytes = base64.b64decode(data)
                    else:
                        video_bytes = data
                    break

        if not video_bytes and hasattr(interaction, "candidates") and interaction.candidates:
            for part in interaction.candidates[0].content.parts:
                if part.inline_data:
                    video_bytes = part.inline_data.data
                    if isinstance(video_bytes, str):
                        video_bytes = base64.b64decode(video_bytes)
                    break

        if not video_bytes:
            return {"error": "No video data returned from gemini-omni-flash-preview model."}

        filename = f"destination_video_{uuid.uuid4().hex[:8]}.mp4"
        mime_type = "video/mp4"

        # 1. Save video bytes with tool_context.save_artifact for Playground Artifacts panel
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes directly to public GCS bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"generated_videos/{filename}")
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/generated_videos/{filename}"

        return {
            "status": "success",
            "video_url": public_url,
            "filename": filename,
            "prompt": prompt,
        }
    except Exception as e:
        return {"error": f"Video generation failed: {str(e)}"}





