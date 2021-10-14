# -*- coding: utf-8 -*-
import json
import os
import signal
import sys
import time
from multiprocessing import Process, Queue, cpu_count, freeze_support

from termcolor import cprint
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.build_bff import BuildBff
from src.processor import Processor
from src.utils import *


def handle_signit(*args, **kwargs):
    cprint("Terminating...", "magenta")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_signit)

queue = Queue()


def process_fn(yyc_boost_dir: str, id: int, queue: Queue):
    print(f"Processor ({id}): Started")
    while True:
        cpp_path, build = queue.get()
        try:
            process_file(id, yyc_boost_dir, cpp_path, build)
        except Exception as e:
            cprint(f"Processor ({id}): ERROR: {e}", "red")


def process_file(processor, yyc_boost_dir, cpp_path, build):
    if not file_is_cpp(cpp_path):
        return
    fname = os.path.basename(cpp_path)

    _cpp_dir = os.path.join(yyc_boost_dir, "cpp")
    if os.path.exists(os.path.join(_cpp_dir, fname)):
        copy_file(os.path.join(_cpp_dir, fname), path_cpp)
        return

    gml_path, is_script = reconstruct_gml_path(build, fname)
    if not gml_path:
        cprint(
            f"Processor ({processor}): Processing {cpp_path}... skipping", "yellow")
        return
    try:
        Processor.inject_code(cpp_path, gml_path)
        cprint(
            f"Processor ({processor}): Processing {cpp_path}... processed", "green")
    except FileNotFoundError:
        cprint(
            f"Processor ({processor}): Processing {cpp_path}... ERROR: GML file not found!", "red")
    except Exception as e:
        cprint(
            f"Processor ({processor}): Processing {cpp_path}... ERROR: {e}", "red")


class EventHandler(FileSystemEventHandler):
    def __init__(self, build):
        super(EventHandler, self).__init__()
        self.build = build
        self.modified = {}

    def on_create(self, event):
        self._process(event)

    def on_modified(self, event):
        self._process(event)

    def _process(self, event):
        global queue
        fpath = event.src_path
        if not ".gml.cpp" in fpath:
            return
        with open(fpath) as f:
            if f.readline().startswith(Processor.INCLUDES):
                return
        queue.put((fpath, build,))


if __name__ == "__main__":
    freeze_support()

    if getattr(sys, "frozen", False):
        yyc_boost_dir = os.path.dirname(sys.executable)
    else:
        yyc_boost_dir = os.path.dirname(os.path.abspath(__file__))

    config_fname = "config.json"
    config_fpath = os.path.join(yyc_boost_dir, config_fname)

    if len(sys.argv) > 1:
        # Load cache directory from command line (no injection, only cleanup,
        # handy for GMS1.4)
        build = None
        path_cpp = sys.argv[1]
    else:
        # Config
        config = {}
        default = BuildBff.PATH_DEFAULT
        build_bff_dir = input(
            "Enter path to the build.bff file [{}]: ".format(default))
        if not build_bff_dir:
            build_bff_dir = default
        config["build_bff"] = build_bff_dir

        # Load build.bff
        try:
            build = BuildBff(build_bff_dir)
            print("Loaded build.bff")
        except:
            print("ERROR: Could not load build.bff!")
            sys.exit(1)

        # Project info
        path_cpp = build.get_cpp_dir()
        print("Project:", build.get_project_name())
        print("Config:", build.get_config())
        print("Project directory:", build.get_project_dir())

    print("Target directory:", path_cpp)

    # Check for permission
    if input("Do you really want to modify the files? [Y/n] ") == "n":
        cprint("Canceled", "magenta")
        sys.exit(0)

    # Copy custom headers
    _cpp_dir = os.path.join(yyc_boost_dir, "cpp")
    for f in os.listdir(_cpp_dir):
        copy_file(os.path.join(_cpp_dir, f), path_cpp)

    # Modify C++ files
    for root, _, files in os.walk(path_cpp):
        for fname in files:
            cpp_path = os.path.join(root, fname)
            queue.put((cpp_path, build,))

    event_handler = EventHandler(build)
    observer = Observer()
    observer.schedule(event_handler, path_cpp, recursive=True)
    observer.start()

    processes = []

    for i in range(cpu_count()):
        p = Process(target=process_fn, args=(
            yyc_boost_dir, i, queue,), daemon=True)
        p.start()
        processes.append(p)

    while True:
        time.sleep(1)
