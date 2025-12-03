from pyswip import Prolog
import os
import logging
from typing import List, Dict, Any, Optional


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




class RoadNetworkPathFinder:
    SUPPORTED_ALGORITHMS = {"dijkstra", "astar", "bfs"}

    def __init__(self, prolog_file: str = "./app/prolog/road_network.pl") -> None:
        self.prolog = Prolog()
        self._load_knowledge_base(prolog_file)

    def _load_knowledge_base(self, prolog_file: str) -> None:
        if not os.path.exists(prolog_file):
            raise FileNotFoundError(f"Prolog file '{prolog_file}' not found")

        self.prolog.consult(prolog_file)
        logger.info("Loaded Prolog file: %s", prolog_file)

    # -------- MAIN API ---------

    def find_path(
        self,
        start: str,
        goal: str,
        algorithm: str = "dijkstra",
        criteria: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm '{algorithm}'")

        criteria = criteria or []
        query = self._build_query(start, goal, algorithm, criteria)

        result = self._execute_query(query)

        if not result:
            return self._failure("No path found")

        return self._build_success_response(result[0], algorithm)

    # -------- ROAD MANAGEMENT ---------

    def add_road(
        self, from_loc: str, to_loc: str, distance: float, road_type: str, status: str
    ) -> bool:
        return self._bool_query(
            f"add_road({from_loc}, {to_loc}, {distance}, {road_type}, {status})"
        )

    def update_road_status(self, from_loc: str, to_loc: str, new_status: str) -> bool:
        return self._bool_query(
            f"update_road_status({from_loc}, {to_loc}, {new_status})"
        )

    def list_roads(self) -> List[Any]:
        result = self._execute_query("list_all_roads(Roads)")
        return result[0]["Roads"] if result else []

    def get_available_locations(self) -> List[str]:
        roads = self.list_roads()
        locations = {self.format_name(road[0]) for road in roads}.union(
            self.format_name(road[1]) for road in roads
        )
        return sorted(locations)

    # -------- HELPERS ---------

    def _execute_query(self, query: str) -> List[Dict]:
        try:
            return list(self.prolog.query(query))
        except Exception as e:
            logger.exception("Prolog query failed: %s, Error: [%s]", query, e)
            return []

    def _bool_query(self, query: str) -> bool:
        try:
            list(self.prolog.query(query))
            return True
        except Exception as e:
            logger.warning("Err: [%s], Query failed: %s", e.__str__(), query)
            return False

    def _build_query(
        self, start: str, goal: str, algorithm: str, criteria: List[str]
    ) -> str:
        crit = self._format_list(criteria)

        if algorithm == "dijkstra":
            return f"dijkstra_path({start}, {goal}, {crit}, Path, Distance)"

        if algorithm == "astar":
            return f"astar_path({start}, {goal}, {crit}, Path, Distance)"

        if algorithm == "bfs":
            return f"bfs_path({start}, {goal}, {crit}, Path)"

        raise ValueError("Unsupported algorithm")

    def _build_success_response(self, result: Dict, algorithm: str) -> Dict[str, Any]:
        response = {
            "success": True,
            "path": result.get("Path"),
            "algorithm": algorithm.upper(),
        }

        if "Distance" in result:
            response["distance"] = result["Distance"]
        elif algorithm == "bfs":
            response["distance"] = self._calculate_distance(result["Path"])

        return response

    def _calculate_distance(self, path: List[str]) -> float:
        result = self._execute_query(f"calculate_distance({path}, Distance)")
        return result[0]["Distance"] if result else 0.0

    def _format_list(self, items: List[str]) -> str:
        return "[" + ",".join(items) + "]"

    @staticmethod
    def format_name(name: str) -> str:
        """Convert 'new_york' → 'New York'"""
        return name.replace("_", " ").title()

    @staticmethod
    def unformat_name(name: str) -> str:
        """Convert 'New York' → 'new_york'"""
        return name.strip().lower().replace(" ", "_")

    @staticmethod
    def _failure(msg: str) -> Dict[str, Any]:
        return {"success": False, "message": msg}
