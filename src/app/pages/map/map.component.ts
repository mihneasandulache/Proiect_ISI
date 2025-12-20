import {
  Component,
  OnInit,
  ViewChild,
  ElementRef,
  Output,
  EventEmitter,
  OnDestroy
} from "@angular/core";

import esri = __esri; // Esri TypeScript Types

import Config from '@arcgis/core/config';
import WebMap from '@arcgis/core/WebMap';
import MapView from '@arcgis/core/views/MapView';
import Bookmarks from '@arcgis/core/widgets/Bookmarks';
import Expand from '@arcgis/core/widgets/Expand';

import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer";
import Graphic from '@arcgis/core/Graphic';
import Point from '@arcgis/core/geometry/Point';

import FeatureLayer from '@arcgis/core/layers/FeatureLayer';

import Polygon from '@arcgis/core/geometry/Polygon';
import Polyline from '@arcgis/core/geometry/Polyline';

import Search from '@arcgis/core/widgets/Search';
import * as route from '@arcgis/core/rest/route';
import RouteParameters from '@arcgis/core/rest/support/RouteParameters';
import FeatureSet from '@arcgis/core/rest/support/FeatureSet';
import { FirebaseService } from '../../services/firebase.service';
import { ApiService, Attraction } from '../../services/api.service';
import { Router } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';


@Component({
  selector: "app-map",
  templateUrl: "./map.component.html",
  styleUrls: ["./map.component.scss"]
})
export class MapComponent implements OnInit, OnDestroy {
  @Output() mapLoadedEvent = new EventEmitter<boolean>();

  @ViewChild("mapViewNode", { static: true }) private mapViewEl: ElementRef;

  map: esri.Map;
  view: esri.MapView;
  graphicsLayer: esri.GraphicsLayer;
  trailheadsLayer: esri.FeatureLayer;
  tourismLayer: esri.FeatureLayer;
  countiesLayer: esri.FeatureLayer;

  // Tourism attraction filter options (excluding accommodations)
  tourismFilterOptions = [
    { value: "all", label: "All Attractions", selected: true },
    { value: "museum", label: "Museums", selected: false },
    { value: "attraction", label: "Tourist Attractions", selected: false },
    { value: "viewpoint", label: "Viewpoints", selected: false },
    { value: "artwork", label: "Artwork", selected: false },
    { value: "gallery", label: "Galleries", selected: false },
    { value: "theme_park", label: "Theme Parks", selected: false },
    { value: "zoo", label: "Zoos", selected: false },
    { value: "aquarium", label: "Aquariums", selected: false },
    { value: "picnic_site", label: "Picnic Sites", selected: false }
  ];

  selectedTourismFilter: string = "all";

  zoom = 10;
  center: Array<number> = [26.1025, 44.4268];
  basemap = "streets-vector";
  loaded = false;
  currentUser: User | null = null; //
  selectedStops: Attraction[] = [];
  routeLoading: boolean = false;
  totalDistance: number = 0;

  // Directions panel
  showDirections: boolean = false;
  directions: any[] = [];
  routeSummary: { distance: string, time: string } | null = null;

  routeGraphicsLayer: esri.GraphicsLayer;

  constructor(
    private fb: FirebaseService,
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router
  ) { }
  private firebaseUnsubscribe: (() => void) | null = null;
  private userPosUnsubscribe: (() => void) | null = null;
  private clientId: string = 'client_' + Math.random().toString(36).substr(2, 9);
  private lastCenterSent: number = 0;
  private centerSyncTimer: any = null;
  graphicsLayerFirebase: esri.GraphicsLayer;

  ngOnInit() {
    // Load tourism configuration from backend
    this.authService.currentUser.subscribe(user => { //
      this.currentUser = user;
    });

    this.loadTourismConfig();

    this.initializeMap().then(() => {
      this.loaded = this.view.ready;
      this.mapLoadedEvent.emit(true);
    });
  }

  loadTourismConfig() {
    this.apiService.getTourismConfig().subscribe({
      next: (config) => {
        this.tourismFilterOptions = config.filter_options;
        console.log('Tourism config loaded from backend:', config);
      },
      error: (err) => {
        console.error('Error loading tourism config:', err);
      }
    });
  }

