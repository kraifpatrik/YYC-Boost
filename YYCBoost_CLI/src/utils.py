import os
import sys
import shutil
from threading import Condition
from time import perf_counter
from typing import Optional

from termcolor import cprint

from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer


def file_is_cpp(file):
    return file[-8:] == ".gml.cpp"


def cpp_is_script(file):
    return file[:17] == "gml_GlobalScript_"


def cpp_is_event(file):
    return file[:11] == "gml_Object_"


def cpp_is_room(file):
    return file[:9] == "gml_Room_"


def reconstruct_gml_path(build_bff, cpp_path):
    project_dir = build_bff.get_project_dir()
    path_src = ""
    is_script = False

    # Reconstruct path of object event
    if cpp_is_event(cpp_path):
        split = cpp_path.split("_")
        file_name = split[-2:]
        if file_name[0] != "PreCreate":
            file_name[-1] = file_name[-1][:-4]
            file_name = "_".join(file_name)
            object_name = "_".join(split[:-2][2:])
            path_src = os.path.join(project_dir, "objects",
                                    object_name, file_name)
    # Reconstruct path of script
    elif cpp_is_script(cpp_path):
        is_script = True
        name = os.path.basename(cpp_path)[17:-8]
        path_src = os.path.join(project_dir, "scripts",
                                name, "{}.gml".format(name))

    return path_src, is_script


def copy_file(src, path_cpp):
    dest = os.path.join(path_cpp, os.path.basename(src))
    print("Copying", src, "...", end="")
    try:
        os.remove(dest)
    except:
        pass
    shutil.copyfile(src, dest)
    cprint("done", "green")


def wait_for_file(path: str, time_limit: Optional[float]):
    parents = [path]
    while not os.path.exists(parents[-1]):
        parent = os.path.dirname(parents[-1])
        if parent == parents[-1]: break
        parents.append(parent)
    
    for path, parent in zip(reversed(parents[:-1]), reversed(parents[1:])):
        if time_limit is None:
            remaining = Noone
        else:
            remaining = time_limit - perf_counter()
            print('Waiting {:.2f}s for "{}" to appear...'.format(remaining, path))
        if not wait_for_file_in(path, parent, remaining):
            cprint('ERROR: "{}" failed to appear in time; aborting.'
                   .format(path), 'red')
            sys.exit(1)


def wait_for_file_in(path: str, parent: str, timeout: Optional[float]) -> bool:
    start = perf_counter()

    cond = Condition()
    class Handler(FileSystemEventHandler):
        def on_created(self, _event: FileCreatedEvent):
            if not os.path.exists(path): return
            with cond: cond.notify_all()
    observer = Observer()
    observer.schedule(Handler(), parent, recursive=False)
    observer.start()

    created = os.path.exists(path)
    while not created and (timeout is None or perf_counter() < start + timeout):
        # Wait for 1s at a time to let the main thread to process signals:
        with cond: created = cond.wait(1)

    observer.stop()
    return created
