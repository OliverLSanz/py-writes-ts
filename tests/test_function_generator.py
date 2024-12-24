from typing import Generic, Optional, TypeVar
from py_writes_ts.function_generator import generate_typescript_function
from dataclasses import dataclass


def test_generate_ts_function_without_valid_refs() -> None:
    @dataclass
    class Patata:
        size: int
        cooked: bool

    out = generate_typescript_function(
        function_name='myfunction',
        parameters={
            'name': str,
            'patata': Patata
        },
        return_type=Optional[Patata],
        valid_refs=[],
        body="""a = b
return b
"""
    )
    print(out)
    assert out == """export function myfunction(
    name: string,
    patata: {
        size: number;
        cooked: boolean;
    }
): {
    size: number;
    cooked: boolean;
} | null {
    a = b
    return b
}

"""

def test_generate_ts_function_with_valid_refs() -> None:
    @dataclass
    class Patata:
        size: int
        cooked: bool

    out = generate_typescript_function(
        function_name='myfunction',
        parameters={
            'name': str,
            'patata': Patata
        },
        return_type=Optional[Patata],
        valid_refs=[Patata],
        body="""a = b
return b
"""
    )
    print(out)
    assert out == """export function myfunction(
    name: string,
    patata: Patata
): Patata | null {
    a = b
    return b
}

"""


def test_generate_ts_function_with_parametrized_generic_ref() -> None:
    T = TypeVar("T")

    @dataclass
    class Container(Generic[T]):
        thing: T

    @dataclass
    class Patata:
        size: int
        cooked: bool

    out = generate_typescript_function(
        function_name='myfunction',
        parameters={
            'name': str,
            'patata': Patata
        },
        return_type=Container[Patata],
        valid_refs=[Container[Patata]],
        body="""a = b
return b
"""
    )
    print(out)
    assert out == """export function myfunction(
    name: string,
    patata: {
        size: number;
        cooked: boolean;
    }
): PatataContainer {
    a = b
    return b
}

"""


def test_generate_ts_function_with_literal_type() -> None:
    @dataclass
    class Patata:
        size: int
        cooked: bool

    out = generate_typescript_function(
        function_name='myfunction',
        parameters={
            'name': str,
            'patata': "Patatita",
        },
        return_type="Patatota",
        valid_refs=[],
        body="""a = b
return b
"""
    )
    print(out)
    assert out == """export function myfunction(
    name: string,
    patata: Patatita
): Patatota {
    a = b
    return b
}

"""