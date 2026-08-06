// stack-tracer.js — print the Java stack trace on *new* Activity launches.
// Helps you understand WHAT drives each component (explicit vs implicit).
Java.perform(function () {
    var StackTrace = Java.use('android.os.StrictMode'); // to have a stable anchor
    var ActivityThread = Java.use('android.app.ActivityThread');
    ActivityThread.performLaunchActivity.implementation = function (r, ei, inst, ei2, fun, id, stackTrace, config) {
        console.log('\n=== [launch] ' + r.getActivityInfo().name + ' ===');
        var ex = Java.use('java.lang.Exception').$new('marker');
        var el = ex.getStackTrace();
        for (var i = 1; i < Math.min(el.length, 12); i++) {
            console.log('   at ' + el[i].toString());
        }
        return this.performLaunchActivity(r, ei, inst, ei2, fun, id, stackTrace, config);
    };
    console.log('[+] stack-tracer.js loaded');
});