from typing import Any, List, Tuple, Dict
from py_writes_ts.class_to_interface import py_type_to_ts_string, ts_name

INDENT = "    "

def generate_typescript_function(
    function_name: str,
    parameters: Dict[str, Any],
    return_type: Any,
    body: str,
    valid_refs: List[type] = [],
    is_async: bool = False 
) -> str:
    if return_type is None:
        return_type = "void"
    valid_ref_names = [ts_name(ref) for ref in valid_refs]
    params_str = f",\n{INDENT}".join([f"{name}: {py_type_to_ts_string(type_, valid_ref_names, indent=1)}" for name, type_ in parameters.items()])
    function_def = f"""export{" async" if is_async else ""} function {function_name}(
{INDENT}{params_str}
): {py_type_to_ts_string(return_type, valid_ref_names)} {{\n"""
    for line in body.strip().split('\n'):
        function_def += f"{INDENT}{line}\n"
    function_def += "}\n\n"
    return function_def
