from pyswip import Prolog
import os
import logging
from typing import List, Dict, Any, Optional
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoadNetworkPathFinder:
    SUPPORTED_ALGORITHMS = {"dijkstra", "astar", "bfs"}

    def __init__(self, prolog_file: str = "./app/prolog/road_network.pl") -> None:
        self.prolog = Prolog()
        self.prolog_file = prolog_file
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

    # -------- ROAD MANAGEMENT WITH FILE PERSISTENCE ---------

    def add_road(
        self, from_loc: str, to_loc: str, distance: float, road_type: str, status: str
    ) -> bool:
        """Add a road to both memory and the Prolog file"""
        try:
            # First, add to Prolog memory
            query = f"add_road({from_loc}, {to_loc}, {distance}, {road_type}, {status})"
            self._bool_query(query)

            # Then, persist to file
            self._append_road_to_file(from_loc, to_loc, distance, road_type, status)

            logger.info(f"Added road: {from_loc} -> {to_loc}")
            return True
        except Exception as e:
            logger.error(f"Failed to add road: {e}")
            return False

    def update_road_status(self, from_loc: str, to_loc: str, new_status: str) -> bool:
        """Update road status in both memory and the Prolog file"""
        try:
            # Update in Prolog memory
            query = f"update_road_status({from_loc}, {to_loc}, {new_status})"
            success = self._bool_query(query)

            if success:
                # Update in file
                self._update_road_in_file(from_loc, to_loc, status=new_status)
                logger.info(
                    f"Updated road status: {from_loc} -> {to_loc} = {new_status}"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update road status: {e}")
            return False

    def update_road_type(self, from_loc: str, to_loc: str, new_type: str) -> bool:
        """Update road type in both memory and the Prolog file"""
        try:
            # Update in Prolog memory
            query = f"update_road_type({from_loc}, {to_loc}, {new_type})"
            success = self._bool_query(query)

            if success:
                # Update in file
                self._update_road_in_file(from_loc, to_loc, road_type=new_type)
                logger.info(f"Updated road type: {from_loc} -> {to_loc} = {new_type}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update road type: {e}")
            return False

    def delete_road(self, from_loc: str, to_loc: str) -> bool:
        """Delete a road from both memory and the Prolog file"""
        try:
            # Delete from Prolog memory
            query = f"delete_road({from_loc}, {to_loc})"
            self._bool_query(query)

            # Delete from file
            self._delete_road_from_file(from_loc, to_loc)

            logger.info(f"Deleted road: {from_loc} -> {to_loc}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete road: {e}")
            return False

    # -------- FILE PERSISTENCE METHODS ---------

    def _append_road_to_file(
        self, from_loc: str, to_loc: str, distance: float, road_type: str, status: str
    ) -> None:
        """Append a new road to the Prolog file"""
        road_entry = f"road({from_loc}, {to_loc}, {distance}, {road_type}, {status}).\n"

        try:
            with open(self.prolog_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Find the last road(...) entry
            # Insert new road before the bidirectional_road section or at the end
            marker = "% ===== BIDIRECTIONAL ROAD PREDICATE ====="

            if marker in content:
                # Insert before the bidirectional section
                parts = content.split(marker)
                parts[0] = parts[0].rstrip() + "\n" + road_entry + "\n"
                new_content = marker.join(parts)
            else:
                # Just append to the end
                new_content = content.rstrip() + "\n" + road_entry

            # Write back to file
            with open(self.prolog_file, "w", encoding="utf-8") as f:
                f.write(new_content)

        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            raise

    def _update_road_in_file(
        self,
        from_loc: str,
        to_loc: str,
        road_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """Update a road entry in the Prolog file"""
        try:
            with open(self.prolog_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Pattern to match road entries
            pattern = re.compile(
                rf"road\({re.escape(from_loc)},\s*{re.escape(to_loc)},\s*"
                r"([\d.]+),\s*(\w+),\s*(\w+)\)\."
            )

            updated = False
            for i, line in enumerate(lines):
                match = pattern.search(line)
                if match:
                    distance = match.group(1)
                    current_type = match.group(2)
                    current_status = match.group(3)

                    # Update the specified fields
                    new_type = road_type if road_type is not None else current_type
                    new_status = status if status is not None else current_status

                    # Replace the line
                    lines[i] = (
                        f"road({from_loc}, {to_loc}, {distance}, {new_type}, {new_status}).\n"
                    )
                    updated = True
                    break

            if updated:
                with open(self.prolog_file, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            else:
                logger.warning(f"Road not found in file: {from_loc} -> {to_loc}")

        except Exception as e:
            logger.error(f"Error updating file: {e}")
            raise

    def _delete_road_from_file(self, from_loc: str, to_loc: str) -> None:
        """Delete a road entry from the Prolog file"""
        try:
            with open(self.prolog_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Pattern to match road entries
            pattern = re.compile(
                rf"road\({re.escape(from_loc)},\s*{re.escape(to_loc)},\s*"
                r"[\d.]+,\s*\w+,\s*\w+\)\."
            )

            # Filter out the matching line
            new_lines = [line for line in lines if not pattern.search(line)]

            if len(new_lines) < len(lines):
                with open(self.prolog_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
            else:
                logger.warning(f"Road not found in file: {from_loc} -> {to_loc}")

        except Exception as e:
            logger.error(f"Error deleting from file: {e}")
            raise

    def backup_prolog_file(self, backup_suffix: str = ".backup") -> str:
        """Create a backup of the Prolog file"""
        try:
            backup_file = self.prolog_file + backup_suffix

            with open(self.prolog_file, "r", encoding="utf-8") as f:
                content = f.read()

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Backup created: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    def export_roads_to_file(self, export_file: str) -> bool:
        """Export all current roads to a new file"""
        try:
            roads = self.list_roads()

            with open(export_file, "w", encoding="utf-8") as f:
                f.write("% Exported Roads\n")
                f.write("% Format: road(From, To, Distance, Type, Status).\n\n")

                for road in roads:
                    from_loc, to_loc, dist, road_type, status = road
                    f.write(
                        f"road({from_loc}, {to_loc}, {dist}, {road_type}, {status}).\n"
                    )

            logger.info(f"Exported {len(roads)} roads to {export_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting roads: {e}")
            return False

    # -------- EXISTING METHODS ---------

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
