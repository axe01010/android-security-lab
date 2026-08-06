// root-bypass.js — neutralise common root-collection checks in Java.
// Many apps call /system/xbin/su, isDeviceRooted(), Runtime.exec("su").
Java.perform(function () {
    // 1) Runtime.exec → block anything referencing 'su' or 'magisk'
    var Rt = Java.use('java.lang.Runtime');
    Rt.exec.overload('java.lang.String').implementation = function (cmd) {
        if (/su|\bsh\b|magisk|root/i.test(cmd)) {
            console.log('[blocked] exec("' + cmd + '")');
            return null;
        }
        return this.exec(cmd);
    };

    // 2) ProcessBuilder start with red flags → throw
    var Pb = Java.use('java.lang.ProcessBuilder');
    Pb.start.implementation = function () {
        var cmd = this.command();
        if (cmd && cmd.join && /su|magisk/i.test(cmd.join(' '))) {
            throw new Error('root check blocked');
        }
        return this.start();
    };

    // 3) common boolean: isDeviceRooted → false
    var candidates = [
        'com.scottyab.rootbeer.RootBeer',
        'com.stericson.RootTools.RootTools'
    ];
    candidates.forEach(function (cls) {
        try {
            var k = Java.use(cls);
            Java.choose(cls, {
                onMatch: function (obj) {
                    for (var f in k.methods) {
                        var m = k.methods[f];
                        if (/isDeviceRooted|checkSuBinary|isRootAvailable/i.test(m)) {
                            k[m.name] && (k[m.name].overloads.forEach(function (o) {
                                o.implementation = function () { return false; };
                            }));
                        }
                    }
                }, onComplete: function () {}
            });
        } catch (e) {}
    });

    console.log('[+] root-bypass.js loaded');
});