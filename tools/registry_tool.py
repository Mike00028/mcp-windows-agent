import winreg

def get_registry_value(key_path: str, value_name: str) -> str:
    try:
        root, subkey = key_path.split("\\", 1)
        root_key = getattr(winreg, root)
        with winreg.OpenKey(root_key, subkey, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return str(value)
    except Exception as e:
        return f"Error reading registry: {e}"

def set_registry_value(key_path: str, value_name: str, new_value: str) -> str:
    try:
        root, subkey = key_path.split("\\", 1)
        root_key = getattr(winreg, root)
        with winreg.OpenKey(root_key, subkey, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, new_value)
            return f"Successfully set '{value_name}' to '{new_value}'"
    except Exception as e:
        return f"Error writing registry: {e}"