  async initializeMap() {
    try {
      Config.apiKey = "AAPTxy8BH1VEsoebNVZXo8HurDPKAq3VaV_xrgUjYre1Pnmwp3O85BVX3fDDKZ1H__qI1kee4d-W5Ai2SSeMCpqWYRpFR_d8YiiRVtGr3WsfTNvUVcuwbnsI6TS9yWTu4Anah6wZlYP73GrnQy_GXhHmnB8lt3sfcc7MpN_MRzvanQ2WjNrxKnBnCuc9DW250fAPPtSyHx31yUN9T5Dh2wlE-DRhGh7RJRYnBBD6IHRhxiY.AT1_4BxOT2Pv";

      const mapProperties: esri.WebMapProperties = {
        basemap: this.basemap
      };
      this.map = new WebMap(mapProperties);

      this.addFeatureLayers();
      this.addGraphicsLayer();
      this.routeGraphicsLayer = new GraphicsLayer({
        id: "route-layer",
        title: "Calculated Route Stops"
      });
      this.map.add(this.routeGraphicsLayer);
      this.addGraphicElements();

      const mapViewProperties = {
        container: this.mapViewEl.nativeElement,
        center: this.center,
        zoom: this.zoom,
        map: this.map
      };
      this.view = new MapView(mapViewProperties);

      this.view.on('pointer-move', ["Shift"], (event) => {
        const point = this.view.toMap({ x: event.x, y: event.y });
        console.log("Map pointer moved: ", point.longitude, point.latitude);
      });

      await this.view.when();
      console.log("ArcGIS map loaded");
      this.setupFirebaseSync();
      this.addSearchWidget();
      return this.view;
    } catch (error) {
      console.error("Error loading the map: ", error);
      alert("Error loading the map");
    }
  }

  addSearchWidget() {
    const search = new Search({
      view: this.view,
      popupEnabled: true
    });

    this.view.ui.add(search, "top-right");
    search.on('select-result', (event) => {
      const result = event.result;
      const geometry = result.feature.geometry as esri.Point;

      if (geometry && geometry.type === 'point') {

        const newAttractionId = `search_${Date.now()}`;

        const newStop: Attraction = {
          attraction_id: newAttractionId,
          name: result.name || 'Locație Căutată',
          location: {
            latitude: geometry.latitude,
            longitude: geometry.longitude
          },
          description: 'Adăugat din căutare',
          type: 'search',
          city_id: 'unknown'
        };

        this.addStopToRoute(newStop);

        search.clear();
      }
    });
  }

  filterTourismAttractions(filterValue: string) {
    this.selectedTourismFilter = filterValue;

    // Get definition expression from backend
    this.apiService.getTourismFilter(filterValue).subscribe({
      next: (response) => {
        const definitionExpression = response.definition_expression;

        if (this.tourismLayer) {
          this.tourismLayer.definitionExpression = definitionExpression;
          console.log("Tourism filter applied:", filterValue, definitionExpression);
        }
      },
      error: (err) => {
        console.error('Error getting tourism filter:', err);
      }
    });
  }

  addGraphicElements() {
    const point = new Point({
      longitude: -118.80657463861,
      latitude: 34.0005930608889,
    });

    const simpleMarkerSymbol = {
      type: "simple-marker",
      color: [226, 119, 40],
      outline: {
        color: [255, 255, 255],
        width: 1,
      },
    };

    const pointGraphic = new Graphic({
      geometry: point,
      symbol: simpleMarkerSymbol
    });
    this.graphicsLayer.add(pointGraphic);

    const polyline = new Polyline({
      paths: [
        [
          [-118.821527826096, 34.0139576938577],
          [-118.814893761649, 34.0080602407843],
          [-118.808878330345, 34.0016642996246]
        ]
      ]
    });

    const simpleLineSymbol = {
      type: "simple-line",
      color: [226, 119, 40],
      width: 2,
    };

    const polylineGraphic = new Graphic({
      geometry: polyline,
      symbol: simpleLineSymbol
    });
    this.graphicsLayer.add(polylineGraphic);

    const polygon = new Polygon({
      rings: [
        [
          [-118.818984489994, 34.0137559967283],
          [-118.806796597377, 34.0215816298725],
          [-118.791432890735, 34.0163883241613],
          [-118.79596686535, 34.008564864635],
          [-118.808558110679, 34.0035027131376],
          [-118.818984489994, 34.0137559967283]
        ]
      ],
    });

    const simpleFillSymbol = {
      type: "simple-fill",
      color: [227, 139, 79, 0.8],
      outline: {
        color: [255, 255, 255],
        width: 1
      },
    };

    const polygonGraphic = new Graphic({
      geometry: polygon,
      symbol: simpleFillSymbol,
    });
    this.graphicsLayer.add(polygonGraphic);

    console.log("Lab 02 graphics added: point, polyline, and polygon");
  }

