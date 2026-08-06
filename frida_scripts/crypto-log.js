// crypto-log.js — log cipher init params (mode) and block the weakest ones.
// Great for deciding whether the app uses AES/GCM or ECB.
Java.perform(function () {
    try {
        var Cp = Java.use('javax.crypto.Cipher');
        Cp.init.overload('int', 'java.security.Key').implementation = function (mode, key) {
            console.log('[crypto] Cipher.init mode=' + mode + ' algo=' + key.getAlgorithm());
            return this.init(mode, key);
        };
        Cp.init.overload('int', 'java.security.Key', 'java.security.spec.AlgorithmParameterSpec').implementation = function (mode, key, spec) {
            console.log('[crypto] Cipher.init mode=' + mode + ' algo=' + key.getAlgorithm() + ' spec=' + spec);
            return this.init(mode, key, spec);
        };
    } catch (e) {}

    try {
        var MessageDigest = Java.use('java.security.MessageDigest');
        MessageDigest.update.overload('[B').implementation = function (data) {
            console.log('[hash] input length=' + data.length);
            return this.update(data);
        };
    } catch (e) {}

    console.log('[+] crypto-log.js loaded');
});