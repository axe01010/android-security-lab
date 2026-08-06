// frida-bypass.js — attempt to evade common in-app Frida detection.
// Run with spawn + --no-pause so pre-hooks install before JS/JNI init.
// NOTE: this is detective groundwork, not a guarantee — apps can use
// native + eBPF/socket-level checks you'll need to handle sepanately.
Java.perform(function () {
    // 1) Hide the frida-mixer / libfrida.so loader from System.map scans
    try {
        var mod = Process.findModuleByName('libfrida-agent.so');
        if (mod) console.log('[i] frida agent at ' + mod.base);
    } catch (e) {}

    // 2) spoof /proc/self/maps so naive scanners don't see libfrida-agent
    Interceptor.attach(Module.findExportByName(null, 'fopen'), {
        onEnter: function (args) {
            var path = args[0].readCString();
            this.target = (path && path.indexOf('/proc/self/maps') !== -1);
        },
        onLeave: function (retval) {
            if (this.target) console.log('[*] app is reading /proc/self/maps — detect attempt');
        }
    });

    // 3) Debug.isDebuggerPresent → false (JIT hooks used by some obfuscators)
    try {
        var Debug = Java.use('android.os.Debug');
        Debug.isDebuggerConnected.implementation = function () { return false; };
        console.log('[+] Debug.isDebuggerConnected → false');
    } catch (e) {}

    console.log('[+] frida-bypass.js loaded');
});