import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';

export interface User {
  user_id?: string;
  username: string;
  email: string;
  password?: string;
  travel_preferences?: string;
  created?: string;
}

export interface City {
  city_id?: string;
  name: string;
  region?: string;
  description?: string;
  latitude?: number;
  longitude?: number;
  attractions_info?: string;
  events?: string;
  created?: string;
}

export interface Attraction {
  attraction_id?: string;
  name: string;
  description: string;
  type: string;
  location: {
    latitude: number;
    longitude: number;
  };
  city_id: string;
  address?: string;
  imageUrl?: string;
  created?: string;
}

export interface Review {
  review_id?: string;
  user_id: string;
  attraction_id: string;
  rating: number;
  comment: string;
  created?: string;
}

export interface Itinerary {
  id?: string;
  title: string;
  description: string;
  attractions: Attraction[];
  userId: string;
  userName: string;
  duration?: string;
  totalDistance?: number;
  likes?: number;
  views?: number;
  created?: string;
  routeGeometry?: any;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl || 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  // ============= USERS =============

  createUser(user: User): Observable<any> {
    return this.http.post(`${this.apiUrl}/users`, user);
  }

  getUser(userId: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/${userId}`);
  }

  updateUser(userId: string, user: Partial<User>): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/${userId}`, user);
  }

  // ============= CITIES =============

  getCities(): Observable<City[]> {
    return this.http.get<City[]>(`${this.apiUrl}/cities`);
  }

  getCity(cityId: string): Observable<City> {
    return this.http.get<City>(`${this.apiUrl}/cities/${cityId}`);
  }

  createCity(city: City): Observable<any> {
    return this.http.post(`${this.apiUrl}/cities`, city);
  }

  // ============= ATTRACTIONS =============

  getAttractions(filters?: { city_id?: string; type?: string }): Observable<Attraction[]> {
    let params = new HttpParams();
    if (filters) {
      if (filters.city_id) params = params.set('city_id', filters.city_id);
      if (filters.type) params = params.set('type', filters.type);
    }
    return this.http.get<Attraction[]>(`${this.apiUrl}/attractions`, { params });
  }

  getAttraction(attractionId: string): Observable<Attraction> {
    return this.http.get<Attraction>(`${this.apiUrl}/attractions/${attractionId}`);
  }

  createAttraction(attraction: Attraction): Observable<any> {
    return this.http.post(`${this.apiUrl}/attractions`, attraction);
  }

  updateAttraction(attractionId: string, attraction: Partial<Attraction>): Observable<any> {
    return this.http.put(`${this.apiUrl}/attractions/${attractionId}`, attraction);
  }

  deleteAttraction(attractionId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/attractions/${attractionId}`);
  }

  // ============= REVIEWS =============

  getReviews(filters?: { attraction_id?: string; user_id?: string }): Observable<Review[]> {
    let params = new HttpParams();
    if (filters) {
      if (filters.attraction_id) params = params.set('attraction_id', filters.attraction_id);
      if (filters.user_id) params = params.set('user_id', filters.user_id);
    }
    return this.http.get<Review[]>(`${this.apiUrl}/reviews`, { params });
  }

  getReview(reviewId: string): Observable<Review> {
    return this.http.get<Review>(`${this.apiUrl}/reviews/${reviewId}`);
  }

  createReview(review: Review): Observable<any> {
    return this.http.post(`${this.apiUrl}/reviews`, review);
  }

  updateReview(reviewId: string, review: Partial<Review>): Observable<any> {
    return this.http.put(`${this.apiUrl}/reviews/${reviewId}`, review);
  }

  deleteReview(reviewId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/reviews/${reviewId}`);
  }

  // ============= ITINERARIES =============

  getItineraries(userId?: string, limit?: number): Observable<Itinerary[]> {
    let params = new HttpParams();
    if (userId) params = params.set('userId', userId);
    if (limit) params = params.set('limit', limit.toString());
    return this.http.get<Itinerary[]>(`${this.apiUrl}/itineraries`, { params });
  }

  getItinerary(id: string): Observable<Itinerary> {
    return this.http.get<Itinerary>(`${this.apiUrl}/itineraries/${id}`);
  }

  createItinerary(itinerary: Itinerary): Observable<any> {
    return this.http.post(`${this.apiUrl}/itineraries`, itinerary);
  }

  updateItinerary(id: string, itinerary: Partial<Itinerary>): Observable<any> {
    return this.http.put(`${this.apiUrl}/itineraries/${id}`, itinerary);
  }

  deleteItinerary(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/itineraries/${id}`);
  }

  likeItinerary(id: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/itineraries/${id}/like`, {});
  }

  // ============= TOURISM =============

  getTourismConfig(): Observable<any> {
    return this.http.get(`${this.apiUrl}/tourism/config`);
  }

  getTourismLayerInfo(): Observable<any> {
    return this.http.get(`${this.apiUrl}/tourism/layer-info`);
  }

  getTourismFilter(tourismType: string): Observable<any> {
    let params = new HttpParams().set('type', tourismType);
    return this.http.get(`${this.apiUrl}/tourism/filter`, { params });
  }
}
