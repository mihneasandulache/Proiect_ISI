#!/usr/bin/env python3
"""
Seed script to populate Firebase with Romanian cities, attractions, users, and reviews
"""
import json
import os
from services.firebase_service import FirebaseService
from datetime import datetime
import hashlib

def hash_password(password):
    """Simple password hashing (in production, use bcrypt or similar)"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_json_file(file_path):
    """Load data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def seed_cities(fb):
    """Seed cities data"""
    print("\n=== Seeding Cities ===")
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'romanian_cities.json')
    cities = load_json_file(json_path)

    city_ids = {}
    for i, city in enumerate(cities, 1):
        city['created'] = datetime.now().isoformat()
        city_id = fb.create_city(city)
        city_ids[city['name']] = city_id
        print(f"[{i}/{len(cities)}] Added city: {city['name']} (ID: {city_id})")

    return city_ids

def seed_attractions(fb, city_ids):
    """Seed attractions data with city references"""
    print("\n=== Seeding Attractions ===")

    attractions_data = [
        {
            "name": "Bran Castle",
            "description": "Famous medieval castle, commonly known as Dracula's Castle. Built in 1377, it's one of Romania's most iconic landmarks.",
            "type": "Historical Monument",
            "location": {"latitude": 45.5150, "longitude": 25.3673},
            "city_name": "Brașov",
            "address": "Strada General Traian Moșoiu 24, Bran 507025",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Bran_Castle.jpg/800px-Bran_Castle.jpg"
        },
        {
            "name": "Palace of Parliament",
            "description": "The world's second-largest administrative building. A massive example of totalitarian architecture.",
            "type": "Historical Monument",
            "location": {"latitude": 44.4276, "longitude": 26.0875},
            "city_name": "Bucharest",
            "address": "Strada Izvor 2-4, București 050563",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Bucharest_Parliament.jpg/800px-Bucharest_Parliament.jpg"
        },
        {
            "name": "Peleș Castle",
            "description": "Neo-Renaissance castle built between 1873-1914 as a summer residence for King Carol I.",
            "type": "Historical Monument",
            "location": {"latitude": 45.3599, "longitude": 25.5429},
            "city_name": "Sinaia",
            "address": "Aleea Peleșului 2, Sinaia 106100",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/RO_PH_Peles_Castle.jpg/800px-RO_PH_Peles_Castle.jpg"
        },
        {
            "name": "Sighișoara Citadel",
            "description": "UNESCO World Heritage Site. Best-preserved inhabited medieval citadel in Europe.",
            "type": "Historical Monument",
            "location": {"latitude": 46.2191, "longitude": 24.7914},
            "city_name": "Sighișoara",
            "address": "Strada Tamplarilor 1, Sighișoara 545400",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Sighisoara_Citadel.jpg/800px-Sighisoara_Citadel.jpg"
        },
        {
            "name": "National Museum of Art of Romania",
            "description": "Main art museum in Romania, housed in the former royal palace.",
            "type": "Museum",
            "location": {"latitude": 44.4392, "longitude": 26.0965},
            "city_name": "Bucharest",
            "address": "Calea Victoriei 49-53, București 010063",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/National_Museum_of_Art_Bucharest.jpg/800px-National_Museum_of_Art_Bucharest.jpg"
        },
        {
            "name": "Black Church (Biserica Neagră)",
            "description": "Largest Gothic church in Romania, built between 1385-1477.",
            "type": "Religious Site",
            "location": {"latitude": 45.6416, "longitude": 25.5886},
            "city_name": "Brașov",
            "address": "Curtea Johannes Honterus 2, Brașov 500025",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Black_Church_Brasov.jpg/800px-Black_Church_Brasov.jpg"
        },
        {
            "name": "Romanian Athenaeum",
            "description": "Concert hall in Bucharest, headquarters of the Romanian Philharmonic. Iconic neoclassical building opened in 1888.",
            "type": "Cultural Site",
            "location": {"latitude": 44.4413, "longitude": 26.0974},
            "city_name": "Bucharest",
            "address": "Strada Benjamin Franklin 1-3, București 030167",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Romanian_Athenaeum.jpg/800px-Romanian_Athenaeum.jpg"
        },
        {
            "name": "Village Museum (Muzeul Satului)",
            "description": "Open-air museum showcasing traditional Romanian village life. Features over 300 authentic peasant farms.",
            "type": "Museum",
            "location": {"latitude": 44.4719, "longitude": 26.0756},
            "city_name": "Bucharest",
            "address": "Șoseaua Pavel Dimitrievici Kiseleff 28-30, București 011347",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Village_Museum_Bucharest.jpg/800px-Village_Museum_Bucharest.jpg"
        },
        {
            "name": "Council Square (Piața Sfatului)",
            "description": "Historic medieval square in the heart of Brașov Old Town.",
            "type": "Historical Site",
            "location": {"latitude": 45.6427, "longitude": 25.5887},
            "city_name": "Brașov",
            "address": "Piața Sfatului, Brașov 500025",
            "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Brasov_Council_Square.jpg/800px-Brasov_Council_Square.jpg"
        },
        {
            "name": "Sinaia Monastery",
            "description": "17th-century monastery that gave the town its name, beautiful Orthodox architecture.",
            "type": "Religious Site",
            "location": {"latitude": 45.3509, "longitude": 25.5478},
            "city_name": "Sinaia",
            "address": "Mănăstirea Sinaia, Sinaia 106100",
            "imageUrl": "https://example.com/sinaia-monastery.jpg"
        }
    ]

    attraction_ids = []
    for i, attraction in enumerate(attractions_data, 1):
        city_name = attraction.pop('city_name')
        if city_name in city_ids:
            attraction['city_id'] = city_ids[city_name]
            attraction['created'] = datetime.now().isoformat()
            attraction_id = fb.create_attraction(attraction)
            attraction_ids.append(attraction_id)
            print(f"[{i}/{len(attractions_data)}] Added: {attraction['name']} (ID: {attraction_id})")
        else:
            print(f"[{i}/{len(attractions_data)}] Skipped {attraction['name']} - city not found")

    return attraction_ids

