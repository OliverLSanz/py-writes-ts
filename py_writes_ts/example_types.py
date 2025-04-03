from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from dataclasses import dataclass


class CreateConnectedRoomInput:
        name: str
        description: str
        exit_to_new_room_name: str
        exit_to_new_room_description: str
        exit_to_old_room_name: str
        exit_to_old_room_description: str

D = TypeVar('D')

class PydanticExit(BaseModel):
    name: str
    description: str
    destination_room_id: str

class PydanticRoom(BaseModel):
    id: str
    name: str
    description: str
    exits: List[PydanticExit]

@dataclass
class Exit:
    name: str
    description: str
    destination_room_id: str

@dataclass
class Room:
    id: str
    name: str
    description: str
    exits: List[Exit]

@dataclass
class ResponseModel(Generic[D]):
    success: bool
    data: Optional[D] = None
    error: Optional[str] = None

RoomResponse = ResponseModel[Room]