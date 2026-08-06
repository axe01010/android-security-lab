// universal-ssl.js — bypass SSL/TLS verification and pinning for OkHttp & HttpURLConnection.
// Usage: frida -U -f com.target.app -l universal-ssl.js --no-pause
Java.perform(function () {
    var modes = ['SSLContext', 'HttpsURLConnection', 'OkHttp3', 'TrustManager'];

    // 1) Trust-all TrustManager on the UNKNOWN TLS stack
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    try {
        var TrustManager = Java.registerClass({
            name: 'com.frida.TrustAllX509',
            implements: [Java.use('javax.net.ssl.X509TrustManager')],
            methods: {
                checkClientTrusted: function () {},
                checkServerTrusted: function () {},
                getAcceptedIssuers: function () { return []; }
            }
        });
        SSLContext.getInstance('TLS').init(null, [TrustManager.$new()], null);
        console.log('[+] SSLContext trust manager replaced');
    } catch (e) { console.log('[!] SSLContext init failed: ' + e); }

    // 2) OkHttp CertificatePinner
    try {
        var Cp = Java.use('okhttp3.CertificatePinner');
        Cp.check.overload('java.lang.String', 'java.util.List').implementation = function (host, pins) {
            console.log('[*] pin bypassed for ' + host);
        };
        console.log('[+] OkHttp CertificatePinner neutralized');
    } catch (e) { console.log('[.] no OkHttp pinner found: ' + e); }

    // 3) HttpsURLConnection host-verifier (defense-in-depth)
    try {
        var Hvc = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        Hvc.checkTrustedRecursive.overload('[Ljava.security.cert.X509Certificate;', 'java.lang.String',
            'java.lang.String', 'int', 'boolean', 'java.util.List').implementation = function (chain, host, algo, i01, fake, e) {
            return false;
        };
        console.log('[+] Conscrypt trust recursion disabled');
    } catch (e) { console.log('[i] conscrypt hook not applied: ' + e); }

    console.log('[+] universal-ssl.js loaded — OkHttp/Conscrypt/SSL hooks active');
});