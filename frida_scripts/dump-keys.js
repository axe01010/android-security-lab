// dump-keys.js — log cryptographic key + secret material at the JCA boundary.
// Surfaces what a target 'app crypto' material really is (for review only).
Java.perform(function () {
    // SecretKeySpec: the trivial common key container
    var SKS = Java.use('javax.crypto.spec.SecretKeySpec');
    SKS.$init.overload('[B', 'java.lang.String').implementation = function (bytes, algo) {
        var hex = Array.prototype.map.call(bytes, function (b) {
            return ('0' + (b & 0xff).toString(16)).slice(-2);
        }).join('');
        console.log('[key] SecretKeySpec(' + algo + ') = ' + hex.slice(0, 64));
        return this.$init(bytes, algo);
    };

    // KeyStore load → run Cipher/DN now: capture AES derived above
    try {
        var KeyStore = Java.use('java.security.KeyStore');
        KeyStore.setKeyEntry.implementation = function (alias, key, pwd, chain) {
            console.log('[key] keystore.setKeyEntry alias=' + alias + ' key=' + key);
            return this.setKeyEntry(alias, key, pwd, chain);
        };
    } catch (e) {}

    // base64 of the secret (often the actual storage form)
    var B64 = Java.use('android.util.Base64');
        B64.encodeToString.overload('[B', 'int').implementation = function (data, flags) {
        var out = this.encodeToString(data, flags);
        if (data.length > 0) console.log('[b64] → ' + out.slice(0, 80));
        return out;
    };
    console.log('[+] dump-keys.js loaded');
});