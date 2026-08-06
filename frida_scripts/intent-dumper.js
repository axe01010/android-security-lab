// intent-dumper.js — log every Intent the app starts/startsActivity.
// Surfaces component boundaries (exported vs private) and deep-link abuse.
Java.perform(function () {
    var ContextImpl = Java.use('android.app.ContextImpl');
    try {
        ContextImpl.startActivity.overload('android.content.Intent').implementation = function (intent) {
            console.log('[intent] >>> startActivity ' + intent);
            // include the deep link (if the action carries a URI)
            var data = intent.getData();
            if (data) console.log('[intent]    data: ' + data.toString());
            return this.startActivity(intent);
        };
    } catch (e) {}

    try {
        var I = Java.use('android.content.Intent');
        I.setClassName.overload('java.lang.String', 'java.lang.String').implementation = function (pkg, cls) {
            console.log('[intent] setClassName → ' + pkg + '/' + cls);
            return this.setClassName(pkg, cls);
        };
    } catch (e) {}

    // also catch Activity#startActivity direct path (non-Context)
    try {
        var Act = Java.use('android.app.Activity');
        Act.startActivity.overload('android.content.Intent').implementation = function (intent) {
            console.log('[intent] (activity) startActivity ' + intent);
            return this.startActivity(intent);
        };
    } catch (e) { console.log('[i] Activity hook n/a'); }

    console.log('[+] intent-dumper.js loaded');
});