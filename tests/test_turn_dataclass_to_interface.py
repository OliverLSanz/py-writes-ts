from typing import Generic, List, Optional, TypeVar, Union
from py_writes_ts.class_to_interface import generate_typescript_interfaces, py_type_to_ts_string
from dataclasses import dataclass
import pytest

def test_transforms_simple_dataclass() -> None:
    @dataclass
    class Data:
        this_is_a_string: str
        this_is_an_int: int
        this_is_a_float: float
        this_is_a_bool: bool

    out = generate_typescript_interfaces([Data])

    print(out)

    assert out == """interface Data {
    this_is_a_string: string;
    this_is_an_int: number;
    this_is_a_float: number;
    this_is_a_bool: boolean;
}
"""


def test_transforms_dataclass_with_list() -> None:
    @dataclass
    class Data:
        list: List[str]

    out = generate_typescript_interfaces([Data])

    print(out)

    assert out == """interface Data {
    list: string[];
}
"""


def test_transforms_nested_dataclasses() -> None:
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
    class World:
        rooms: List[Room]

    out = generate_typescript_interfaces([World, Room, Exit])

    print(out)

    assert out == """interface World {
    rooms: Room[];
}

interface Room {
    id: string;
    name: string;
    description: string;
    exits: Exit[];
}

interface Exit {
    name: string;
    description: string;
    destination_room_id: string;
}
"""


def test_transforms_nested_dataclasses_exploding_not_included_classes() -> None:
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
    class World:
        rooms: List[Room]

    out = generate_typescript_interfaces([World])

    print(out)

    assert out == """interface World {
    rooms: {
        id: string;
        name: string;
        description: string;
        exits: {
            name: string;
            description: string;
            destination_room_id: string;
        }[];
    }[];
}
"""

def testpy_type_to_ts_string() -> None:

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
    class World:
        rooms: List[Room]

    out = py_type_to_ts_string(World, [])

    print(out)

    assert out == """{
    rooms: {
        id: string;
        name: string;
        description: string;
        exits: {
            name: string;
            description: string;
            destination_room_id: string;
        }[];
    }[];
}"""


def test_optional_fields() -> None:
    @dataclass
    class ResponseModel():
        success: bool
        data: Optional[str] = None
        error: Optional[str] = None

    out = py_type_to_ts_string(ResponseModel, [])
    # out = generate_typescript_interfaces([ResponseModel[Exit], Exit])

    print(out)

    assert out == """{
    success: boolean;
    data: string | null;
    error: string | null;
}"""

def test_union_fields() -> None:
    @dataclass
    class Exit:
        name: str
        description: str
        destination_room_id: str

    @dataclass
    class ResponseModel():
        success: bool
        data: Union[str, int]
        error: Union[str, bool, Exit]

    out = py_type_to_ts_string(ResponseModel, [])
    # out = generate_typescript_interfaces([ResponseModel[Exit], Exit])

    print(out)

    assert out == """{
    success: boolean;
    data: string | number;
    error: string | boolean | {
        name: string;
        description: string;
        destination_room_id: string;
    };
}"""

@pytest.mark.skip(reason="this feature is not yet implemented")
def test_unparametrized_generic_type() -> None:
    D = TypeVar("D")

    @dataclass
    class ResponseModel(Generic[D]):
        success: bool
        data: Optional[D] = None
        error: Optional[str] = None

    @dataclass
    class Exit:
        name: str
        description: str
        destination_room_id: str

    # out = py_type_to_ts_string(ResponseModel[Exit], {})
    out = generate_typescript_interfaces([ResponseModel])

    print(out)

    assert out == """interface ResponseModel<D> {
    success: boolean;
    data: D | null;
    error: string | null;
}
"""

@pytest.mark.skip(reason="this feature is not yet implemented")
def test_partially_parametrized_generic_type() -> None:
    D = TypeVar("D")
    T = TypeVar("T")

    @dataclass
    class ResponseModel(Generic[D, T]):
        success: bool
        data: Optional[D] = None
        error: Optional[T] = None

    @dataclass
    class Exit:
        name: str
        description: str
        destination_room_id: str

    # out = py_type_to_ts_string(ResponseModel[Exit], {})
    out = generate_typescript_interfaces([ResponseModel])

    print(out)

    assert out == """???"""

@pytest.mark.skip(reason="this feature is not yet implemented")
def test_generic_type_both_parametrized_and_unparametrized() -> None:
    D = TypeVar("D")

    @dataclass
    class ResponseModel(Generic[D]):
        success: bool
        data: Optional[D] = None
        error: Optional[str] = None

    @dataclass
    class Exit:
        name: str
        description: str
        destination_room_id: str

    out = generate_typescript_interfaces([ResponseModel[Exit], ResponseModel, Exit])

    print(out)

    assert out == """interface ExitResponseModel extends ResponseModel<Exit> { }

interface ResponseModel<D> {
    success: boolean;
    data: any | null;
    error: string | null;
}

interface Exit {
    name: string;
    description: string;
    destination_room_id: string;
}
"""

def test_parametrized_generic_type() -> None:
    D = TypeVar("D")

    @dataclass
    class ResponseModel(Generic[D]):
        success: bool
        data: Optional[D] = None
        error: Optional[str] = None

    @dataclass
    class Exit:
        name: str
        description: str
        destination_room_id: str

    # out = py_type_to_ts_string(ResponseModel[Exit], {})
    out = generate_typescript_interfaces([ResponseModel[Exit], Exit])

    print(out)

    assert out == """interface ExitResponseModel {
    success: boolean;
    data: Exit | null;
    error: string | null;
}

interface Exit {
    name: string;
    description: string;
    destination_room_id: string;
}
"""

from py_writes_ts.class_to_interface import ts_name

def test_name() -> None:
    D = TypeVar("D")

    @dataclass
    class ResponseModel(Generic[D]):
        success: bool
        data: Optional[D] = None
        error: Optional[str] = None

    @dataclass
    class Exit:
        name: str
        description: str
        destination_room_id: str 

    out = ts_name(ResponseModel)
    print(out)
    assert out == """ResponseModel<D>"""   

