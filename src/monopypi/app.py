import os

import flask
import requests

from monopypi.build import build_package_if_not
from monopypi.config import CFG
from monopypi.find import find_packages
from monopypi.state import STATE


def build_app():
    _app = flask.Flask(__name__)
    STATE.schema = find_packages(CFG().root_dir)
    os.makedirs(CFG().cache_dir, exist_ok=True)
    return _app


app = build_app()


@app.route("/", methods=["GET"])
def get_root():
    res = []
    res.append(
        """
<!DOCTYPE html>
<html>
  <body><ul>
"""
    )
    for package_name in STATE.schema:
        res.append(f'<li><a href="/{package_name}/">{package_name}</a></li>')
    res.append(
        """
  </ul></body>
</html>
    """
    )
    return "\n".join(res)


@app.route("/<package_name>/", methods=["GET"])
def get_package(package_name):
    if package_name not in STATE.schema:
        return requests.get(f"{CFG().pypi_fallback}/{package_name}", timeout=CFG().pypi_fallback_timeout).content
    package_dist_dir = build_package_if_not(package_name)
    artifacts = os.listdir(package_dist_dir)
    res = []
    res.append(
        """
<!DOCTYPE html>
<html>
  <body><ul>
"""
    )
    for artifact in artifacts:
        res.append(f'<li><a href="/{package_name}/{artifact}">{artifact}</a></li>')
    res.append(
        """
  </ul></body>
</html>
    """
    )
    return "\n".join(res)


@app.route("/<package_name>/<package_artifact>", methods=["GET"])
def get_artifact(package_name, package_artifact):
    if package_name not in STATE.schema:
        return requests.get(f"{PYPI_FALLBACK}/{package_name}/{package_artifact}", timeout=PYPI_TIMEOUT).content
    package_dist_dir = build_package_if_not(package_name)
    return flask.send_file(os.path.join(package_dist_dir, package_artifact))
