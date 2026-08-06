// shared-prefs.js — mirror SharedPreferences reads/writes (incl. secrets the
// app persists in plaintext XML). For validating storage hygiene.
Java.perform(function () {
    var sp = Java.use('android.app.SharedPreferencesImpl.EditorImpl');
    try {
        sp.commit.implementation = function () {
            console.log('[prefs] commit()');
            return this.commit();
        };
    } catch (e) {}

    var EditorImpl = Java.use('android.app.SharedPreferencesImpl$EditorImpl');
    EditorImpl.putString.overload('java.lang.String', 'java.lang.String').implementation = function (k, v) {
        console.log('[prefs] putString ' + k + ' = ' + v);
        return this.putString(k, v);
    };
    EditorImpl.putStringSet.overload('java.lang.String', 'java.util.Set').implementation = function (k, v) {
        console.log('[prefs] putStringSet ' + k + ' = ' + v);
        return this.putStringSet(k, v);
    };
    EditorImpl.putInt.implementation = function (k, v) {
        console.log('[prefs] putInt ' + k + ' = ' + v);
        return this.putInt(k, v);
    };

    var SPI = Java.use('android.app.SharedPreferencesImpl');
    SPI.getSharedPreferences.implementation = function (file, mode) {
        console.log('[prefs] open ' + file.getName());
        return this.getSharedPreferences(file, mode);
    };

    console.log('[+] shared-prefs.js loaded');
});