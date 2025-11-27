#!/usr/bin/env python3
"""
Seed script to populate Firebase with Romanian tourist attractions
"""
import json
import os
from services.firebase_service import FirebaseService
from datetime import datetime

def load_attractions_from_json(file_path):
    """Load attractions from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def seed_attractions():
    """Seed attractions data into Firebase"""
    print("Initializing Firebase connection...")
    fb = FirebaseService()

    # Load attractions from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'romanian_attractions.json')
    attractions = load_attractions_from_json(json_path)

    print(f"Found {len(attractions)} attractions to seed...")

    # Add each attraction to Firebase
    for i, attraction in enumerate(attractions, 1):
        attraction['created'] = datetime.now().isoformat()
        attraction_id = fb.create_attraction(attraction)
        print(f"[{i}/{len(attractions)}] Added: {attraction['name']} (ID: {attraction_id})")

    print("\n✓ Successfully seeded all attractions!")

def seed_sample_itineraries():
    """Seed sample itineraries"""
    print("\nSeeding sample itineraries...")
    fb = FirebaseService()

    # Get some attractions to create sample itineraries
    attractions = fb.get_attractions(region="Transylvania", category="Historical Monument")

    if len(attractions) >= 3:
        # Sample itinerary 1: Transylvania Castles Tour
        itinerary1 = {
            "title": "Transylvania Castles Adventure",
            "description": "Explore the most famous castles in Transylvania, including Dracula's Castle and the stunning Peleș Castle. A perfect 3-day trip through medieval Romania.",
            "attractions": attractions[:3],
            "userId": "demo_user_1",
            "userName": "Maria Popescu",
            "duration": "3 days",
            "totalDistance": 245.5,
            "likes": 42,
            "views": 156,
            "created": datetime.now().isoformat()
        }

        itinerary_id = fb.create_itinerary(itinerary1)
        print(f"Created sample itinerary: {itinerary1['title']} (ID: {itinerary_id})")

    # Get attractions for Bucharest
    bucharest_attractions = fb.get_attractions(city="Bucharest")

    if len(bucharest_attractions) >= 2:
        # Sample itinerary 2: Bucharest City Tour
        itinerary2 = {
            "title": "Bucharest Heritage Walk",
            "description": "Discover the architectural wonders and cultural treasures of Romania's capital city. From the massive Palace of Parliament to the charming Village Museum.",
            "attractions": bucharest_attractions[:2],
            "userId": "demo_user_2",
            "userName": "Ion Ionescu",
            "duration": "1 day",
            "totalDistance": 12.3,
            "likes": 28,
            "views": 89,
            "created": datetime.now().isoformat()
        }

        itinerary_id = fb.create_itinerary(itinerary2)
        print(f"Created sample itinerary: {itinerary2['title']} (ID: {itinerary_id})")

    print("\n✓ Successfully seeded sample itineraries!")

def clear_all_data():
    """Clear all attractions and itineraries (use with caution!)"""
    response = input("⚠️  This will delete ALL attractions and itineraries. Are you sure? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return

    fb = FirebaseService()

    # Get all attractions
    attractions = fb.get_attractions()
    print(f"Deleting {len(attractions)} attractions...")
    for attr in attractions:
        fb.delete_attraction(attr['id'])

    # Get all itineraries
    itineraries = fb.get_itineraries(limit=1000)
    print(f"Deleting {len(itineraries)} itineraries...")
    for itin in itineraries:
        fb.delete_itinerary(itin['id'])

    print("\n✓ All data cleared!")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_all_data()
    elif len(sys.argv) > 1 and sys.argv[1] == '--itineraries-only':
        seed_sample_itineraries()
    else:
        print("=" * 60)
        print("Romanian Tourism Data Seeder")
        print("=" * 60)
        seed_attractions()
        seed_sample_itineraries()
        print("\n" + "=" * 60)
        print("All done! Your database is ready.")
        print("=" * 60)
