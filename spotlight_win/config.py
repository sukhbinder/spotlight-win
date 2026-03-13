import configparser
import os

def get_config():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'search_path': os.path.expanduser('~'),
        'llm_location': '',
        'max_results': '10'
    }

    config_file_path = os.path.join(os.path.expanduser('~'), '.config', 'spotlight-win', 'config.ini')

    if os.path.exists(config_file_path):
        config.read(config_file_path)
    else:
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, 'w') as f:
            config.write(f)

    return config


def init_config():
    config = get_config()
    return config

