# -*- coding: utf-8 -*-
import json
import os
import os.path
import signal
import sys
import time
import subprocess
import inspect
import traceback
from subprocess import DEVNULL, CREATE_NO_WINDOW
from multiprocessing import (
    Process, Queue, cpu_count, freeze_support, current_process
)
from argparse import ArgumentParser
from queue import Empty as QueueEmpty

from termcolor import cprint
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.build_bff import BuildBff
from src.processor import Processor
from src.utils import *


def process_fn(yyc_boost_dir: str, id: int, queue: Queue,
               exit_when_queue_empty: bool = False):
    print(f"Processor ({id}): Started")
    while True:
        try:
            cpp_path, build = queue.get(block = not exit_when_queue_empty)
        except QueueEmpty:
            break
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


def parse_args(*args, **kwds):
    # Apply some cosmetic changes to the help and usage output:
    class CustomArgumentParser(ArgumentParser):
        def format_usage(self):
            usage = super(CustomArgumentParser, self).format_usage()
            return usage.replace('usage: ', 'Usage: ')

        def format_help(self):
            help = super(CustomArgumentParser, self).format_help()
            return help.replace('usage: ', 'Usage: ') \
                       .replace('buildpath PATH', 'buildpath=PATH') \
                       .replace('timeout SECONDS', 'timeout=SECONDS')

    arg_parser = CustomArgumentParser(
        prefix_chars='/-', allow_abbrev=False, add_help=False)

    main_args = arg_parser.add_argument_group('Options')
    main_args.add_argument(
        '/?', '/help', action='help',
        help='Show information about command-line arguments.',
    )
    main_args.add_argument(
        '/b', '/background', dest='run_in_background', action='store_true',
        help='Create a background process that is detached from the current '
             'terminal (if any) and allows the calling process to continue '
             'immediately instead of blocking until finished, and closes after '
             'the first build. Implies "/close" and "/auto".'
    )
    main_args.add_argument(
        '/c', '/close', dest='close_after_first_build', action='store_true',
        help='Close the yycboost process after the first build; otherwise, '
             'it stays open until manually closed.',
    )
    main_args.add_argument(
        '/a', '/auto', dest='auto', action='store_true',
        help='Use default values rather than prompting the user for any input.',
    )
    main_args.add_argument(
        '-buildpath', dest='build_bff_path', nargs=1, metavar='PATH',
        help='The path of the "build.bff" file corresponding to the target. If '
             'not specified, the user is prompted to enter a path on the '
             'terminal, unless "/auto" is set, in which case the default value '
             'of "{}" is used.'.format(BuildBff.PATH_DEFAULT),
    )
    main_args.add_argument(
        '-timeout', dest='timeout', nargs=1, metavar='SECONDS',
        type=float, default=[300], help='The number of seconds to wait for '
            '"build.bff" to appear, if it does not already exist, before '
            'aborting the process. Defaults to 300 seconds, i.e. 5 minutes, '
            'if not specified.',
    )

    other_args = arg_parser.add_argument_group('Positional arguments')
    other_args.add_argument(
        'cpp_dir', metavar='CPP_DIR', nargs='?', help='Load cache directory '
        'from command line (no injection, only cleanup, handy for GMS1.4) '
        '[Note: this option doesn\'t appear to do anything useful; it has '
        'been kept for backward compatibility, but may be removed in the '
        'future. The "cache directory" referred to here is the project-'
        'specific directory for .gml.cpp files, for example "%%LocalAppData%%\\'
        'GameMakerStudio2\\Cache\\GMS2CACHE\\YYCBoost_2083F10D\\YYCBoost\\'
        'Default\Scripts\llvm-win"; if this argument is present, then the '
        '"build.bff" file is not loaded and its path need not be given.]',
    )

    return arg_parser.parse_args(*args, **kwds)