  toggleGraphics() {
    this.graphicsLayer.visible = !this.graphicsLayer.visible;
    console.log("Graphics visibility:", this.graphicsLayer.visible);
  }

  addFeatureLayers() {
    this.trailheadsLayer = new FeatureLayer({
      url: "https://services3.arcgis.com/GVgbJbqm8hXASVYi/arcgis/rest/services/Trailheads/FeatureServer/0",
      outFields: ['*']
    });
    this.map.add(this.trailheadsLayer);

    const trailsLayer = new FeatureLayer({
      url: "https://services3.arcgis.com/GVgbJbqm8hXASVYi/arcgis/rest/services/Trails/FeatureServer/0"
    });
    this.map.add(trailsLayer, 0);
    this.countiesLayer = new FeatureLayer({
      url: "https://services2.arcgis.com/T4rPchMqQ2Fwj1pR/arcgis/rest/services/Judete_Romania/FeatureServer/0",
      title: "Romanian Counties",
      outFields: ["*"],
      opacity: 0.6,
      renderer: {
        type: "simple",
        symbol: {
          type: "simple-fill",
          color: [51, 51, 204, 0.2],
          outline: {
            color: [40, 40, 120, 0.8],
            width: 2
          }
        }
      } as any,
      popupTemplate: {
        title: "{JUDET}",
        content: [{
          type: "fields",
          fieldInfos: [
            {
              fieldName: "JUDET",
              label: "County Name"
            }
          ]
        }]
      } as any
    });
    this.map.add(this.countiesLayer, 0);
    // Add OpenStreetMap Tourism Layer for Europe (includes Romania)
    // Exclude all accommodation types
    const excludeAccommodation = "tourism NOT IN ('apartment', 'camp_pitch', 'camp_site', 'caravan_site', 'chalet', 'guest_house', 'hostel', 'hotel', 'motel', 'trail_riding_station')";

    this.tourismLayer = new FeatureLayer({
      url: "https://services-eu1.arcgis.com/zci5bUiJ8olAal7N/arcgis/rest/services/OSM_EU_Tourism/FeatureServer/0",
      title: "Romanian Tourist Attractions",
      outFields: ["name", "tourism", "historic", "amenity", "description", "opening_hours", "website", "phone"],
      definitionExpression: `name IS NOT NULL AND ${excludeAccommodation}`,
      popupTemplate: {
        title: "{name}",
        content: `
          <div style="padding: 10px;">
            <p><strong>Type:</strong> {tourism} {historic} {amenity}</p>
            <p><strong>Description:</strong> {description}</p>
            <p><strong>Opening Hours:</strong> {opening_hours}</p>
            <p><strong>Website:</strong> {website}</p>
            <p><strong>Phone:</strong> {phone}</p>
          </div>
          <div class="popup-review-controls">
            <div class="review-stats">
            </div>
            <div class="review-actions">
              <a 
                href="#" 
                class="btn btn-primary" 
                style="color: white; text-decoration: none; margin-right: 8px;"
              >
                Visit
              </a>
              <a 
                href="#/attractions/{OBJECTID}/reviews?name={name}" 
                class="btn btn-primary" 
                data-attraction-id="{OBJECTID}"
                style="color: white; text-decoration: none;"
              >
                View Reviews
              </a>
            </div>
          </div>
        `
      }
    } as any);
    this.map.add(this.tourismLayer);

    console.log("Feature layers added including Romanian tourism layer");
  }

  addGraphicsLayer() {
    this.graphicsLayer = new GraphicsLayer();
    this.map.add(this.graphicsLayer);

    this.graphicsLayerFirebase = new GraphicsLayer({ title: 'Firebase Points' });
    this.map.add(this.graphicsLayerFirebase);
  }

  // Route calculation is handled by backend algorithm
  // Points and routes are managed through your custom route optimizer service

