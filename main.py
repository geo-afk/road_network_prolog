# main.py - Example Usage
from app.database import Database
from app.graph import RoadNetwork
from app.pathfinding import RouteFinder
from app.visualization import MapVisualizer

from app.models import Location, Road


def main():
    db = Database()

    # Example: Add locations (admin function)
    loc1 = Location(None, "Kingston", 18.0179, -76.8099, "city")
    loc2 = Location(None, "Spanish Town", 17.9911, -76.9574, "town")
    loc3 = Location(None, "Portmore", 17.9533, -76.8827, "town")

    loc1_id = db.add_location(loc1)
    loc2_id = db.add_location(loc2)
    loc3_id = db.add_location(loc3)

    # Add roads (admin function)
    road1 = Road(None, loc1_id, loc2_id, 15.5, "paved", 25, "open", True)
    road2 = Road(None, loc1_id, loc3_id, 10.2, "paved", 18, "open", True)
    road3 = Road(None, loc2_id, loc3_id, 8.3, "unpaved", 22, "open", True)

    db.add_road(road1)
    db.add_road(road2)
    db.add_road(road3)

    # Build network
    network = RoadNetwork()
    locations = db.get_all_locations()
    roads = db.get_all_roads()
    network.build_from_database(locations, roads)

    print(f"Network: {network.get_node_count()} locations, {network.get_edge_count()} roads")

    # Find route
    finder = RouteFinder(network, db)
    route = finder.find_shortest_route(loc1_id, loc2_id)

    if route:
        print(f"\nRoute found!")
        print(f"Distance: {route.total_distance} km")
        print(f"Time: {route.total_time} minutes")
        print(f"Path: {' -> '.join([locations[i-1].name for i in route.path])}")

        # Visualize
        viz = MapVisualizer(db)
        viz.create_route_map(route)
        viz.create_network_map()
        print("\nMaps created: route_map.html and network_map.html")
    else:
        print("No route found!")

if __name__ == "__main__":
    main()
