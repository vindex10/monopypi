import os
import threading
from contextlib import contextmanager

from build.__main__ import main as build_main

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
