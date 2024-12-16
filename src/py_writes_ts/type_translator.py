from typing import Any, Type, Union, get_origin, get_args


def python_type_to_typescript(py_type: Union[Type, str]) -> str:
    """
    Translate a Python type or a string to its TypeScript equivalent.

    :param py_type: Python type (e.g., str, int, List[int], Dict[str, int]) or string.
    :return: Corresponding TypeScript type.
    """
    if isinstance(py_type, str):
        # If the type is already a string, return it as-is
        return py_type

    type_mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        list: "Array<any>",
        dict: "Record<string, any>",
        type(None): "null",
        Any: "any",
    }

    # Handle generic types
    origin = get_origin(py_type)
    args = get_args(py_type)

    if origin is list and args:
        return f"Array<{python_type_to_typescript(args[0])}>"
    elif origin is dict and args:
        return f"Record<{python_type_to_typescript(args[0])}, {python_type_to_typescript(args[1])}>"

    return type_mapping.get(py_type, "any")