def seed_users(fb):
    """Seed sample users"""
    print("\n=== Seeding Users ===")

    users_data = [
        {
            "username": "maria_popescu",
            "email": "maria.popescu@example.com",
            "password": hash_password("password123"),
            "travel_preferences": "History, Architecture, Museums",
            "created": datetime.now().isoformat()
        },
        {
            "username": "ion_ionescu",
            "email": "ion.ionescu@example.com",
            "password": hash_password("password123"),
            "travel_preferences": "Nature, Hiking, Photography",
            "created": datetime.now().isoformat()
        },
        {
            "username": "ana_tudor",
            "email": "ana.tudor@example.com",
            "password": hash_password("password123"),
            "travel_preferences": "Culture, Food, Local experiences",
            "created": datetime.now().isoformat()
        }
    ]

    user_ids = []
    for i, user in enumerate(users_data, 1):
        user_id = fb.create_user(user)
        user_ids.append(user_id)
        print(f"[{i}/{len(users_data)}] Added user: {user['username']} (ID: {user_id})")

    return user_ids

def seed_reviews(fb, user_ids, attraction_ids):
    """Seed sample reviews"""
    print("\n=== Seeding Reviews ===")

    if len(user_ids) < 2 or len(attraction_ids) < 3:
        print("Not enough users or attractions to create reviews")
        return

    reviews_data = [
        {
            "user_id": user_ids[0],
            "attraction_id": attraction_ids[0],
            "rating": 5,
            "comment": "Amazing castle with incredible history! The views from the top are breathtaking. A must-visit in Romania!"
        },
        {
            "user_id": user_ids[1],
            "attraction_id": attraction_ids[0],
            "rating": 4,
            "comment": "Very interesting place, though it can get quite crowded. The castle itself is beautiful and well-maintained."
        },
        {
            "user_id": user_ids[0],
            "attraction_id": attraction_ids[1],
            "rating": 5,
            "comment": "Absolutely massive building! The guided tour is fascinating and provides great insight into Romania's history."
        },
        {
            "user_id": user_ids[2],
            "attraction_id": attraction_ids[2],
            "rating": 5,
            "comment": "Peleș Castle is like a fairy tale! The interior is stunning with incredible attention to detail. Highly recommended!"
        },
        {
            "user_id": user_ids[1],
            "attraction_id": attraction_ids[3],
            "rating": 4,
            "comment": "Walking through the medieval citadel feels like stepping back in time. Great atmosphere and lovely cafes."
        }
    ]

    for i, review in enumerate(reviews_data, 1):
        review['created'] = datetime.now().isoformat()
        review_id = fb.create_review(review)
        print(f"[{i}/{len(reviews_data)}] Added review (ID: {review_id})")

def clear_all_data(fb):
    """Clear all data from database"""
    response = input("⚠️  This will delete ALL data. Are you sure? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return

    print("\nClearing all data...")

    # Clear reviews
    reviews = fb.get_reviews()
    print(f"Deleting {len(reviews)} reviews...")
    for review in reviews:
        fb.delete_review(review['review_id'])

    # Clear attractions
    attractions = fb.get_attractions()
    print(f"Deleting {len(attractions)} attractions...")
    for attraction in attractions:
        fb.delete_attraction(attraction['attraction_id'])

    # Clear cities
    cities = fb.get_cities()
    print(f"Deleting {len(cities)} cities...")
    for city in cities:
        fb.delete_city(city['city_id'])

    # Clear users (be careful with this!)
    # Commented out for safety
    # users = fb.get_users()
    # print(f"Deleting {len(users)} users...")
    # for user in users:
    #     fb.delete_user(user['user_id'])

    print("\n✓ Data cleared!")

if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("Romanian Tourism Database Seeder")
    print("=" * 60)

    fb = FirebaseService()

    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_all_data(fb)
    else:
        city_ids = seed_cities(fb)
        attraction_ids = seed_attractions(fb, city_ids)
        user_ids = seed_users(fb)
        seed_reviews(fb, user_ids, attraction_ids)

        print("\n" + "=" * 60)
        print("All done! Your database is ready.")
        print("=" * 60)
        print(f"\nSeeded:")
        print(f"  - {len(city_ids)} cities")
        print(f"  - {len(attraction_ids)} attractions")
        print(f"  - {len(user_ids)} users")
        print(f"  - Sample reviews")