if __name__ == "__main__":
    queue = Queue()
    freeze_support()

    def handle_sigint(*args, **kwargs):
        if not current_process().daemon:
            # To avoid duplicates, only print this message from the parent process. 
            cprint("Terminating...", "magenta")
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    args = parse_args()

    # If "/background" is set, launch as a background process and then exit:
    if args.run_in_background:
        abs_argv0 = os.path.join(os.getcwd(), sys.argv[0])
        if os.path.samefile(abs_argv0, sys.executable):
            # Guess we are running as a standalone executable file.
            new_argv = [abs_argv0] + sys.argv[1:]
        elif '__file__' in globals() and os.path.samefile(sys.argv[0], __file__):
            # Guess we are running as a script under an executable interpreter.
            new_argv = [sys.executable] + sys.argv
        else:
            # Unable to determine correct command line to relaunch self.
            cprint('ERROR: failed to launch background process!', 'red')
            sys.exit(1)

        # Ensure that "/close" and "/auto" are set and "/background" is not
        # set for the background process:
        new_argv = [arg for arg in new_argv if arg not in ('/b', '/background')]
        if all(arg not in new_argv for arg in ('/c', '/close')):
            new_argv.append('/close')
        if all(arg not in new_argv for arg in ('/a', '/auto')):
            new_argv.append('/auto')

        proc = subprocess.Popen(
            new_argv, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL,
            creationflags=CREATE_NO_WINDOW
        )
        print('Continuing in background as PID {} with command line "{}".'
               .format(proc.pid, ' '.join(new_argv)))
        sys.exit(0)

    if getattr(sys, "frozen", False):
        yyc_boost_dir = os.path.dirname(sys.executable)
    else:
        yyc_boost_dir = os.path.dirname(os.path.abspath(__file__))

    config_fname = "config.json"
    config_fpath = os.path.join(yyc_boost_dir, config_fname)

    if args.cpp_dir is not None:
        # Load cache directory from command line (no injection, only cleanup,
        # handy for GMS1.4)

        # This doesn't seem to do anything except print errors at the moment;
        # what is the "cleanup" referred to in the above comment? Should this be
        # removed?

        build = None
        path_cpp = args.cpp_dir
    else:
        # Config
        config = {}

        default = BuildBff.PATH_DEFAULT
        [build_bff_path] = args.build_bff_path or [None]
        [timeout] = args.timeout
        time_limit = perf_counter() + timeout

        if not build_bff_path and not args.auto:
            build_bff_path = input(
                "Enter path to the build.bff file [{}]: ".format(default))
        if not build_bff_path:
            build_bff_path = default
        config["build_bff"] = build_bff_path

        # Load build.bff
        wait_for_file(build_bff_path, time_limit)
        try:
            build = BuildBff(build_bff_path)
            print("Loaded build.bff")
        except:
            cprint('ERROR: Could not load "{}":'.format(build_bff_path), 'red')
            traceback.print_exc()
            sys.exit(1)

        # Project info
        path_cpp = build.get_cpp_dir()
        print("Project:", build.get_project_name())
        print("Config:", build.get_config())
        print("Project directory:", build.get_project_dir())

    print("Target directory:", path_cpp)

    # Check for permission
    if not args.auto:
        if input("Do you really want to modify the files? [Y/n] ") == "n":
            cprint("Canceled", "magenta")
            sys.exit(0)

    # Copy custom headers
    _cpp_dir = os.path.join(yyc_boost_dir, "cpp")
    wait_for_file(path_cpp, time_limit)
    for f in os.listdir(_cpp_dir):
        copy_file(os.path.join(_cpp_dir, f), path_cpp)

    # Modify C++ files
    initial_file_count = 0
    for root, _, files in os.walk(path_cpp):
        initial_file_count += len(files)
        for fname in files:
            cpp_path = os.path.join(root, fname)
            queue.put((cpp_path, build,))

    if not args.close_after_first_build:
        event_handler = EventHandler(build)
        observer = Observer()
        observer.schedule(event_handler, path_cpp, recursive=True)
        observer.start()

    processes = []
    for i in range(cpu_count()):
        bound = inspect.signature(process_fn).bind(
            yyc_boost_dir=yyc_boost_dir, id=i, queue=queue,
            exit_when_queue_empty=args.close_after_first_build,
        )
        p = Process(target=process_fn, kwargs=bound.arguments, daemon=True)
        p.start()
        processes.append(p)

    # Wait for all processes to exit (or wait forever):
    for p in processes:
        while p.is_alive():
            p.join(1)

    if queue.empty() and args.close_after_first_build:
        print('First build complete, in which {} files were found; exiting.'
              .format(initial_file_count))
    else:
        cprint('ERROR: all worker processes have exited abnormally!', 'red')
