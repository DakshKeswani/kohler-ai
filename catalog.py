import json
import os

def load_catalog():
    """
    Loads the Kohler product inventory from the JSON data store.
    """
    # Build the path dynamically so it runs flawlessly on any judge's machine
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'data', 'catalog.json')
    
    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Catalog database not found at {json_path}")
        return []
    except json.JSONDecodeError:
        print("Error: Catalog JSON is malformed.")
        return []

# We initialize this once when the module loads, acting as a mock in-memory DB
KOHLER_INVENTORY = load_catalog()