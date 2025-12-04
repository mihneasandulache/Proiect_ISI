"""
Route Optimization Service
Implements Nearest Neighbor algorithm starting from user's location
"""
import math
from typing import List, Dict, Optional

class RouteOptimizer:
    def __init__(self):
        self.earth_radius_km = 6371

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon / 2) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = self.earth_radius_km * c

        return distance

    def calculate_optimal_route(self, attractions: List[Dict], start_location: Dict = None) -> Dict:
        """
        Calculate optimal route using Nearest Neighbor algorithm from a starting location

        Args:
            attractions: List of attraction dicts with 'latitude', 'longitude', 'name', 'id'
            start_location: Optional dict with 'latitude', 'longitude', 'name' for starting point
                          If None, starts from first attraction

        Returns:
            Dict containing optimized route, total distance, and segments
        """
        if not attractions:
            return {
                'route': [],
                'total_distance': 0,
                'segments': [],
                'start_location': start_location,
                'algorithm': 'nearest_neighbor'
            }

        if len(attractions) == 1:
            # Single attraction case
            distance_from_start = 0
            segments = []

            if start_location:
                distance_from_start = self.calculate_distance(
                    start_location['latitude'],
                    start_location['longitude'],
                    attractions[0]['latitude'],
                    attractions[0]['longitude']
                )
                segments.append({
                    'from': start_location['name'],
                    'to': attractions[0]['name'],
                    'distance_km': round(distance_from_start, 2)
                })

            return {
                'route': attractions,
                'total_distance': round(distance_from_start, 2),
                'segments': segments,
                'start_location': start_location,
                'algorithm': 'nearest_neighbor'
            }

        # Use starting location if provided, otherwise start from first attraction
        unvisited = list(range(len(attractions)))
        route_order = []
        total_distance = 0
        segments = []

        # Determine first attraction from start location
        if start_location:
            current_lat = start_location['latitude']
            current_lon = start_location['longitude']
            current_name = start_location['name']
        else:
            # Start from first attraction
            current_lat = attractions[0]['latitude']
            current_lon = attractions[0]['longitude']
            current_name = attractions[0]['name']
            route_order.append(0)
            unvisited.remove(0)

        # Visit nearest unvisited attraction at each step
        while unvisited:
            nearest_idx = None
            nearest_distance = float('inf')

            # Find nearest unvisited attraction
            for idx in unvisited:
                candidate = attractions[idx]
                distance = self.calculate_distance(
                    current_lat,
                    current_lon,
                    candidate['latitude'],
                    candidate['longitude']
                )

                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_idx = idx

            # Move to nearest attraction
            nearest_attraction = attractions[nearest_idx]
            segments.append({
                'from': current_name,
                'to': nearest_attraction['name'],
                'distance_km': round(nearest_distance, 2)
            })

            route_order.append(nearest_idx)
            total_distance += nearest_distance

            # Update current position
            current_lat = nearest_attraction['latitude']
            current_lon = nearest_attraction['longitude']
            current_name = nearest_attraction['name']

            unvisited.remove(nearest_idx)

        # Build ordered route
        ordered_route = [attractions[idx] for idx in route_order]

        return {
            'route': ordered_route,
            'total_distance': round(total_distance, 2),
            'segments': segments,
            'start_location': start_location,
            'algorithm': 'nearest_neighbor'
        }

    def calculate_route_geometry(self, route: List[Dict], start_location: Dict = None) -> List[List[float]]:
        """
        Generate route geometry as list of [longitude, latitude] pairs

        Args:
            route: List of attractions in order
            start_location: Optional starting location to include

        Returns:
            List of [lon, lat] coordinate pairs
        """
        geometry = []

        # Add start location if provided
        if start_location:
            geometry.append([start_location['longitude'], start_location['latitude']])

        # Add all attractions in route order
        for attraction in route:
            geometry.append([attraction['longitude'], attraction['latitude']])

        return geometry
