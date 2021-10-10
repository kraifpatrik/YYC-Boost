# Multithreading
Using function [yyc_run_in_thread](./yyc_run_in_thread.html) you can run
functions in a separate thread. This is handy for example when you need to do
a heavy computation without freezing the game. [Mutexes](./YYC_Mutex.html) and
[semaphores](./YYC_Semaphore.html) are available too!

```gml
/// @desc Create event
yyc_run_in_thread(function () {
    while (true)
    {
        show_debug_message("This does not block the main thread!");
    }
});
```

See [YYC_Task](./YYC_Task.html) and [YYC_GroupTask](./YYC_GroupTask.html) if you
would like to utilize threads to run tasks.

## Known limitations
Following is a list of GM features that are known to not work when run in a
separate thread:

* Rendering to surfaces

*Have you found some more? Please, let me know!*
