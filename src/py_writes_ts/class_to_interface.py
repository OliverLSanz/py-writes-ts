from typing import Type, List, Dict, Any, get_type_hints
from py_writes_ts.type_translator import python_type_to_typescript

def py_type_to_ts_string(py_type: Type, allowed_classes: Dict[str, Type[Any]], indent: int = 0) -> str:
    """
    Convierte un tipo Python en una definición TypeScript, con soporte para indentación.
    :param py_type: El tipo de Python a convertir.
    :param allowed_classes: Diccionario de clases permitidas para referencias.
    :param indent: Nivel de indentación actual.
    :return: String con el código TypeScript correspondiente.
    """
    INDENTATION = "    "  # Define el tamaño de la indentación
    current_indent = INDENTATION * indent
    next_indent = INDENTATION * (indent + 1)

    if hasattr(py_type, "__annotations__"):
        if py_type.__name__ in allowed_classes:
            # Usar una referencia al nombre de la clase si está en la lista permitida
            return py_type.__name__
        else:
            # Expandir en línea para tipos anidados no permitidos
            nested_properties = get_type_hints(py_type)
            nested_body = ",\n".join(
                f"{next_indent}{nested_prop}: {py_type_to_ts_string(nested_type, allowed_classes, indent + 1)}"
                for nested_prop, nested_type in nested_properties.items()
            )
            return f"{{\n{nested_body}\n{current_indent}}}"
    elif hasattr(py_type, "__origin__") and py_type.__origin__ == list:
        # Manejar tipos List
        item_type = py_type.__args__[0]
        if hasattr(item_type, "__annotations__"):
            if item_type.__name__ in allowed_classes:
                # Usar una referencia al nombre de la clase para listas permitidas
                return f"{item_type.__name__}[]"
            else:
                # Expandir en línea para tipos anidados en listas no permitidos
                nested_properties = get_type_hints(item_type)
                nested_body = ",\n".join(
                    f"{next_indent}{nested_prop}: {py_type_to_ts_string(nested_type, allowed_classes, indent + 1)}"
                    for nested_prop, nested_type in nested_properties.items()
                )
                return f"{{\n{nested_body}\n{current_indent}}}[]"
        else:
            return f"{py_type_to_ts_string(item_type, allowed_classes, indent)}[]"
    else:
        # Traducir tipos simples o no soportados
        return python_type_to_typescript(py_type)


def generate_typescript_interfaces(interface_names_and_classes: List[Type]) -> str:
    """
    Generate TypeScript interface definitions for a list of Python classes.

    :param interface_names_and_classes: A list of Python classes to convert to TypeScript interfaces.
    :return: A string with all TypeScript interfaces.
    """
    processed_interfaces = {}

    def process_class(interface_name: str, cls: Type, allowed_classes: Dict[str, Type]) -> None:
        """
        Process a single class to generate a TypeScript interface.

        :param interface_name: Name of the TypeScript interface.
        :param cls: The Python class to process.
        :param allowed_classes: A dictionary of allowed classes for generating separate interfaces.
        :return: The generated TypeScript interface as a string.
        """
        if interface_name in processed_interfaces:
            return

        properties = get_type_hints(cls)
        print("PROPS OF", interface_name, properties)
        interface_definition = [f"interface {interface_name} {{"]

        for prop, py_type in properties.items():
            ts_type = py_type_to_ts_string(py_type, allowed_classes, indent=1)
            interface_definition.append(f"    {prop}: {ts_type};")

        interface_definition.append("}")
        processed_interfaces[interface_name] = "\n".join(interface_definition) + "\n"

    # Process each class in the list
    allowed_classes = {cls.__name__: cls for cls in interface_names_and_classes}
    for cls in interface_names_and_classes:
        process_class(cls.__name__, cls, allowed_classes)

    # Combine all processed interfaces
    return "\n".join(processed_interfaces.values())


# Example usage
if __name__ == "__main__":
    class Exit:
        name: str
        description: str
        destination_room_id: str

    class Room:
        id: str
        name: str
        description: str
        exits: List[Exit]

    # Case 1: Exit included in the list
    typescript_code_included = generate_typescript_interfaces([Room, Exit])
    print("Case 1: Exit included")
    print(typescript_code_included)

    # Case 2: Exit not included in the list
    typescript_code_not_included = generate_typescript_interfaces([Room])
    print("Case 2: Exit not included")
    print(typescript_code_not_included)
