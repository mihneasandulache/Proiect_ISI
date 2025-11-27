from flask import Flask, request, jsonify
from flask_cors import CORS
from services.firebase_service import FirebaseService
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

fb_service = FirebaseService()

# ============= ATTRACTIONS ENDPOINTS =============

@app.route('/api/attractions', methods=['GET'])
def get_attractions():
    """Get all attractions with optional filters"""
    category = request.args.get('category')
    region = request.args.get('region')
    city = request.args.get('city')

    try:
        attractions = fb_service.get_attractions(category=category, region=region, city=city)
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
        required_fields = ['name', 'latitude', 'longitude', 'category', 'city', 'region']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        data['created'] = datetime.now().isoformat()
        attraction_id = fb_service.create_attraction(data)

        return jsonify({'id': attraction_id, 'message': 'Attraction created'}), 201
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
