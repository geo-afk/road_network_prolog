
from typing import List

import folium

from app.database import Database
from app.models import Location, Route


class MapVisualizer:
    def __init__(self, db: Database):
        self.db = db

    def create_route_map(self, route: Route, output_file: str = 'route_map.html'):
        """Create an interactive map showing the route"""
        # Get location details
        locations = [self.db.get_location(loc_id) for loc_id in route.path]

        # Calculate center point
        avg_lat = sum(loc.latitude for loc in locations if loc.latitude) / len(locations)
        avg_lon = sum(loc.longitude for loc in locations if loc.longitude) / len(locations)

        # Create map
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)

        # Add markers for each location
        for i, loc in enumerate(locations):
            if loc.latitude and loc.longitude:
                popup_text = f"{loc.name}"
                if i == 0:
                    icon_color = 'green'
                    popup_text += " (Start)"
                elif i == len(locations) - 1:
                    icon_color = 'red'
                    popup_text += " (End)"
                else:
                    icon_color = 'blue'

                folium.Marker(
                    [loc.latitude, loc.longitude],
                    popup=popup_text,
                    icon=folium.Icon(color=icon_color)
                ).add_to(m)

        # Draw route lines
        coordinates = [(loc.latitude, loc.longitude)
                      for loc in locations
                      if loc.latitude and loc.longitude]

        if len(coordinates) > 1:
            folium.PolyLine(
                coordinates,
                color='blue',
                weight=3,
                opacity=0.7
            ).add_to(m)

        # Add route info
        info_text = f"""
        <div style="position: fixed;
                    top: 10px; right: 10px;
                    background: white;
                    padding: 10px;
                    border: 2px solid grey;
                    border-radius: 5px;
                    z-index: 9999;">
            <b>Route Information</b><br>
            Total Distance: {route.total_distance} km<br>
            Travel Time: {route.total_time} min<br>
            Stops: {len(route.path)}
        </div>
        """
        m.get_root().html.add_child(folium.Element(info_text))

        # Save map
        m.save(output_file)
        return output_file

    def create_network_map(self, output_file: str = 'network_map.html'):
        """Create a map showing the entire road network"""
        locations = self.db.get_all_locations()
        roads = self.db.get_all_roads()

        if not locations:
            return None

        # Calculate center
        valid_locs = [loc for loc in locations if loc.latitude and loc.longitude]
        avg_lat = sum(loc.latitude for loc in valid_locs) / len(valid_locs)
        avg_lon = sum(loc.longitude for loc in valid_locs) / len(valid_locs)

        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=9)

        # Add all locations
        for loc in valid_locs:
            folium.Marker(
                [loc.latitude, loc.longitude],
                popup=f"{loc.name} ({loc.type})",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

        # Add all roads
        loc_dict = {loc.id: loc for loc in valid_locs}

        for road in roads:
            from_loc = loc_dict.get(road.from_location_id)
            to_loc = loc_dict.get(road.to_location_id)

            if from_loc and to_loc and from_loc.latitude and to_loc.latitude:
                # Color based on road type
                color_map = {
                    'paved': 'green',
                    'unpaved': 'orange',
                    'broken_cisterns': 'red',
                    'deep_potholes': 'darkred'
                }
                color = color_map.get(road.road_type, 'gray')

                if road.status == 'closed':
                    color = 'black'

                folium.PolyLine(
                    [(from_loc.latitude, from_loc.longitude),
                     (to_loc.latitude, to_loc.longitude)],
                    color=color,
                    weight=2,
                    opacity=0.6,
                    popup=f"{road.road_type} - {road.distance_km}km"
                ).add_to(m)

        m.save(output_file)
        return output_file
