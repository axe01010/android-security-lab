Java.perform(function () {
    console.log("[+] hooking OkHttp CertificatePinner");
    var Cp = Java.use("okhttp3.CertificatePinner");
    Cp.check.overload('java.lang.String', 'java.util.List').implementation = function(h, ps) {
        console.log("[*] cert pin bypassed for " + h);
    };
});