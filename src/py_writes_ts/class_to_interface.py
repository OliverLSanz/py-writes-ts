from typing import Type, List, Dict, Any, Union, get_type_hints
from py_writes_ts.type_translator import python_type_to_typescript

from typing import Type, get_origin, get_args

def get_type_name(py_type: Type) -> str:
    origin = get_origin(py_type)
    if origin is not None:
        # Es un tipo genérico
        origin_name = getattr(origin, '__name__', None)
        if origin_name is None:
            # Para tipos como Union, List, Dict, etc. en 'typing', el __name__ no está definido.
            # Ejemplo: str(origin) podría ser 'typing.Union', 'typing.List', etc.
            origin_str = str(origin)
            # Tomamos la última parte después del punto, por ejemplo: 'typing.Union' -> 'Union'
            origin_name = origin_str.split('.')[-1] if '.' in origin_str else origin_str

        args = get_args(py_type)
        if args:
            args_names = [get_type_name(a) for a in args]
            return f"{origin_name}<{', '.join(args_names)}>"
        else:
            # Tipo genérico sin args (raro, pero posible)
            return origin_name
    else:
        # No es un genérico
        if hasattr(py_type, "__name__"):
            return py_type.__name__
        else:
            # Fallback si no tiene __name__
            return str(py_type)


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
            # Expandir para tipos anidados no permitidos
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
    elif hasattr(py_type, "__origin__") and py_type.__origin__ == Union:
        # Caso: Union[...] incluyendo Optional (Union[T, None])
        union_args = py_type.__args__
        # Verificamos si tenemos NoneType (Optional)
        if type(None) in union_args:
            # Tipo opcional: Union[T, None]
            non_none_args = [arg for arg in union_args if arg is not type(None)]
            # Si solo hay un tipo además de None, es T | null
            if len(non_none_args) == 1:
                return f"{py_type_to_ts_string(non_none_args[0], allowed_classes, indent)} | null"
            else:
                # Varios tipos + null
                union_parts = " | ".join(py_type_to_ts_string(arg, allowed_classes, indent) for arg in non_none_args)
                return f"{union_parts} | null"
        else:
            # Union genérico sin None
            union_parts = " | ".join(py_type_to_ts_string(arg, allowed_classes, indent) for arg in union_args)
            return union_parts
    elif hasattr(py_type, "__origin__"):
        origin = py_type.__origin__
        args = py_type.__args__
        if hasattr(origin, "__annotations__"):
            type_params = getattr(origin, '__parameters__', ())  # tuple of typevars
            typevar_to_type = dict(zip(type_params, args))  # dict of typevar to its associated type
        
            def substitute_typevars(t):
                # Reemplaza las TypeVar por sus args concretos
                if t in typevar_to_type:
                    return typevar_to_type[t]
                # No entiendo la siguiente parte, habra que probarla
                elif hasattr(t, '__origin__') and hasattr(t, '__args__'):
                    # Recursivo para tipos compuestos
                    new_args = tuple(substitute_typevars(a) for a in t.__args__)
                    # Crear un nuevo tipo genérico a partir del origin con args sustituidos
                    return t.__origin__[new_args]
                return t
            
            if origin.__name__ in allowed_classes:
                # Si la clase base está permitida, generar una notación genérica TS: Ej: Origin<Arg1, Arg2>
                arg_ts_list = [py_type_to_ts_string(substitute_typevars(a), allowed_classes, indent) for a in args]
                return f"{origin.__name__}<{', '.join(arg_ts_list)}>"
            else:
                # Expandir inline la clase genérica con sus propiedades sustituidas
                nested_properties = get_type_hints(origin)
                substituted_properties = {property_name: substitute_typevars(type) for property_name, type in nested_properties.items()}
                nested_body = ",\n".join(
                    f"{next_indent}{prop}: {py_type_to_ts_string(t, allowed_classes, indent + 1)}"
                    for prop, t in substituted_properties.items()
                )
                return f"{{\n{nested_body}\n{current_indent}}}"
        else:
            # Es un genérico sin anotaciones (podría ser un Union, Dict, o un tipo genérico integrado)
            # Llamar a python_type_to_typescript para manejo por defecto.
            return python_type_to_typescript(py_type)
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
