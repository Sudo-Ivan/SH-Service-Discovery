import yaml

def load_config():
    with open("config.yaml", "r") as ymlfile:
        return yaml.safe_load(ymlfile)

def get_cors_origins():
    config = load_config()
    return [f"http://{origin}" for origin in config.get('cors_origins', [])]