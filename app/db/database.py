
from typing import Any, Generator, Generic, Optional, Sequence, Type, TypeVar

from models.models import Location, Road, Route
from sqlmodel import Session, SQLModel, create_engine, select

from app.utils.config import Config

# ------------------------
# Database Setup
# ------------------------
engine = create_engine(Config.db_url,echo=True)
SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session


# ------------------------
# Generic CRUD Handler
# ------------------------
T = TypeVar("T", bound=SQLModel)


class DatabaseHandler(Generic[T]):
    def __init__(self, session: Session, model: Type[T]) -> None:
        self.session = session
        self.model = model

    # CREATE
    def create(self, obj_data: T) -> T:
        self.session.add(obj_data)
        self.session.commit()
        self.session.refresh(obj_data)
        return obj_data

    # READ (Single)
    def get(self, obj_id: Any) -> Optional[T]:
        return self.session.get(self.model, obj_id)

    # READ (All)
    def get_all(self) -> Sequence[T]:
        statement = select(self.model)
        results = self.session.exec(statement)
        return results.all()

    # UPDATE
    def update(self, obj_id: Any, new_data: dict) -> Optional[T]:
        obj = self.session.get(self.model, obj_id)
        if not obj:
            return None
        for key, value in new_data.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    # DELETE
    def delete(self, obj_id: Any) -> bool:
        obj = self.session.get(self.model, obj_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True


# ------------------------
# Example Usage
# ------------------------
next_session = next(get_session())

# You can now create handlers for any model dynamically:
location_db = DatabaseHandler(next_session, Location)
road_db = DatabaseHandler(next_session, Road)
route_db = DatabaseHandler(next_session, Route)

# Example CRUD actions:
# new_location = Location(name="Downtown", latitude=18.0123, longitude=-76.789)
# saved_location = location_db.create(new_location)
# fetched_location = location_db.get(saved_location.id)
# updated_location = location_db.update(saved_location.id, {"name": "New Downtown"})
# deleted = location_db.delete(saved_location.id)
