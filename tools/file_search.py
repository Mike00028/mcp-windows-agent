import os

def find_file(filename: str, path: str = "C:\\") -> list:
    try:
        name_only = os.path.splitext(filename)[0].lower()
        matches = []

        # Start searching from subdirectories, ignore the root directory itself
        for root, dirs, files in os.walk(path):
            if os.path.abspath(root) == os.path.abspath(path):
                continue  # skip the root directory itself
            for file in files:
                file_name_only = os.path.splitext(file)[0].lower()
                # Always require 'includes' substring in the filename (hardcoded, e.g., "data")
                if file_name_only == name_only or name_only in file_name_only:
                    matches.append(os.path.join(root, file))
                    if len(matches) >= 10:
                        return matches  # return early if 3 found

        return matches if matches else [f"'{filename}' not found in {path}"]
    except Exception as e:
        return [f"Error while searching: {e}"]
# def find_file(filename: str, path: str = "C:\\") -> str:
#     try:
#         for root, dirs, files in os.walk(path):
#             if filename in files:
#                 return os.path.join(root, filename)
#         return f"'{filename}' not found in {path}"
#     except Exception as e:
#         return f"Error while searching: {e}"
