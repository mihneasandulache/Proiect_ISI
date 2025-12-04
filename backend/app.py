from flask import Flask, request, jsonify
from flask_cors import CORS
from services.firebase_service import FirebaseService
from services.auth_service import AuthService
from services.route_optimizer import RouteOptimizer
from services.arcgis_service import ArcGISRouteService
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

fb_service = FirebaseService()
auth_service = AuthService()
route_optimizer = RouteOptimizer()
arcgis_service = ArcGISRouteService()

# ============= USERS ENDPOINTS =============

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user (registration)"""
    try:
        data = request.json
        required_fields = ['username', 'email', 'password']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if email already exists
        existing_user = fb_service.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400

        data['created'] = datetime.now().isoformat()
        user_id = fb_service.create_user(data)

        return jsonify({'user_id': user_id, 'message': 'User created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        user = fb_service.get_user(user_id)
        if user:
            # Don't send password to client
            user.pop('password', None)
            user['user_id'] = user_id
            return jsonify(user), 200
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    try:
        data = request.json
        data['updated'] = datetime.now().isoformat()

        fb_service.update_user(user_id, data)
        return jsonify({'message': 'User updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= CITIES ENDPOINTS =============

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get all cities"""
    try:
        cities = fb_service.get_cities()
        return jsonify(cities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cities/<city_id>', methods=['GET'])
def get_city(city_id):
    """Get single city by ID"""
    try:
        city = fb_service.get_city(city_id)
        if city:
            return jsonify(city), 200
        return jsonify({'error': 'City not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cities', methods=['POST'])
def create_city():
    """Create new city"""
    try:
        data = request.json
        required_fields = ['name']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        data['created'] = datetime.now().isoformat()
        city_id = fb_service.create_city(data)

        return jsonify({'city_id': city_id, 'message': 'City created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ATTRACTIONS ENDPOINTS =============

@app.route('/api/attractions', methods=['GET'])
def get_attractions():
    """Get all attractions with optional filters"""
    city_id = request.args.get('city_id')
    attraction_type = request.args.get('type')

    try:
        attractions = fb_service.get_attractions(city_id=city_id, attraction_type=attraction_type)
        return jsonify(attractions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attractions/<attraction_id>', methods=['GET'])
def get_attraction(attraction_id):
    """Get single attraction by ID"""
    try:
        attraction = fb_service.get_attraction(attraction_id)
        if attraction:
            return jsonify(attraction), 200
        return jsonify({'error': 'Attraction not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attractions', methods=['POST'])
def create_attraction():
    """Create new attraction"""
    try:
        data = request.json
        required_fields = ['name', 'description', 'type', 'location', 'city_id']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        data['created'] = datetime.now().isoformat()
        attraction_id = fb_service.create_attraction(data)

        return jsonify({'attraction_id': attraction_id, 'message': 'Attraction created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attractions/<attraction_id>', methods=['PUT'])
def update_attraction(attraction_id):
    """Update existing attraction"""
    try:
        data = request.json
        data['updated'] = datetime.now().isoformat()

        fb_service.update_attraction(attraction_id, data)
        return jsonify({'message': 'Attraction updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attractions/<attraction_id>', methods=['DELETE'])
def delete_attraction(attraction_id):
    """Delete attraction"""
    try:
        fb_service.delete_attraction(attraction_id)
        return jsonify({'message': 'Attraction deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= REVIEWS ENDPOINTS =============

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Get reviews with optional filters"""
    attraction_id = request.args.get('attraction_id')
    user_id = request.args.get('user_id')

    try:
        reviews = fb_service.get_reviews(attraction_id=attraction_id, user_id=user_id)
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    """Get single review by ID"""
    try:
        review = fb_service.get_review(review_id)
        if review:
            return jsonify(review), 200
        return jsonify({'error': 'Review not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews', methods=['POST'])
def create_review():
    """Create new review"""
    try:
        data = request.json
        required_fields = ['user_id', 'attraction_id', 'rating', 'comment']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate rating
        if not (1 <= data['rating'] <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        data['created'] = datetime.now().isoformat()
        review_id = fb_service.create_review(data)

        return jsonify({'review_id': review_id, 'message': 'Review created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews/<review_id>', methods=['PUT'])
def update_review(review_id):
    """Update existing review"""
    try:
        data = request.json
        data['updated'] = datetime.now().isoformat()

        # Validate rating if provided
        if 'rating' in data and not (1 <= data['rating'] <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        fb_service.update_review(review_id, data)
        return jsonify({'message': 'Review updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    """Delete review"""
    try:
        fb_service.delete_review(review_id)
        return jsonify({'message': 'Review deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ITINERARIES ENDPOINTS =============

@app.route('/api/itineraries', methods=['GET'])
def get_itineraries():
    """Get itineraries feed"""
    user_id = request.args.get('userId')
    limit = int(request.args.get('limit', 20))

    try:
        itineraries = fb_service.get_itineraries(limit=limit, user_id=user_id)
        return jsonify(itineraries), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/itineraries/<itinerary_id>', methods=['GET'])
def get_itinerary(itinerary_id):
    """Get single itinerary by ID"""
    try:
        itinerary = fb_service.get_itinerary(itinerary_id)
        if itinerary:
            # Increment views
            fb_service.increment_views(itinerary_id)
            return jsonify(itinerary), 200
        return jsonify({'error': 'Itinerary not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/itineraries', methods=['POST'])
def create_itinerary():
    """Create new itinerary"""
    try:
        data = request.json
        required_fields = ['title', 'description', 'attractions', 'userId', 'userName']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Initialize metadata
        data['created'] = datetime.now().isoformat()
        data['likes'] = 0
        data['views'] = 0

        itinerary_id = fb_service.create_itinerary(data)

        return jsonify({'id': itinerary_id, 'message': 'Itinerary created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/itineraries/<itinerary_id>', methods=['PUT'])
def update_itinerary(itinerary_id):
    """Update existing itinerary"""
    try:
        data = request.json
        data['updated'] = datetime.now().isoformat()

        fb_service.update_itinerary(itinerary_id, data)
        return jsonify({'message': 'Itinerary updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/itineraries/<itinerary_id>', methods=['DELETE'])
def delete_itinerary(itinerary_id):
    """Delete itinerary"""
    try:
        fb_service.delete_itinerary(itinerary_id)
        return jsonify({'message': 'Itinerary deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/itineraries/<itinerary_id>/like', methods=['POST'])
def like_itinerary(itinerary_id):
    """Increment likes for itinerary"""
    try:
        success = fb_service.increment_likes(itinerary_id)
        if success:
            return jsonify({'message': 'Itinerary liked'}), 200
        return jsonify({'error': 'Itinerary not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= HEALTH CHECK =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Romania Tourism API'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
