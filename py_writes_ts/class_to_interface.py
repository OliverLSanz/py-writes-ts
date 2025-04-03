from typing import Literal, Type, List, Dict, Any, Union, get_type_hints, get_origin, Generic
from typing import Type, get_origin, get_args


def _primitive_to_ts(py_type: Union[Type, str]) -> str:
    """
    Translate a primitive Python type or a string to its TypeScript equivalent.
    """
    if isinstance(py_type, str):
        # If the type is already a string, return it as-is
        return py_type

    type_mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        type(None): "null",
        None: "null",
        Any: "any",
    }

    return type_mapping.get(py_type, "any")

def _is_parametrized_generic(type: Type) -> bool:
    """Returns true if type is a parametrized generic class
    https://docs.python.org/3/library/stdtypes.html#types-genericalias
    
    _is_parametrized_generic(GenericClass) -> False
    _is_parametrized_generic(NonGenericClass) -> False
    _is_parametrized_generic(GenericClass[str]) -> True
    """
    return get_origin(type) is not None

def _is_generic(type: Type) -> bool:
    """Returns true if type is a unparametrized generic class
    
    _is_generic(GenericClass) -> True
    _is_generic(NonGenericClass) -> False
    _is_parametrized_generic(GenericClass[str]) -> False
    """
    return get_origin(type) is None and len(getattr(type, "__parameters__", [])) > 0

def _is_user_defined_class(py_type: Type) -> bool:
    if isinstance(py_type, type) and py_type.__module__ != 'builtins':
        return True
    
    return False


def ts_name(py_type: Type) -> str:
    """Returns the typescript interface ts_name for a python type
    
    - NonGeneric -> NonGeneric (same as python ts_name)
    - GenericClass -> GenericClass<a, b>
    - GenericClass[Potatos, Carrots] -> PotatosCarrotsGenericClass 
    - Partially parametrized classes are not yet supported
    """
    if _is_parametrized_generic(py_type):
        origin: Any = get_origin(py_type)
        origin_name = origin.__name__
        args = get_args(py_type)
        args_names = [ts_name(a) for a in args]
        return f"{''.join(args_names)}{origin_name}"
    elif _is_generic(py_type):
        type_params = getattr(py_type, '__parameters__', ())
        origin_name = py_type.__name__
        params_names = [p.__name__ for p in type_params]
        return f"{origin_name}<{', '.join(params_names)}>"
    else:
        return py_type.__name__

def _substitute_typevars(t: Type, substitutions: Dict[Type, Type]) -> Type:
    if t in substitutions:
        return substitutions[t]
    elif _is_parametrized_generic(t):
        new_args = tuple(_substitute_typevars(a, substitutions) for a in t.__args__)
        return t.__origin__[new_args]
    return t

def py_type_to_ts_string(py_type: Type, allowed_refs: List[str], indent: int = 0) -> str:
    """
    Converts a Python type into a TypeScript definition, with support for indentation.
    :param py_type: The Python type to convert.
    :param allowed_refs: Dictionary of allowed classes for references.
    :param indent: Current indentation level.
    :return: A string with the corresponding TypeScript code.
    """
    INDENTATION = "    "
    current_indent = INDENTATION * indent
    next_indent = INDENTATION * (indent + 1)

    if _is_user_defined_class(py_type):
        if ts_name(py_type) in allowed_refs:
            return ts_name(py_type)
        else:
            # a reference to this type is not permitted,
            # so represent it by writting its properties
            # and types 
            nested_properties = get_type_hints(py_type)
            nested_body = "".join(
                f"{next_indent}{nested_prop}: {py_type_to_ts_string(nested_type, allowed_refs, indent + 1)};\n"
                for nested_prop, nested_type in nested_properties.items()
            )
            return f"{{\n{nested_body}{current_indent}}}"
    elif get_origin(py_type) == list:
        item_type = get_args(py_type)[0]
        return f"{py_type_to_ts_string(item_type, allowed_refs, indent)}[]"
    elif get_origin(py_type) is Literal:
        literal_args = get_args(py_type)
        def literal_value_to_ts(value: Any) -> str:
            if value is None:
                return "null"
            elif isinstance(value, str):
                return f"'{value}'"
            elif isinstance(value, bool):
                return "true" if value else "false"
            else:
                # for ints, floats, etc
                return str(value)

        union_of_literals = " | ".join(literal_value_to_ts(arg) for arg in literal_args)
        return union_of_literals
    elif get_origin(py_type) == Union:  
        # This includes Optionals as Optional[str] is Union[str, None]
        union_args = get_args(py_type)
        non_none_args = [arg for arg in union_args if arg is not type(None)]
        union_str = " | ".join(py_type_to_ts_string(arg, allowed_refs, indent) for arg in non_none_args)
        if type(None) in union_args:
            union_str = f"{union_str} | null"
        return union_str
    elif _is_parametrized_generic(py_type):
        if ts_name(py_type) in allowed_refs:
            return ts_name(py_type)
        origin = get_origin(py_type)
        assert origin  # damn mypy
        args = get_args(py_type)
        if hasattr(origin, "__annotations__"):
            type_params = getattr(origin, '__parameters__', ())  # tuple of typevars
            typevar_to_type = dict(zip(type_params, args))  # dict of typevar to its associated type
            if ts_name(origin) in allowed_refs:
                raise ValueError("Translating a parametrized generic with its generic class as a valid reference is not yet supported.")
                arg_ts_list = [py_type_to_ts_string(_substitute_typevars(a, typevar_to_type), allowed_refs, indent) for a in args]
                return f"{ts_name(origin)}<{', '.join(arg_ts_list)}>"
            else:
                nested_properties = get_type_hints(origin)
                substituted_properties = {property_name: _substitute_typevars(type, typevar_to_type) for property_name, type in nested_properties.items()}
                nested_body = ";\n".join(
                    f"{next_indent}{prop}: {py_type_to_ts_string(t, allowed_refs, indent + 1)}"
                    for prop, t in substituted_properties.items()
                ) + ";\n"
                return f"{{\n{nested_body}{current_indent}}}"
        else:
            # Generic type without annotations
            # Could be an integrated generic type we don't support yet
            raise ValueError("This unannotated generic type is not supported yet.")
            return _primitive_to_ts(py_type)
    else:
        # Traducir tipos simples o no soportados
        return _primitive_to_ts(py_type)


def generate_typescript_interfaces(py_types: List[Type]) -> str:
    """
    Generate TypeScript interface definitions for a list of Python classes.

    :param py_types: A list of Python classes to convert to TypeScript interfaces.
    :return: A string with all TypeScript interfaces.
    """
    processed_interfaces = {}

    def process_class(interface_name: str, cls: Type, allowed_refs: List[str]) -> None:
        """
        Process a single class to generate a TypeScript interface.

        :param interface_name: Name of the TypeScript interface.
        :param cls: The Python class to process.
        :param allowed_refs: A dictionary of allowed classes for generating separate interfaces.
        :return: The generated TypeScript interface as a string.
        """
        if interface_name in processed_interfaces:
            return

        allowed_classes_excluding_cls = [ts_name for ts_name in allowed_refs if ts_name != interface_name]
        type_body = py_type_to_ts_string(cls, allowed_classes_excluding_cls)
        interface_definition = f"export interface {interface_name} {type_body}\n"

        processed_interfaces[interface_name] = interface_definition

    # Process each class in the list
    allowed_refs = [ts_name(cls) for cls in py_types]
    for cls in py_types:
        process_class(ts_name(cls), cls, allowed_refs)

    # Combine all processed interfaces
    return "\n".join(processed_interfaces.values())