  setupFirebaseSync() {
    this.firebaseUnsubscribe = this.fb.subscribePoints((data) => {
      if (this.graphicsLayerFirebase) {
        this.graphicsLayerFirebase.removeAll();
      }
      if (!data) return;
      Object.keys(data).forEach((k) => {
        const p: any = data[k];
        if (!p || typeof p.lat !== 'number' || typeof p.lng !== 'number') return;
        const point = new Point({ longitude: p.lng, latitude: p.lat });
        const symbol = {
          type: 'simple-marker',
          color: [0, 120, 255],
          outline: { color: [255, 255, 255], width: 1 },
          size: 10
        };
        const g = new Graphic({ geometry: point, symbol, attributes: { ...p, id: k } });
        this.graphicsLayerFirebase.add(g);
      });
    });

    this.centerSyncTimer = setInterval(() => {
      if (!this.view || !this.view.center) return;
      const center = this.view.center as any;
      const now = Date.now();
      if (now - this.lastCenterSent < 1000) return;
      this.lastCenterSent = now;
      try {
        this.fb.updateUserPosition(this.clientId, { lat: center.latitude, lng: center.longitude, timestamp: now });
      } catch (err) {
        console.error('Error updating user position to Firebase', err);
      }
    }, 1000);
  }

  ngOnDestroy() {
    if (this.view) {
      this.view.container = null;
    }
    if (this.firebaseUnsubscribe) {
      this.firebaseUnsubscribe();
      this.firebaseUnsubscribe = null;
    }
    if (this.userPosUnsubscribe) {
      this.userPosUnsubscribe();
      this.userPosUnsubscribe = null;
    }
    if (this.centerSyncTimer) {
      clearInterval(this.centerSyncTimer);
      this.centerSyncTimer = null;
    }
  }
  logout() {
    this.authService.logout().subscribe({ //
      next: () => {
        this.router.navigate(['/login']); //
      },
      error: (err) => {
        console.error('Logout error:', err);
        this.router.navigate(['/login']);
      }
    });
  }

  goToLogin() {
    this.router.navigate(['/login']); //
  }

  goToSignup() {
    this.router.navigate(['/signup']); //
  }
  /**
 * Șterge un punct de oprire din listă.
 */
  removeStop(index: number): void {
    this.selectedStops.splice(index, 1);
    this.redrawStopGraphics();
  }

  /**
   * Șterge toate punctele de oprire.
   */
  clearAll(): void {
    this.selectedStops = [];
    this.routeGraphicsLayer.removeAll();
    this.totalDistance = 0;
  }

  calculateRoute(): void {
    if (this.selectedStops.length < 2) {
      alert('Vă rugăm să selectați cel puțin 2 locații pentru a calcula ruta.');
      return;
    }

    this.routeLoading = true;
    console.log("Calculare traseu optim...");

    // Transform attractions to match backend expected format
    const transformedAttractions = this.selectedStops.map(stop => ({
      ...stop,
      latitude: stop.location.latitude,
      longitude: stop.location.longitude
    }));

    // Call backend to calculate optimal route order
    this.apiService.calculateOptimalRoute(transformedAttractions).subscribe({
      next: (result) => {
        console.log('Route calculation result:', result);

        // Transform result back to frontend format
        const transformedRoute = result.route.map((stop: any) => ({
          ...stop,
          location: {
            latitude: stop.latitude,
            longitude: stop.longitude
          }
        }));

        // Update the selected stops with the optimized order
        this.selectedStops = transformedRoute;
        this.totalDistance = result.total_distance;

        // Redraw the stops in the new order
        this.redrawStopGraphics();

        // Now calculate the actual route using ArcGIS routing service
        this.calculateArcGISRoute(this.selectedStops);
      },
      error: (error) => {
        console.error('Error calculating route:', error);
        this.routeLoading = false;
        alert('Eroare la calcularea traseului. Vă rugăm să încercați din nou.');
      }
    });
  }

