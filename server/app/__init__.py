from app.utils import get_footer

from configparser import ConfigParser, NoSectionError, NoOptionError

import os
from flask import Flask


def create_app():
    """ Creates and returns a Flask app."""
    app = Flask(__name__, template_folder='../templates')
    return app


app = create_app()

root_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(root_dir)
ini_path = os.path.join(root_dir, 'svarog.ini')

try:

    config = ConfigParser()
    config.optionxform = str

    loaded_configs = config.read(ini_path)

    if not loaded_configs:
        raise Exception(f"Unable to read config file from {ini_path}")

    for key, value in config.defaults().items():
        app.config[key] = value

    for section_name in config.sections():
        app.config[section_name] = {}
        section = config[section_name]
        for key, value in section.items():
            app.config[section_name][key] = value

except IOError as e:
    raise Exception("Unable to read %s file: %s" % (ini_path, e))
except NoSectionError as e:
    raise Exception("Unable to find section 'database' in the %s file: %s" % (ini_path, e))
except NoOptionError as e:
    raise Exception("Unable to find option in 'database' section in the %s file: %s" % (ini_path, e))

# TODO: this is a hack. Template_globals and routes does "from app import app". This is a circular dependency.
from app import template_globals  # noqa: F401, E402
from app import routes  # noqa: F401, E402

footer = get_footer()
app.jinja_env.globals["footer"] = footer
