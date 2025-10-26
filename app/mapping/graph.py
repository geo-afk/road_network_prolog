from typing import Dict, List

import networkx as nx

from app.models.models import Location, Road


class RoadNetwork():

    def __init__(self) -> None:
        self.graph = nx.DiGraph() # Direct Graph
        self.locations: Dict[int, Location] = {}


    def _calculate_weight(self, road: Road) -> float:
        """Calculates the edge weight  based on distance and road quality"""
        base_weight = road.distance_km

        road_penalties = {
            'paved': 1.0,
            'unpaved': 1.3,
            'broken_cisterns': 1.8,
            'deep_potholes': 2.2
        }


        penalties = road_penalties.get(road.road_type, 1.5)
        return base_weight * penalties

    def build_from_database(self, locations: List[Location], roads: List[Road]):

        # Add Nodes
        for loc in locations:
            self.graph.add_node(loc.id, **loc.to_dict())
            self.locations[0 if loc.id is None else loc.id] = loc


        # Add Edges
        for road in roads:
            if road.status == "open":

                weight = self._calculate_weight(road)

                self.graph.add_edge(
                     road.from_location_id,
                     road.to_location_id,
                     weight=weight,
                     distance=road.distance_km,
                     road_type=road.road_type,
                     travel_time=road.travel_time_minutes,
                     road_id=road.id
                )

                if road.is_bidirectional:
                    self.graph.add_edge(
                        road.to_location_id,
                        road.from_location_id,
                        weight=weight,
                        distance=road.distance_km,
                        road_type=road.road_type,
                        travel_time=road.travel_time_minutes,
                        road_id=road.id
                    )

        def get_node_count(self) -> int:
            return self.graph.number_of_nodes()

        def get_edge_count(self) -> int:
            return self.graph.number_of_edges()
