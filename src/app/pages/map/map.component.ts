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
import { FirebaseService } from '../../services/firebase.service';
import { ApiService } from '../../services/api.service';


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

  constructor(
    private fb: FirebaseService,
    private apiService: ApiService
  ) { }
  private firebaseUnsubscribe: (() => void) | null = null;
  private userPosUnsubscribe: (() => void) | null = null;
  private clientId: string = 'client_' + Math.random().toString(36).substr(2, 9);
  private lastCenterSent: number = 0;
  private centerSyncTimer: any = null;
  graphicsLayerFirebase: esri.GraphicsLayer;

  ngOnInit() {
    // Load tourism configuration from backend
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
    // Add Romanian Counties layer
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

    this.trailheadsLayer = new FeatureLayer({
      url: "https://services3.arcgis.com/GVgbJbqm8hXASVYi/arcgis/rest/services/Trailheads/FeatureServer/0",
      outFields: ['*']
    });
    this.map.add(this.trailheadsLayer);

    const trailsLayer = new FeatureLayer({
      url: "https://services3.arcgis.com/GVgbJbqm8hXASVYi/arcgis/rest/services/Trails/FeatureServer/0"
    });
    this.map.add(trailsLayer, 0);

    const parksLayer = new FeatureLayer({
      url: "https://services3.arcgis.com/GVgbJbqm8hXASVYi/arcgis/rest/services/Parks_and_Open_Space/FeatureServer/0"
    });
    this.map.add(parksLayer, 0);

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
}
