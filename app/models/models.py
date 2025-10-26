from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import List, Optional


class Location(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    type: Optional[float]


    def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'type': self.type
            }




class Road(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    from_location_id: int = Field(foreign_key="location.id")
    to_location_id: int = Field(foreign_key="location.id")
    distance_km: float
    road_type: str # paved, unpaved, pot_holes,broken_cisterms
    travel_time_minutes: Optional[int]
    status: str
    is_bidirectional: bool = Field(default=True)
    geom: Optional[str] = Field(default=None, sa_column=Geometry("LINESTRING", 4326))

    def to_dict(self):
            return {
                'id': self.id,
                'from_location_id': self.from_location_id,
                'to_location_id': self.to_location_id,
                'distance_km': self.distance_km,
                'road_type': self.road_type,
                'travel_time_minutes': self.travel_time_minutes,
                'status': self.status,
                'is_bidirectional': self.is_bidirectional
            }



class Route(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    from_location_id: int
    path: List[int]
    total_distance: float
    total_time: int
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc).utcnow)


    def to_dict(self):
            return {
                'total_distance': self.total_distance,
                'total_time': self.total_time,
                'roads': [r.to_dict() for r in self.roads]
            }
