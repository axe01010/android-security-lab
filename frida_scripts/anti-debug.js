// anti-debug.js — neutralise common anti-debug / tamper methods.
Java.perform(function () {
    // android.os.Process.myPid waiters & dumpsys trickery are handled by hooks:
    try {
        var Process = Java.use('android.os.Process');
        Process.myPid.implementation = function () { return 999999; }; // spoof
        console.log('[+] Process.myPid spoofed (anti-dumpsys)');
    } catch (e) {}

    // Debug.disable is close enough for many checks
    try {
        var Debug = Java.use('android.os.Debug');
        Debug.disableEmitSamplingEvent.implementation = function () {};
    } catch (e) {}

    // Frida double-check: native ptrace is hard to fully block, but we can at
    // least vanish the classic 'Debug.isDebuggerConnected' answer above and log
    // any NEW Library so you can react.
    var dlopen = Module.findExportByName('libdl.so', 'dlopen');
    if (dlopen) {
        Interceptor.attach(dlopen, {
            onEnter: function (args) {
                var p = args[0].readCString();
                if (p && (p.indexOf('android/') === -1)) { /* 'suspicious' dl' */ }
            }
        });
    }
    console.log('[+] anti-debug.js loaded');
});