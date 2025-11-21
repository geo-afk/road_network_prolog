import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import osmium
from shapely.geometry import LineString
from sqlmodel import Session, select

from app.db.database import next_session
from app.models.models import Location, Road  # Import your models


class OSMRoadNetworkHandler(osmium.SimpleHandler):
    """
    Optimized handler for parsing OSM PBF files and extracting road network data.
    Uses batch processing and memory-efficient streaming.
    """

    def __init__(self, batch_size: int = 5000):
        super().__init__()
        self.batch_size = batch_size

        # Temporary storage for batch processing
        self.nodes: Dict[int, Tuple[float, float, Optional[str], Optional[str]]] = {}
        self.ways_batch: List[Dict] = []
        self.locations_batch: List[Location] = []

        # Track which nodes are used in ways (intersections)
        self.node_usage_count: Dict[int, int] = defaultdict(int)

        # Highway types to include (filter out pedestrian, cycleway if needed)
        self.valid_highway_types = {
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "unclassified",
            "residential",
            "motorway_link",
            "trunk_link",
            "primary_link",
            "secondary_link",
            "tertiary_link",
            "service",
            "living_street",
            "road",
            "highway",
        }

        self.stats = {
            "nodes_processed": 0,
            "ways_processed": 0,
            "roads_created": 0,
            "locations_created": 0,
        }

    def node(self, n):
        """Process nodes - store all nodes temporarily"""
        self.stats["nodes_processed"] += 1

        # Store node data: (lat, lon, name, type)
        name = n.tags.get("name")
        node_type = None

        # Determine node type from tags
        if "highway" in n.tags:
            node_type = n.tags["highway"]  # traffic_signals, crossing, etc.
        elif "amenity" in n.tags:
            node_type = n.tags["amenity"]
        elif "railway" in n.tags:
            node_type = n.tags["railway"]

        self.nodes[n.id] = (n.location.lat, n.location.lon, name, node_type)

    def way(self, w):
        """Process ways (roads) - extract and batch"""
        self.stats["ways_processed"] += 1

        # Filter: only process highways (roads)
        if "highway" not in w.tags:
            return

        highway_type = w.tags["highway"]
        if highway_type not in self.valid_highway_types:
            return

        # Track node usage for identifying intersections
        for node in w.nodes:
            self.node_usage_count[node.ref] += 1

        # Extract way properties
        way_data = {
            "osm_id": w.id,
            "name": w.tags.get("name"),
            "highway": highway_type,
            "surface": w.tags.get("surface"),
            "maxspeed": self._parse_speed(w.tags.get("maxspeed")),
            "lanes": self._parse_int(w.tags.get("lanes")),
            "oneway": w.tags.get("oneway") in ("yes", "1", "true"),
            "nodes": [node.ref for node in w.nodes],
        }

        self.ways_batch.append(way_data)

    def _parse_speed(self, speed_str: Optional[str]) -> Optional[int]:
        """Parse maxspeed tag (handles '50', '50 mph', 'walk', etc.)"""
        if not speed_str:
            return None

        try:
            # Remove common suffixes
            speed_str = speed_str.lower().replace("mph", "").replace("km/h", "").strip()
            speed = int(speed_str)
            return speed
        except (ValueError, AttributeError):
            # Handle special cases
            if speed_str in ("walk", "walking"):
                return 5
            return None

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Safely parse integer values"""
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula (in km)"""
        R = 6371  # Earth radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def create_road_segments(self, session: Session):
        """
        Create road segments from ways, splitting at intersections.
        This is called after all nodes and ways are processed.
        """
        print(f"Creating road segments from {len(self.ways_batch)} ways...")

        # First pass: identify intersection nodes (used by multiple ways)
        intersection_nodes = {
            node_id for node_id, count in self.node_usage_count.items() if count > 1
        }

        # Create location objects for intersections and way endpoints
        location_map: Dict[int, int] = {}  # OSM node ID -> DB location ID

        nodes_to_create = {}

        for way_data in self.ways_batch:
            nodes = way_data["nodes"]

            # Always include first and last node
            nodes_to_create = {nodes[0], nodes[-1]}

            # Include intersection nodes
            for node_id in nodes:
                if node_id in intersection_nodes:
                    nodes_to_create.add(node_id)

        # Batch create locations
        for node_id in nodes_to_create:
            if node_id not in location_map and node_id in self.nodes:
                lat, lon, name, node_type = self.nodes[node_id]

                location = Location(
                    osm_id=node_id,
                    name=name,
                    latitude=lat,
                    longitude=lon,
                    location_type=node_type or "junction",
                )
                self.locations_batch.append(location)

                if len(self.locations_batch) >= self.batch_size:
                    self._flush_locations(session)

        # Flush remaining locations
        if self.locations_batch:
            self._flush_locations(session)

        # Build location_map from database
        print("Building location map...")
        locations = session.exec(select(Location)).all()
        for loc in locations:
            if loc.osm_id:
                location_map[loc.osm_id] = 0 if loc.id is None else loc.id

        # Second pass: create road segments
        roads_batch: List[Road] = []

        for way_data in self.ways_batch:
            nodes = way_data["nodes"]

            # Split way into segments at intersections
            segment_start_idx = 0

            for i in range(1, len(nodes)):
                node_id = nodes[i]

                # Create segment if we hit an intersection or end of way
                if node_id in intersection_nodes or i == len(nodes) - 1:
                    from_node = nodes[segment_start_idx]
                    to_node = node_id

                    # Skip if we don't have location data
                    if from_node not in location_map or to_node not in location_map:
                        segment_start_idx = i
                        continue

                    # Calculate segment geometry and distance
                    segment_coords = []
                    total_distance = 0.0

                    for j in range(segment_start_idx, i + 1):
                        node = nodes[j]
                        if node in self.nodes:
                            lat, lon, _, _ = self.nodes[node]
                            segment_coords.append((lon, lat))

                            if j > segment_start_idx:
                                prev_node = nodes[j - 1]
                                if prev_node in self.nodes:
                                    prev_lat, prev_lon, _, _ = self.nodes[prev_node]
                                    total_distance += self._calculate_distance(
                                        prev_lat, prev_lon, lat, lon
                                    )

                    if len(segment_coords) >= 2:
                        # Create LineString geometry
                        linestring = LineString(segment_coords)
                        geom_wkt = linestring.wkt

                        # Estimate travel time (assuming average speeds by road type)
                        speed_map = {
                            "motorway": 100,
                            "trunk": 80,
                            "primary": 60,
                            "secondary": 50,
                            "tertiary": 40,
                            "residential": 30,
                            "unclassified": 40,
                            "service": 20,
                        }
                        avg_speed = way_data["maxspeed"] or speed_map.get(
                            way_data["highway"], 40
                        )
                        travel_time = (
                            int((total_distance / avg_speed) * 60)
                            if avg_speed > 0
                            else None
                        )

                        # Create road segment
                        road = Road(
                            osm_id=way_data["osm_id"],
                            name=way_data["name"],
                            from_location_id=location_map[from_node],
                            to_location_id=location_map[to_node],
                            distance_km=round(total_distance, 3),
                            road_type=way_data["highway"],
                            surface=way_data["surface"],
                            travel_time_minutes=travel_time,
                            max_speed=way_data["maxspeed"],
                            lanes=way_data["lanes"],
                            oneway=way_data["oneway"],
                            is_bidirectional=not way_data["oneway"],
                            status="active",
                            geom=geom_wkt,
                        )
                        roads_batch.append(road)
                        self.stats["roads_created"] += 1

                        # Create reverse direction if bidirectional
                        if not way_data["oneway"]:
                            reverse_road = Road(
                                osm_id=way_data["osm_id"],
                                name=way_data["name"],
                                from_location_id=location_map[to_node],
                                to_location_id=location_map[from_node],
                                distance_km=round(total_distance, 3),
                                road_type=way_data["highway"],
                                surface=way_data["surface"],
                                travel_time_minutes=travel_time,
                                max_speed=way_data["maxspeed"],
                                lanes=way_data["lanes"],
                                oneway=False,
                                is_bidirectional=True,
                                status="active",
                                geom=geom_wkt,
                            )
                            roads_batch.append(reverse_road)
                            self.stats["roads_created"] += 1

                        # Batch insert
                        if len(roads_batch) >= self.batch_size:
                            session.add_all(roads_batch)
                            session.commit()
                            print(f"Inserted {len(roads_batch)} roads...")
                            roads_batch = []

                    segment_start_idx = i

        # Flush remaining roads
        if roads_batch:
            session.add_all(roads_batch)
            session.commit()
            print(f"Inserted {len(roads_batch)} roads...")

    def _flush_locations(self, session: Session):
        """Flush location batch to database"""
        session.add_all(self.locations_batch)
        session.commit()
        self.stats["locations_created"] += len(self.locations_batch)
        print(f"Inserted {len(self.locations_batch)} locations...")
        self.locations_batch = []

    def print_stats(self):
        """Print processing statistics"""
        print("\n=== Processing Statistics ===")
        print(f"Nodes processed: {self.stats['nodes_processed']:,}")
        print(f"Ways processed: {self.stats['ways_processed']:,}")
        print(f"Locations created: {self.stats['locations_created']:,}")
        print(f"Road segments created: {self.stats['roads_created']:,}")


def parse_osm_to_database(pbf_file: str, batch_size: int = 5000):
    """
    Main function to parse OSM PBF file and populate database.

    Args:
        pbf_file: Path to .osm.pbf file
        database_url: SQLAlchemy database URL
        batch_size: Number of records to batch before committing
    """
    print(f"Starting OSM PBF parsing: {pbf_file}")
    print(f"Batch size: {batch_size}")

    # Create database engine

    # Create handler
    handler = OSMRoadNetworkHandler(batch_size=batch_size)

    # First pass: read all nodes and ways
    print("\nPass 1: Reading nodes and ways...")
    handler.apply_file(pbf_file)

    # Second pass: create road network
    print("\nPass 2: Creating road network...")
    handler.create_road_segments(next_session)

    # Print statistics
    handler.print_stats()

    print("\n✓ Processing complete!")
