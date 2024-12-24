from typing import Optional
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
    assert out == """function myfunction(
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
}"""

def test_generate_ts_function_with() -> None:
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
    assert out == """function myfunction(
    name: string,
    patata: Patata
): Patata | null {
    a = b
    return b
}"""