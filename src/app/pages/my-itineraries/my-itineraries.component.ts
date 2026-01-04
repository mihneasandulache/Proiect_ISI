import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService, Itinerary } from '../../services/api.service';
import { AuthService, User } from '../../services/auth.service';

@Component({
  selector: 'app-my-itineraries',
  templateUrl: './my-itineraries.component.html',
  styleUrls: ['./my-itineraries.component.scss']
})
export class MyItinerariesComponent implements OnInit {
  itineraries: Itinerary[] = [];
  isLoading = true;
  errorMessage = '';
  currentUser: User | null = null;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
      if (user) {
        this.loadItineraries(user.user_id);
      } else {
        this.isLoading = false;
      }
    });
  }

  loadItineraries(userId: string): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.apiService.getItineraries(userId).subscribe({
      next: (itineraries) => {
        this.itineraries = itineraries;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading itineraries:', err);
        this.errorMessage = 'Could not load your itineraries.';
        this.isLoading = false;
      }
    });
  }

  goToMap(): void {
    this.router.navigate(['/map']);
  }
}
