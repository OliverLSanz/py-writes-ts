# PY WRITES TS

A library of tools to aid in the generation of typescript interfaces and functions from python dataclasses.

Use this to write a script that generates a typescript sdk from your python backend!

## Installation

```bash
pip install py-writes-ts
```

## Usage

### Class to Interface

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

code = generate_typescript_function(
    function_name="getUserById",
    parameters={
        "params": GetUserByIdRequest
    },
    return_type=GetUserByIdResponse,
    valid_refs=[GetUserByIdRequest, GetUserByIdResponse],
    body="""
const response = await fetch(`/api/get_user_by_id`, {{
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

Look at the tests for more examples.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
