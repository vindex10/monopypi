import glob
import os
import re
import tomllib
from collections import defaultdict


def find_packages(root_dir):
    pyproject_paths = glob.glob(f"{root_dir}/**/pyproject.toml", recursive=True)
    res = defaultdict(list)
    for pyproject_path in pyproject_paths:
        parsed_pyproject = parse_pyproject(pyproject_path)
        if not is_package(parsed_pyproject):
            continue
        package_name = get_package_name(parsed_pyproject)
        if package_name is None:
            continue
        package_source_dir = get_package_dir(pyproject_path)
        res[package_name] = package_source_dir
    return res


def parse_pyproject(pyproject_path):
    with open(pyproject_path, "rb") as fin:
        return tomllib.load(fin)


def is_package(pyproject):
    return "build-system" in pyproject


def get_package_name(pyproject):
    name = pyproject["project"].get("name")
    if name is None:
        return None
    return normalize_package_name(name)


def get_package_dir(pyproject_path):
    return os.path.dirname(pyproject_path)


def normalize_package_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()
