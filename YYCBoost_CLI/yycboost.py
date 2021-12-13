# -*- coding: utf-8 -*-
import json
import os
import os.path
import signal
import sys
import time
import subprocess
import traceback
import atexit
import threading
import datetime
from subprocess import DEVNULL, CREATE_NO_WINDOW
from multiprocessing import (
    Process, Queue, cpu_count, freeze_support, parent_process,
)
from argparse import ArgumentParser

from termcolor import cprint
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.build_bff import BuildBff
from src.processor import Processor
from src.utils import *


DEFAULT_TIMEOUT = 300

queue = Queue()


def process_fn(yyc_boost_dir: str, id: int, queue: Queue):
    print(f"Processor ({id}): Started")
    while True:
        cpp_path, build = queue.get(block=True)
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
            res = super(CustomArgumentParser, self).format_usage()
            return res.replace('usage: ', 'Usage: ')

        def format_help(self):
            res = super(CustomArgumentParser, self).format_help()
            for sname, lname, meta in (
                ('bp', 'buildpath', 'PATH'), ('pf', 'pidfile', '[PATH]'),
                ('t', 'timeout', 'SECONDS'), ('l', 'logfile', 'PATH'),
                ('j', 'threads', 'COUNT')
            ):
                e = ('[=%s]' % meta[1:-1]) if meta[0] == '[' else ('=%s' % meta)
                f = lambda s: s.format(sname, lname, meta, e) 
                res = res.replace(f('-{0} {2}, -{1} {2}'), f('-{0}, -{1}{3}'))
                res = res.replace(f('-{0} {2}'),           f('-{0}{3}'))
            return res.replace('usage: ', 'Usage: ')

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
             'immediately instead of blocking until finished. Implies "/auto".'
    )
    main_args.add_argument(
        '/c', '/close', dest='close_existing_instance', action='store_true',
        help='Signal an existing instance of YYCBoost to exit, by deleting '
             'the file given by the "-pidfile" option, or, if that option '
             'is absent, the default PID file location. Do not perform any '
             'code injection and immediately exit after this.',
    )
    main_args.add_argument(
        '/a', '/auto', dest='auto', action='store_true',
        help='Use default values rather than prompting the user for any input.',
    )
    main_args.add_argument(
        '-bp', '-buildpath', dest='build_bff_path', nargs=1, metavar='PATH',
        help='The path of the "build.bff" file corresponding to the target. If '
             'not specified, the user is prompted to enter a path on the '
             'terminal, unless "/auto" is set, in which case the default value '
             'of "{}" is used.'.format(BuildBff.PATH_DEFAULT),
    )
    main_args.add_argument(
        '-pf', '-pidfile', dest='pidfile_path', nargs='?', metavar='PATH',
        const=True, help='Creates a text file at "PATH" containing the main '
             'process ID of YYCBoost and watches it for changes: if the file '
             'is deleted, moved, or its contents changed, this acts as a '
             'termination signal and causes the present instance to exit; '
             'otherwise, YYCboost deletes the PID file when exiting normally. '
             'If "PATH" exists, YYCBoost overwrites it. If "-pidfile" is given '
             'without a "PATH" argument, then it defaults to "yycboost.pid" in '
             'the current user\'s home directory (on Windows: %%USERPROFILE%%).'
    )
    main_args.add_argument(
        '-t', '-timeout', dest='timeout', nargs=1, metavar='SECONDS', type=float,
        help='Close after this many seconds, or stay open until explicitly '
             'close if SECONDS is 0. If not specified, defaults to {} if '
             '"/background" is set, or otherwise to 0.'.format(DEFAULT_TIMEOUT)
    )
    main_args.add_argument(
        '-j', '-threads', dest='threads', nargs=1, metavar='COUNT', type=int,
        help='The number of CPU cores to use. If not specified, defaults '
             'to the total number of cores on the system.',
    )
    main_args.add_argument(
        '-l', '-logfile', dest='logfile', nargs=1, metavar='PATH',
        help='Print status messages to PATH rather than to stdout/err. This is '
             'useful for debugging while the "/background" option is active.'
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
    # Set handler to exit with a message upon keyboard interrupt:
    def handle_sigint(*args, **kwargs):
        if parent_process() is None: 
            cprint("Terminating...", "magenta")
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    freeze_support()

    args = parse_args()

    # If a log file is configured, open that file (appending, with line
    # buffering), and redirect stdout and stderr to the open file.
    if args.logfile and not args.run_in_background:
        sys.stdout = sys.stderr = open(args.logfile[0], 'a', 1)
        if sys.stdout.tell(): print('')
        print('--- Log opened at {} by PID {} ---'
              .format(datetime.datetime.now(), os.getpid()))

    if getattr(sys, "frozen", False):
        yyc_boost_dir = os.path.dirname(sys.executable)
    else:
        yyc_boost_dir = os.path.dirname(os.path.abspath(__file__))

    # TODO: This doesn't seem to be used by anything; should it be deleted?
    config_fname = "config.json"
    config_fpath = os.path.join(yyc_boost_dir, config_fname)

    # What `args.pidfile_path` would be after substituting default values:
    actual_pidfile_path = \
        os.path.join(os.path.expanduser('~'), 'yycboost.pid') \
        if args.pidfile_path in (None, True) else args.pidfile_path

    # If "/close" is set, delete any existing PID file and then exit:
    if args.close_existing_instance:
        if os.path.exists(actual_pidfile_path):
            print('Deleting PID file at "{}"...'.format(actual_pidfile_path),
                  end=' ')
            os.remove(actual_pidfile_path)
        else:
            print('PID file "{}" does not exist.'.format(actual_pidfile_path),
                  end=' ')
        print('Exiting.')
        sys.exit(0)

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

        # Ensure that "/auto" is set and "/background" is not set for the
        # background process, and that "-timeout" is set with the default
        # value if not otherwise specified:
        new_argv = [arg for arg in new_argv if arg not in ('/b', '/background')]
        if all(arg not in new_argv for arg in ('/a', '/auto')):
            new_argv.append('/auto')
        if args.timeout is None:
            new_argv.append('-timeout={}'.format(DEFAULT_TIMEOUT))

        proc = subprocess.Popen(
            new_argv, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL,
            creationflags=CREATE_NO_WINDOW
        )
        print('Continuing in background as PID {} with command line "{}".'
               .format(proc.pid, ' '.join(new_argv)))
        sys.exit(0)

    # If '-pidfile' is set, write the PID file and set appropriate handlers:
    main_thread_exit = threading.Event()
    if args.pidfile_path:
        with open(actual_pidfile_path, 'w') as file:
            file.write(str(os.getpid()))
        print('Wrote PID file at "{}" with contents "{}".'
              .format(actual_pidfile_path, os.getpid()))

        # Set handler to exit if PID file deleted, moved or contents changed:
        class PIDHandler(FileSystemEventHandler):
            def _on_deleted_modified_moved(self, _event):
                if os.path.exists(actual_pidfile_path):
                    with open(actual_pidfile_path, 'r') as file:
                        text = file.read().strip()
                        if text == str(os.getpid()): return
                        exit_message = 'Our PID file at "{}" now contains: ' \
                            '"{}". Exiting.'.format(actual_pidfile_path, text)
                else:
                    exit_message = '"Our PID file at "{}" no longer exists. ' \
                        'Exiting.'.format(actual_pidfile_path)
                if not main_thread_exit.is_set():
                    cprint(exit_message, 'yellow')
                    main_thread_exit.set()
            on_deleted = on_modified = on_moved = _on_deleted_modified_moved
        (pid_observer := Observer()).schedule(
            PIDHandler(), os.path.dirname(actual_pidfile_path), recursive=False)
        pid_observer.start()

        # Set handler to delete PID file if unmodified upon exit:
        @atexit.register
        def handle_exit():
            try:
                if os.path.exists(actual_pidfile_path):
                    with open(actual_pidfile_path, 'r') as file:
                        if file.read().strip() != str(os.getpid()): return
                    # Set this flag so the above handler isn't triggered:
                    main_thread_exit.set()
                    os.remove(actual_pidfile_path)
            except IOError:
                pass

    if args.cpp_dir is not None:
        # Load cache directory from command line (no injection, only cleanup,
        # handy for GMS1.4)

        # TODO: This doesn't seem to do anything except print errors at the
        # moment; what is the "cleanup" referred to in the above comment?
        # Should this be removed?

        build = None
        path_cpp = args.cpp_dir
    else:
        # TODO: This doesn't seem to be used for anything. Should it be deleted?
        config = {}

        # Configure instance timeout:
        time_limit = perf_counter() + args.timeout[0] \
                     if args.timeout and args.timeout[0] else None

        # Configure path of "build.bff":
        [build_bff_path] = args.build_bff_path or [None]
        if not build_bff_path and not args.auto:
            build_bff_path = input("Enter path to the build.bff file [{}]: "
                                   .format(BuildBff.PATH_DEFAULT))
        if not build_bff_path:
            build_bff_path = BuildBff.PATH_DEFAULT
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

        # Print project info:
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

    event_handler = EventHandler(build)
    observer = Observer()
    observer.schedule(event_handler, path_cpp, recursive=True)
    observer.start()

    process_count = args.threads[0] if args.threads else cpu_count()
    processes = []
    for i in range(process_count):
        p = Process(target=process_fn, args=(yyc_boost_dir, i, queue),
                    daemon=True)
        p.start()
        processes.append(p)

    while time_limit is None or perf_counter() < time_limit:
        # It is necessary to sleep for only short periods of time so that the
        # main thread remains responsive to signals such as SIGINT:
        if main_thread_exit.wait(1): break
    else:
        print('Timeout of {:.2f} seconds exceeded; exiting.'
              .format(args.timeout[0]))