  private calculateArcGISRoute(stops: Attraction[]): void {
    // ArcGIS World Routing Service URL
    const routeServiceUrl = "https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World";

    // Create route stops as graphics
    const routeStops = stops.map(stop => {
      return new Graphic({
        geometry: new Point({
          longitude: stop.location.longitude,
          latitude: stop.location.latitude
        }),
        attributes: {
          Name: stop.name
        }
      });
    });

    // Set up route parameters
    const routeParams = new RouteParameters({
      stops: new FeatureSet({
        features: routeStops
      }),
      returnDirections: true,
      directionsLanguage: 'ro', // Romanian language for directions
      directionsLengthUnits: 'kilometers',
      outSpatialReference: this.view.spatialReference
    });

    // Solve the route
    route.solve(routeServiceUrl, routeParams).then((result: any) => {
      console.log('ArcGIS Route result:', result);

      // Clear previous route
      this.routeGraphicsLayer.graphics.forEach((graphic) => {
        if (graphic.geometry.type === 'polyline') {
          this.routeGraphicsLayer.remove(graphic);
        }
      });

      // Display the route on the map
      if (result.routeResults && result.routeResults.length > 0) {
        const routeResult = result.routeResults[0];

        // Draw the route line
        const routeSymbol = {
          type: "simple-line",
          color: [51, 122, 183, 0.8],
          width: 4
        };

        const routeGraphic = new Graphic({
          geometry: routeResult.route.geometry,
          symbol: routeSymbol
        });

        this.routeGraphicsLayer.add(routeGraphic);

        // Get total distance from ArcGIS
        const totalKm = (routeResult.route.attributes.Total_Kilometers || 0).toFixed(2);
        const totalTime = (routeResult.route.attributes.Total_TravelTime || 0).toFixed(0); // in minutes

        this.totalDistance = parseFloat(totalKm);

        // Set route summary
        this.routeSummary = {
          distance: totalKm,
          time: totalTime
        };

        // Display directions
        if (routeResult.directions) {
          this.displayDirections(routeResult.directions);
        }

        this.routeLoading = false;
        alert(`Traseu calculat!\nDistanță: ${totalKm} km\nTimp estimat: ${totalTime} minute\n\nVezi panoul de indicații pentru detalii.`);
      } else {
        this.routeLoading = false;
        alert('Nu s-a putut calcula traseul pe drumuri. Se afișează distanța directă.');
      }
    }).catch((error: any) => {
      console.error('ArcGIS routing error:', error);
      this.routeLoading = false;

      // Fallback to simple line if routing service fails
      alert('Nu s-a putut folosi serviciul de rutare ArcGIS. Se afișează distanța directă: ' + this.totalDistance.toFixed(2) + ' km');
    });
  }

  private displayDirections(directions: any): void {
    console.log('Route Directions:');
    console.log('=================');

    if (directions.features && directions.features.length > 0) {
      // Extract and format directions
      this.directions = directions.features.map((feature: any) => ({
        text: feature.attributes.text,
        length: (feature.attributes.length || 0).toFixed(2)
      }));

      // Log to console as well
      this.directions.forEach((direction, index) => {
        console.log(`${index + 1}. ${direction.text} (${direction.length} km)`);
      });

      console.log('=================');
      console.log('Total Features:', this.directions.length);

      // Show the directions panel
      this.showDirections = true;
    }
  }

  closeDirections(): void {
    this.showDirections = false;
  }

  private drawRouteLine(routeGeometry: number[][]): void {
    // Clear any existing route lines
    this.routeGraphicsLayer.graphics.forEach((graphic) => {
      if (graphic.geometry.type === 'polyline') {
        this.routeGraphicsLayer.remove(graphic);
      }
    });

    // Convert route geometry to Polyline
    const paths = routeGeometry.map(coord => [coord[1], coord[0]]); // [lng, lat]

    const polyline = new Polyline({
      paths: [paths]
    });

    const lineSymbol = {
      type: "simple-line",
      color: [51, 122, 183, 0.8], // Blue color
      width: 4
    } as any;

    const routeGraphic = new Graphic({
      geometry: polyline,
      symbol: lineSymbol
    });

    this.routeGraphicsLayer.add(routeGraphic);
    console.log('Route line drawn on map');
  }

  private drawStopGraphic(stop: Attraction, order: number): void {
    const point = new Point({
      latitude: stop.location.latitude,
      longitude: stop.location.longitude
    });

    const markerSymbol = {
      type: "simple-marker",
      style: "circle",
      color: [102, 126, 234, 0.9],
      size: 8
    } as esri.SimpleMarkerSymbolProperties;

    const stopGraphic = new Graphic({
      geometry: point,
      symbol: markerSymbol,
      attributes: stop,
      popupTemplate: {
        title: `${order}. ${stop.name}`,
        content: `Locație selectată`
      }
    });
    this.routeGraphicsLayer.add(stopGraphic);
  }

  private redrawStopGraphics(): void {
    this.routeGraphicsLayer.removeAll();
    this.selectedStops.forEach((stop, i) => this.drawStopGraphic(stop, i + 1));
  }

  addStopToRoute(attraction: Attraction): void {
    const exists = this.selectedStops.some(s => s.attraction_id === attraction.attraction_id);
    if (!exists) {
      this.selectedStops.push(attraction);
      this.redrawStopGraphics();
    }
  }
  
}
