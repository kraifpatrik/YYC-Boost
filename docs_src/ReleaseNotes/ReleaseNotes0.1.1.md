# Release notes 0.1.1
* Fixed an exception raised when `yycboost.exe` is started before the `build.bff` file is created.
* Removed the `config.json` file which remembered the path to the `build.bff`. You can now enter the path (or hit enter to use the default one) on each start. This is useful in case you have multiple versions of GMS2 installed (e.g. stable and beta release).
