// network-log.js — log HTTP(S) activity at the OkHttp + java sockets layers.
// Great first step for mapping what an app calls out to without MITM.
Java.perform(function () {
    // OkHttp Request URL
    try {
        var Req = Java.use('okhttp3.Request');
        var Method = Java.use('java.lang.String');
        // intercept Url surface via toString of built requests
        var BuiltReq = Java.use('okhttp3.Request$Builder');
        BuiltReq.build.implementation = function () {
            var r = this.build();
            var url = r.url().toString();
            var method = r.method();
            console.log('[net] ' + method + ' ' + url);
            return r;
        };
    } catch (e) { console.log('[i] okhttp not present: ' + e); }

    // HttpURLConnection base sockets (non-OkHttp clients)
    var SockImpl = Java.use('com.android.okhttp.internal.http.HttpURLConnectionImpl');
    try {
        SockImpl.getInputStream.implementation = function () {
            console.log('[net] GET start: ' + this.getURL());
            return this.getInputStream();
        };
    } catch (e) {}

    // Android java.net URL.openConnection (generic)
    var URL = Java.use('java.net.URL');
    URL.openConnection.overload().implementation = function () {
        var c = this.openConnection();
        console.log('[net] openConnection ' + this.toString());
        return c;
    };

    console.log('[+] network-log.js loaded');
});