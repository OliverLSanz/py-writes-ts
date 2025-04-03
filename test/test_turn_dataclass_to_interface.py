from typing import Generic, List, Literal, Optional, TypeVar, Union
from py_writes_ts.class_to_interface import generate_typescript_interfaces, py_type_to_ts_string, ts_name
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

    assert out == """export interface Data {
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

    assert out == """export interface Data {
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

    assert out == """export interface World {
    rooms: Room[];
}

export interface Room {
    id: string;
    name: string;
    description: string;
    exits: Exit[];
}

export interface Exit {
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

    assert out == """export interface World {
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


def testpy_ty_to_ts_string_does_not_expand_parametrized_generic_included_in_refs() -> None:
    T = TypeVar("T")

    @dataclass
    class Container(Generic[T]):
        thing: T

    @dataclass
    class Patata:
        size: int
        cooked: bool


    out = py_type_to_ts_string(Container[Patata], [ts_name(Container[Patata])])

    print(ts_name(Container[Patata]))

    print(out)

    assert out == """PatataContainer"""


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

    assert out == """export interface ResponseModel<D> {
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

    assert out == """export interface ExitResponseModel extends ResponseModel<Exit> { }

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

    assert out == """export interface ExitResponseModel {
    success: boolean;
    data: Exit | null;
    error: string | null;
}

export interface Exit {
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


def test_subclass_of_parametrized_generic() -> None:
    T = TypeVar('T')

    class Command(Generic[T]):
        pass

    @dataclass
    class LoginResult:
        user_id: str

    class Login(Command[LoginResult]):
        password: str

    out = generate_typescript_interfaces([Login])
    print(out)
    assert out == """export interface Login {
    password: string;
}
"""


def test_literal_type() -> None:
    class MessageOptions():
        display: Literal['wrap', 'box', 'underline', 'fit'] = 'wrap'
        section: bool = True
        fillInput: Optional[str] = None
        asksForPassword: bool = False

    out = generate_typescript_interfaces([MessageOptions])
    print(out)

    assert out == """export interface MessageOptions {
    display: 'wrap' | 'box' | 'underline' | 'fit';
    section: boolean;
    fillInput: string | null;
    asksForPassword: boolean;
}
"""

def test_empty_dataclass() -> None:
    @dataclass
    class ListWorlds:
        pass

    out = generate_typescript_interfaces([ListWorlds])
    print(out)

    assert out == """export interface ListWorlds {
}
"""