from pyswip import Prolog
import os


class RoadNetworkPathFinder:
    def __init__(self, prolog_file="./app/prolog/road_network.pl"):
        """Initialize the Prolog engine and load knowledge base"""
        self.prolog = Prolog()

        # Check if Prolog file exists
        if not os.path.exists(prolog_file):
            raise FileNotFoundError(f"Prolog file {prolog_file} not found!")
        # Load the Prolog knowledge base
        self.prolog.consult(prolog_file)
        print(f"✓ Loaded {prolog_file}")

    def find_path(self, start, goal, algorithm="dijkstra", criteria=None):
        """
        Find path between two locations

        Args:
            start: Starting location
            goal: Destination location
            algorithm: 'dijkstra', 'astar', or 'bfs'
            criteria: List of criteria to avoid (e.g., ['avoid_closed', 'avoid_unpaved'])

        Returns:
            Dictionary with path, distance, and status
        """
        if criteria is None:
            criteria = []

        # Convert Python list to Prolog list format
        criteria_str = "[" + ",".join(criteria) + "]"

        try:
            if algorithm == "dijkstra":
                query = (
                    f"dijkstra_path({start}, {goal}, {criteria_str}, Path, Distance)"
                )
                result = list(self.prolog.query(query))

                if result:
                    path = result[0]["Path"]
                    distance = result[0]["Distance"]
                    return {
                        "success": True,
                        "path": path,
                        "distance": distance,
                        "algorithm": "Dijkstra",
                    }

            elif algorithm == "astar":
                query = f"astar_path({start}, {goal}, {criteria_str}, Path, Distance)"
                result = list(self.prolog.query(query))

                if result:
                    path = result[0]["Path"]
                    distance = result[0]["Distance"]
                    return {
                        "success": True,
                        "path": path,
                        "distance": distance,
                        "algorithm": "A*",
                    }

            elif algorithm == "bfs":
                query = f"bfs_path({start}, {goal}, {criteria_str}, Path)"
                result = list(self.prolog.query(query))

                if result:
                    path = result[0]["Path"]
                    # Calculate distance for BFS
                    dist_query = f"calculate_distance({path}, Distance)"
                    dist_result = list(self.prolog.query(dist_query))
                    distance = dist_result[0]["Distance"] if dist_result else 0

                    return {
                        "success": True,
                        "path": path,
                        "distance": distance,
                        "algorithm": "BFS",
                    }

            return {"success": False, "message": "No path found between the locations"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def add_road(self, from_loc, to_loc, distance, road_type, status):
        """Add a new road to the network"""
        query = f"add_road({from_loc}, {to_loc}, {distance}, {road_type}, {status})"
        try:
            list(self.prolog.query(query))
            return True
        except:
            return False

    def update_road_status(self, from_loc, to_loc, new_status):
        """Update the status of an existing road"""
        query = f"update_road_status({from_loc}, {to_loc}, {new_status})"
        try:
            list(self.prolog.query(query))
            return True
        except:
            return False

    def list_roads(self):
        """Get all roads in the network"""
        query = "list_all_roads(Roads)"
        result = list(self.prolog.query(query))
        if result:
            return result[0]["Roads"]
        return []

    def get_available_locations(self):
        """Get all unique locations in the network"""
        roads = self.list_roads()
        locations = set()
        for road in roads:
            locations.add(road[0])  # From
            locations.add(road[1])  # To
        return sorted(list(locations))


def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 60)
    print("  JAMAICAN RURAL ROAD NETWORK PATH-FINDER")
    print("=" * 60)
    print("1. Find Shortest Path")
    print("2. Add New Road (Admin)")
    print("3. Update Road Status (Admin)")
    print("4. View All Roads")
    print("5. Exit")
    print("=" * 60)


def main():
    """Main program loop"""
    try:
        pathfinder = RoadNetworkPathFinder()
    except Exception as e:
        print(f"Error initializing system: {e}")
        return

    while True:
        display_menu()
        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            # Find path
            print("\n--- PATH FINDER ---")
            locations = pathfinder.get_available_locations()
            print(f"Available locations: {', '.join(locations)}")

            start = (
                input("\nEnter starting location: ").strip().lower().replace(" ", "_")
            )
            goal = input("Enter destination: ").strip().lower().replace(" ", "_")

            print("\nSelect algorithm:")
            print("1. Dijkstra (shortest distance)")
            print("2. A* (with heuristics)")
            print("3. BFS (simple search)")
            algo_choice = input("Choice (1-3): ").strip()

            algo_map = {"1": "dijkstra", "2": "astar", "3": "bfs"}
            algorithm = algo_map.get(algo_choice, "dijkstra")

            print(
                "\nSelect criteria to avoid (comma-separated, or press Enter for none):"
            )
            print(
                "Options: avoid_closed, avoid_unpaved, avoid_broken_cisterns, avoid_potholes"
            )
            criteria_input = input("Criteria: ").strip()
            criteria = [c.strip() for c in criteria_input.split(",") if c.strip()]

            print("\nSearching for path...")
            result = pathfinder.find_path(start, goal, algorithm, criteria)

            if result["success"]:
                print(f"\n✓ Path found using {result['algorithm']} algorithm!")
                print(f"Route: {' → '.join(str(loc) for loc in result['path'])}")
                print(f"Total Distance: {result['distance']} km")

                # Estimate travel time (assume 40 km/h average)
                travel_time = result["distance"] / 40
                print(f"Estimated Travel Time: {travel_time:.1f} hours")
            else:
                print(f"\n✗ {result['message']}")

        elif choice == "2":
            # Add road
            print("\n--- ADD NEW ROAD ---")
            from_loc = input("From location: ").strip().lower().replace(" ", "_")
            to_loc = input("To location: ").strip().lower().replace(" ", "_")
            distance = input("Distance (km): ").strip()

            print("Road type: paved, unpaved, broken_cisterns, deep_potholes")
            road_type = input("Type: ").strip().lower()

            print("Status: open, closed")
            status = input("Status: ").strip().lower()

            if pathfinder.add_road(from_loc, to_loc, distance, road_type, status):
                print("✓ Road added successfully!")
            else:
                print("✗ Failed to add road")

        elif choice == "3":
            # Update road status
            print("\n--- UPDATE ROAD STATUS ---")
            from_loc = input("From location: ").strip().lower().replace(" ", "_")
            to_loc = input("To location: ").strip().lower().replace(" ", "_")
            new_status = input("New status (open/closed): ").strip().lower()

            if pathfinder.update_road_status(from_loc, to_loc, new_status):
                print("✓ Road status updated!")
            else:
                print("✗ Failed to update road status")

        elif choice == "4":
            # View all roads
            print("\n--- ALL ROADS ---")
            roads = pathfinder.list_roads()
            print(f"\nTotal roads: {len(roads)}\n")
            print(
                f"{'From':<15} {'To':<15} {'Distance':<10} {'Type':<20} {'Status':<10}"
            )
            print("-" * 75)
            for road in roads:
                print(
                    f"{str(road[0]):<15} {str(road[1]):<15} {str(road[2]):<10} {str(road[3]):<20} {str(road[4]):<10}"
                )

        elif choice == "5":
            print("\nThank you for using the Path-Finder!")
            break

        else:
            print("\n✗ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
