from typing import List, Tuple



def generate_typescript_function(
    function_name: str,
    parameters: List[Tuple[str, str]],
    return_type: str,
    body: List[str],
) -> str:
    """
    Generate a TypeScript function definition.

    :param function_name: The name of the function.
    :param parameters: A list of tuples where each tuple contains the parameter name and its type.
                       Example: [("socket", "Socket"), ("callback", "(event: OtherLeftRoomData) => void")]
    :param return_type: The return type of the function.
                        Use "void" if the function does not return anything.
    :param body: A list of strings representing the lines of the function body.
                 Example: ["socket.on('other_left_room', callback)"]
    :return: A string with the TypeScript function definition.
    """
    # Generate the parameters string
    params_str = ", ".join([f"{name}: {type_}" for name, type_ in parameters])

    # Generate the function definition
    function_def = f"function {function_name}({params_str}): {return_type} {{\n"
    for line in body:
        function_def += f"    {line}\n"
    function_def += "}"
    return function_def
