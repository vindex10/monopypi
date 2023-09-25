import os
import shutil
import tempfile
import threading
from contextlib import contextmanager

import wheel.cli.pack
import wheel.cli.unpack
from build.__main__ import main as build_main
from wheel.wheelfile import WheelFile

from monopypi.config import CFG
from monopypi.state import STATE

BUILD_TARGETS = ["sdist", "wheel"]


def build_package_if_not(package_name):
    package_dist_dir = get_package_dist_dir(package_name)
    if os.path.exists(package_dist_dir):
        wait_package_build_finished(package_name)
        return package_dist_dir
    build_package(package_name)
    return package_dist_dir


def build_package(package_name):
    with package_build_lock(package_name):
        build_source_dir = STATE.schema[package_name]
        package_dist_dir = get_package_dist_dir(package_name)
        if os.path.exists(package_dist_dir):
            # acquired lock after package was built
            return
        args = [build_source_dir, "-o", package_dist_dir]
        if "sdist" in BUILD_TARGETS:
            args.append("-s")
        if "wheel" in BUILD_TARGETS:
            args.append("-w")
        build_main(args)
        if CFG().editable:
            make_wheels_editable(package_dist_dir, build_source_dir)


def make_wheels_editable(package_dist_dir, build_source_dir):
    for fname in os.listdir(package_dist_dir):
        if not fname.endswith(".whl"):
            continue
        wheel_path = os.path.join(package_dist_dir, fname)
        make_wheel_editable(wheel_path, build_source_dir)


def make_wheel_editable(wheel_path, build_source_dir):
    with WheelFile(wheel_path) as wf:
        name = wf.parsed_filename.group("name")
        namever = wf.parsed_filename.group("namever")
    with tempfile.TemporaryDirectory() as tmpdir:
        wheel.cli.unpack.unpack(wheel_path, tmpdir)
        wheel_dir = os.path.join(tmpdir, namever)
        with open(os.path.join(wheel_dir, f"{name}.pth"), "w", encoding="utf-8") as pth:
            pth.write(f"{build_source_dir}/src\n")
        shutil.rmtree(os.path.join(wheel_dir, name))
        os.remove(wheel_path)
        wheel.cli.pack.pack(wheel_dir, os.path.dirname(wheel_path), build_number=None)


@contextmanager
def package_build_lock(package_name):
    if package_name not in STATE.build_locks:
        STATE.build_locks[package_name] = threading.Lock()
    with STATE.build_locks[package_name] as lock:
        yield lock


def wait_package_build_finished(package_name):
    if package_name not in STATE.build_locks:
        return
    if STATE.build_locks[package_name].locked():
        STATE.build_locks[package_name].acquire()
        STATE.build_locks[package_name].release()


def get_package_dist_dir(package_name):
    package_dist_dir = os.path.join(CFG().cache_dir, package_name)
    return package_dist_dir
