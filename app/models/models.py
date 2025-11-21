
from typing import Optional

from pydantic import BaseModel, Field


# -----------------------------
# Location Model
# -----------------------------
class Location(BaseModel):
    id: Optional[int] = Field(default=None, description="Primary key ID")
    name: Optional[str] = None
    latitude: float
    longitude: float
    location_type: Optional[str] = Field(
        default=None,
        description="e.g. 'junction', 'poi', 'traffic_signal', etc."
    )


# -----------------------------
# Route Model
# -----------------------------
class Route(BaseModel):
    id: Optional[int] = Field(default=None, description="Primary key ID")
    total_distance: float
    total_time: int


# -----------------------------
# Road Model
# -----------------------------
class Road(BaseModel):
    id: Optional[int] = Field(default=None, description="Primary key ID")
    from_location_id: int
    to_location_id: int
    route_id: Optional[int] = None
    name: Optional[str] = None
    distance_km: float
    road_type: str
    travel_time_minutes: Optional[int] = None
    status: str = Field(default="active")
