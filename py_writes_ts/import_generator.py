from typing import List

def generate_typescript_import(module_name: str, imports: List[str]) -> str:
    """
    Generate a TypeScript import statement.

    :param module_name: The name of the module to import from.
    :param imports: A list of items to import from the module.
    :return: A TypeScript import statement as a string.
    """
    if not imports:
        raise ValueError("The imports list cannot be empty.")
    
    # Create the import statement
    import_items = ", ".join(imports)
    return f"import {{ {import_items} }} from '{module_name}';\n"
