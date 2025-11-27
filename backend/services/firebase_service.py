# backend/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, db
import os
import json

class FirebaseService:
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            # Load credentials from JSON file
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json')

            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Firebase credentials file not found at {credentials_path}. "
                    "Please download your service account key from Firebase Console and save it as "
                    "'backend/firebase-credentials.json'"
                )

            cred = credentials.Certificate(credentials_path)

            # Load the credentials to get database URL
            with open(credentials_path, 'r') as f:
                cred_data = json.load(f)
                project_id = cred_data.get('project_id')
                database_url = f'https://{project_id}-default-rtdb.firebaseio.com/'

            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })

        self.db = db.reference()
    
    # ============= USERS =============

    def get_user(self, user_id):
        """Get single user by ID"""
        ref = self.db.child('users').child(user_id)
        return ref.get()

    def get_user_by_email(self, email):
        """Get user by email"""
        ref = self.db.child('users')
        users = ref.order_by_child('email').equal_to(email).get()
        if users:
            for key, value in users.items():
                value['user_id'] = key
                return value
        return None

    def create_user(self, data):
        """Create new user"""
        ref = self.db.child('users')
        new_ref = ref.push(data)
        return new_ref.key

    def update_user(self, user_id, data):
        """Update existing user"""
        ref = self.db.child('users').child(user_id)
        ref.update(data)
        return True

    def delete_user(self, user_id):
        """Delete user"""
        ref = self.db.child('users').child(user_id)
        ref.delete()
        return True

    # ============= CITIES =============

    def get_cities(self):
        """Get all cities"""
        ref = self.db.child('cities')
        cities = ref.get()

        if not cities:
            return []

        result = []
        for key, value in cities.items():
            value['city_id'] = key
            result.append(value)

        return result

    def get_city(self, city_id):
        """Get single city by ID"""
        ref = self.db.child('cities').child(city_id)
        city = ref.get()

        if city:
            city['city_id'] = city_id

        return city

    def create_city(self, data):
        """Create new city"""
        ref = self.db.child('cities')
        new_ref = ref.push(data)
        return new_ref.key

    def update_city(self, city_id, data):
        """Update existing city"""
        ref = self.db.child('cities').child(city_id)
        ref.update(data)
        return True

    def delete_city(self, city_id):
        """Delete city"""
        ref = self.db.child('cities').child(city_id)
        ref.delete()
        return True

    # ============= ATTRACTIONS =============

    def get_attractions(self, city_id=None, attraction_type=None):
        """Get all attractions with optional filters"""
        ref = self.db.child('attractions')

        if city_id:
            attractions = ref.order_by_child('city_id').equal_to(city_id).get()
        else:
            attractions = ref.get()

        if not attractions:
            return []

        # Convert to list with IDs
        result = []
        for key, value in attractions.items():
            value['attraction_id'] = key
            result.append(value)

        # Apply type filter
        if attraction_type:
            result = [a for a in result if a.get('type') == attraction_type]

        return result

    def get_attraction(self, attraction_id):
        """Get single attraction by ID"""
        ref = self.db.child('attractions').child(attraction_id)
        attraction = ref.get()

        if attraction:
            attraction['attraction_id'] = attraction_id

        return attraction

    def create_attraction(self, data):
        """Create new attraction"""
        ref = self.db.child('attractions')
        new_ref = ref.push(data)
        return new_ref.key

    def update_attraction(self, attraction_id, data):
        """Update existing attraction"""
        ref = self.db.child('attractions').child(attraction_id)
        ref.update(data)
        return True

    def delete_attraction(self, attraction_id):
        """Delete attraction"""
        ref = self.db.child('attractions').child(attraction_id)
        ref.delete()
        return True

    # ============= REVIEWS =============

    def get_reviews(self, attraction_id=None, user_id=None):
        """Get reviews with optional filters"""
        ref = self.db.child('reviews')

        if attraction_id:
            reviews = ref.order_by_child('attraction_id').equal_to(attraction_id).get()
        elif user_id:
            reviews = ref.order_by_child('user_id').equal_to(user_id).get()
        else:
            reviews = ref.get()

        if not reviews:
            return []

        result = []
        for key, value in reviews.items():
            value['review_id'] = key
            result.append(value)

        return result

    def get_review(self, review_id):
        """Get single review by ID"""
        ref = self.db.child('reviews').child(review_id)
        review = ref.get()

        if review:
            review['review_id'] = review_id

        return review

    def create_review(self, data):
        """Create new review"""
        ref = self.db.child('reviews')
        new_ref = ref.push(data)
        return new_ref.key

    def update_review(self, review_id, data):
        """Update existing review"""
        ref = self.db.child('reviews').child(review_id)
        ref.update(data)
        return True

    def delete_review(self, review_id):
        """Delete review"""
        ref = self.db.child('reviews').child(review_id)
        ref.delete()
        return True
    
    # ============= ITINERARIES =============
    
    def get_itineraries(self, limit=20, user_id=None):
        """Get itineraries for feed"""
        ref = self.db.child('itineraries')
        
        if user_id:
            # Get user's itineraries
            itineraries = ref.order_by_child('userId').equal_to(user_id).get()
        else:
            # Get all itineraries (for feed)
            itineraries = ref.order_by_child('created').limit_to_last(limit).get()
        
        if not itineraries:
            return []
        
        # Convert to list with IDs
        result = []
        for key, value in itineraries.items():
            value['id'] = key
            result.append(value)
        
        # Sort by created date (newest first)
        result.sort(key=lambda x: x.get('created', ''), reverse=True)
        
        return result
    
    def get_itinerary(self, itinerary_id):
        """Get single itinerary by ID"""
        ref = self.db.child('itineraries').child(itinerary_id)
        itinerary = ref.get()
        
        if itinerary:
            itinerary['id'] = itinerary_id
        
        return itinerary
    
    def create_itinerary(self, data):
        """Create new itinerary"""
        ref = self.db.child('itineraries')
        new_ref = ref.push(data)
        return new_ref.key
    
    def update_itinerary(self, itinerary_id, data):
        """Update existing itinerary"""
        ref = self.db.child('itineraries').child(itinerary_id)
        ref.update(data)
        return True
    
    def delete_itinerary(self, itinerary_id):
        """Delete itinerary"""
        ref = self.db.child('itineraries').child(itinerary_id)
        ref.delete()
        return True
    
    def increment_likes(self, itinerary_id):
        """Increment likes count"""
        ref = self.db.child('itineraries').child(itinerary_id)
        itinerary = ref.get()
        
        if itinerary:
            current_likes = itinerary.get('likes', 0)
            ref.update({'likes': current_likes + 1})
            return True
        
        return False
    
    def increment_views(self, itinerary_id):
        """Increment views count"""
        ref = self.db.child('itineraries').child(itinerary_id)
        itinerary = ref.get()
        
        if itinerary:
            current_views = itinerary.get('views', 0)
            ref.update({'views': current_views + 1})
            return True
        
        return False