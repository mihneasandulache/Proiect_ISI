# backend/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, db
import os
import json

class FirebaseService:
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        # Use environment variable or service account file
        if not firebase_admin._apps:
            # For local development
            if os.path.exists('firebase-credentials.json'):
                cred = credentials.Certificate('firebase-credentials.json')
            else:
                # For deployment (use environment variables)
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                })
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', 
                    'https://isc-proiect-default-rtdb.firebaseio.com/')
            })
        
        self.db = db.reference()
    
    # ============= ATTRACTIONS =============
    
    def get_attractions(self, category=None, region=None, city=None):
        """Get all attractions with optional filters"""
        ref = self.db.child('attractions')
        attractions = ref.get()
        
        if not attractions:
            return []
        
        # Convert to list with IDs
        result = []
        for key, value in attractions.items():
            value['id'] = key
            result.append(value)
        
        # Apply filters
        if category:
            result = [a for a in result if a.get('category') == category]
        if region:
            result = [a for a in result if a.get('region') == region]
        if city:
            result = [a for a in result if a.get('city') == city]
        
        return result
    
    def get_attraction(self, attraction_id):
        """Get single attraction by ID"""
        ref = self.db.child('attractions').child(attraction_id)
        attraction = ref.get()
        
        if attraction:
            attraction['id'] = attraction_id
        
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