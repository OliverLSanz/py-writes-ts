# PY WRITES TS

A library of tools to aid in the generation of typescript interfaces and functions from python dataclasses.

Use this to write a script that generates a typescript sdk from your python backend!

## Installation

```bash
pip install py-writes-ts
```

## Usage

### Class to Interface

The simplest example:

```python
from py_writes_ts.class_to_interface import generate_typescript_interfaces
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    age: int

code = generate_typescript_interfaces([User])
print(code)
```

Output:

```typescript
export interface User {
    id: number;
    name: string;
    age: number;
}
```

We can get more complex:

```python
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

out = generate_typescript_interfaces([ResponseModel[Exit], Exit])

print(out)
```

Output:

```typescript
export interface ExitResponseModel {
    success: boolean;
    data: Exit | null;
    error: string | null;
}

export interface Exit {
    name: string;
    description: string;
    destination_room_id: string;
}
```

### Function Generator

```python
from py_writes_ts.function_generator import generate_typescript_function
from dataclasses import dataclass

@dataclass
class GetUserByIdRequest:
    id: int

@dataclass
class GetUserByIdResponse:
    id: int
    name: str
    age: int

endpoint = "get_user_by_id"

code = generate_typescript_function(
    function_name="getUserById",
    parameters={
        "params": GetUserByIdRequest
    },
    return_type=GetUserByIdResponse,
    valid_refs=[GetUserByIdRequest, GetUserByIdResponse],
    body="""
const response = await fetch(`/api/{endpoint}`, {{
  method: "POST",
  headers: {{
      "Content-Type": "application/json"
  }},
  body: JSON.stringify(params)
}});

const data = await response.json();
return data;
"""
)
print(code)
```

Output:

```typescript
export async function getUserById(
    params: GetUserByIdRequest
): Promise<GetUserByIdResponse> {
    const response = await fetch(`/api/get_user_by_id`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    });
    
    if (!response.ok) {
        throw new Error(`API call failed with status ${response.status}`);
    }
    
    const data: GetUserByIdResponse = await response.json();
    return data;
}
```

### More examples

Look at the tests for more examples, including a full example of a typescript sdk generator.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
