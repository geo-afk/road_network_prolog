from typing import Optional

import networkx as nx

from app.db.database import DatabaseHandler
from app.mapping.graph import RoadNetwork
from app.models.models import Road, Route


class RouteFinder:
    def __init__(self, network: RoadNetwork, db: DatabaseHandler):
        self.network = network
        self.db = db

    def find_shortest_route(self, from_location_id: int,
                           to_location_id: int) -> Optional[Route]:
        """Find shortest route using Dijkstra's algorithm"""
        try:
            # Find shortest path
            path = nx.shortest_path(
                self.network.graph,
                from_location_id,
                to_location_id,
                weight='weight'
            )

            # Calculate total distance and time
            total_distance = 0
            total_time = 0
            roads = []

            for i in range(len(path) - 1):
                edge_data = self.network.graph[path[i]][path[i+1]]
                total_distance += edge_data['distance']
                total_time += edge_data.get('travel_time', 0) or 0

                # Reconstruct road object
                road = Road(
                    id=edge_data.get('road_id'),
                    from_location_id=path[i],
                    to_location_id=path[i+1],
                    distance_km=edge_data['distance'],
                    road_type=edge_data['road_type'],
                    travel_time_minutes=edge_data.get('travel_time'),
                    status='open',
                    is_bidirectional=True
                )
                roads.append(road)

            route = Route(
                path=path,
                total_distance=round(total_distance, 2),
                total_time=total_time,
                roads=roads
            )

            # Save to database
            self.db.save_route_search(from_location_id, to_location_id, route)

            return route

        except nx.NetworkXNoPath:
            return None  # No path exists
        except nx.NodeNotFound:
            return None  # Invalid location
