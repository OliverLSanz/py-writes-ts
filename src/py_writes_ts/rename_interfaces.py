import re
from typing import Any, Dict
from py_writes_ts.class_to_interface import ts_name

def rename_interfaces(code: str, substitutions: Dict[Any, str]) -> str:
    """
    Substitutes all exact (standalone) occurrences of each key in 'substitutions'
    with the corresponding value, treating them like TypeScript identifiers.

    :param code: The original TypeScript code.
    :param substitutions: A dictionary where each key is the python type
                          and each value is the new interface/name.
    :return: The modified code with substitutions applied.
    """
    # Regex snippet to match boundaries of TypeScript identifiers
    # We consider letters, digits, underscores, and $ as valid identifier chars.
    # So, the pattern looks like:
    #    (?<![A-Za-z0-9_$])OLD_NAME(?![A-Za-z0-9_$])
    for py_type, new_name in substitutions.items():
        pattern = rf"(?<![A-Za-z0-9_$]){re.escape(ts_name(py_type))}(?![A-Za-z0-9_$])"
        code = re.sub(pattern, new_name, code)
    return code