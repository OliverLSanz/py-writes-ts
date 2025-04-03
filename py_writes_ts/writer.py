from typing import Generic, List, TypeVar, Optional

from py_writes_ts.class_to_interface import generate_typescript_interfaces
from py_writes_ts.function_generator import generate_typescript_function
from py_writes_ts.import_generator import generate_typescript_import

def write_to_file(content: str, filename: str):
    """
    Write the given content to a file.

    :param content: The content to write.
    :param filename: The file to write to.
    """
    with open(filename, "w") as file:
        file.write(content)

# Example usage
if __name__ == "__main__":
    typescript_code = ""

    typescript_code += generate_typescript_import("socket.io-client", ["Socket"])

    from py_writes_ts.example_types import Room, Exit, CreateConnectedRoomInput, PydanticRoom

    typescript_code += generate_typescript_interfaces([Room, Exit])
    
    
    # typescript_code += generate_typescript_function(
    #     function_name='emitCreateConnectedRoom',
    #     parameters=[
    #         ('socket', 'Socket'),
    #         ('params', 'CreateConnectedRoomParams'),
    #         ('callback', '(response: CreateConnectedRoomResponse) => void')
    #     ],
    #     return_type='void',
    #     body=[
    #         "socket.emit('create_connected_room', params, callback)"
    #     ]
    # )

    print(typescript_code)  # Print the result to the console

    # Write the result to ./out.ts
    write_to_file(typescript_code, "../ts/out.ts")
    print("TypeScript interface written to ./out.ts")
