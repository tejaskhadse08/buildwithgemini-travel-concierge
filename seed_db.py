#!/usr/bin/env python3
"""Seed script for travel-concierge Firestore database."""

from google.cloud import firestore

# IMPORTANT: Hardcode project ID as explicit string for Firestore client
PROJECT_ID = "qwiklabs-gcp-02-9b87699e22a7"

DESTINATIONS = [
    {
        "id": "paris",
        "name": "Paris",
        "country": "France",
        "description": "City of Light known for the Eiffel Tower, art museums like the Louvre, world-class cuisine, and romantic atmosphere.",
        "climate": "Temperate",
        "rating": 4.8,
        "estimated_cost_usd": 2500,
        "popular_activities": ["Eiffel Tower Visit", "Louvre Museum Tour", "Seine River Cruise", "Montmartre Stroll"],
    },
    {
        "id": "tokyo",
        "name": "Tokyo",
        "country": "Japan",
        "description": "A bustling metropolis blending ultra-modern skyscrapers with historic temples, anime culture, and renowned gastronomy.",
        "climate": "Subtropical",
        "rating": 4.9,
        "estimated_cost_usd": 2800,
        "popular_activities": ["Shibuya Crossing", "Senso-ji Temple", "Tsukiji Outer Market", "Akihabara Tech District"],
    },
    {
        "id": "san_francisco",
        "name": "San Francisco",
        "country": "USA",
        "description": "Iconic West Coast city famous for the Golden Gate Bridge, cable cars, steep hills, and vibrant cultural tech scene.",
        "climate": "Mediterranean / Coastal Fog",
        "rating": 4.6,
        "estimated_cost_usd": 2200,
        "popular_activities": ["Golden Gate Park", "Alcatraz Island Tour", "Fisherman's Wharf", "Chinatown Tour"],
    },
    {
        "id": "kyoto",
        "name": "Kyoto",
        "country": "Japan",
        "description": "Japan's cultural capital filled with thousands of classical Buddhist temples, gardens, imperial palaces, and traditional wooden houses.",
        "climate": "Temperate",
        "rating": 4.9,
        "estimated_cost_usd": 2400,
        "popular_activities": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji (Golden Pavilion)", "Gion Geisha District"],
    },
    {
        "id": "rome",
        "name": "Rome",
        "country": "Italy",
        "description": "The Eternal City featuring nearly 3,000 years of globally influential art, architecture, and ancient ruins like the Colosseum.",
        "climate": "Mediterranean",
        "rating": 4.7,
        "estimated_cost_usd": 2100,
        "popular_activities": ["Colosseum Tour", "Vatican Museums & Sistine Chapel", "Trevi Fountain", "Roman Forum"],
    },
]


def seed_database():
    print(f"Connecting to Firestore database in project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("destinations")

    for dest in DESTINATIONS:
        doc_id = dest["id"]
        data = {k: v for k, v in dest.items() if k != "id"}
        collection_ref.document(doc_id).set(data)
        print(f"  ✓ Seeded destination: {dest['name']} ({doc_id})")

    print(f"Successfully seeded {len(DESTINATIONS)} destinations into Firestore!")


if __name__ == "__main__":
    seed_database()
