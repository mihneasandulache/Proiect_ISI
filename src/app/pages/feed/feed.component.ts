import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService, Itinerary } from '../../services/api.service';

@Component({
  selector: 'app-feed',
  templateUrl: './feed.component.html',
  styleUrls: ['./feed.component.scss']
})
export class FeedComponent implements OnInit {
  itineraries: Itinerary[] = [];
  isLoading = true;
  errorMessage = '';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadFeed();
  }

  loadFeed(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.apiService.getItineraries(undefined, 50, true).subscribe({
      next: (itineraries) => {
        this.itineraries = itineraries;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading feed with posted filter:', err);
        this.loadFeedFallback();
      }
    });
  }

  private loadFeedFallback(): void {
    this.apiService.getItineraries(undefined, 50).subscribe({
      next: (itineraries) => {
        this.itineraries = itineraries.filter(item => item.posted);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading feed fallback:', err);
        this.errorMessage = 'Could not load feed.';
        this.isLoading = false;
      }
    });
  }

  openItineraryOnMap(itinerary: Itinerary): void {
    if (!itinerary.id) {
      this.router.navigate(['/map']);
      return;
    }
    this.router.navigate(['/map'], { queryParams: { itineraryId: itinerary.id } });
  }
}
