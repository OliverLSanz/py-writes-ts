from py_writes_ts.rename_interfaces import rename_interfaces

def test_rename_interfaces() -> None:
    class Potato:
        name: str

    class Login:
        name: str

    in_ = """
interface Login {
    email: any;
    password: string;
}

Potato,
PotatoManiac
Potato;
(Potato)
{Potato}
[Potato]
Potato<>
"""
    out = rename_interfaces(in_, {
        Login: "LoginRenamed",
        Potato: "Tomato"
    })

    print(out)

    assert out == """
interface LoginRenamed {
    email: any;
    password: string;
}

Tomato,
PotatoManiac
Tomato;
(Tomato)
{Tomato}
[Tomato]
Tomato<>
"""