// log-dex.js — report the loaded .dex files and the app's classloader.
// Baseline for reverse-engineering: tells you what's actually on disk (native
// loaders can hide things under obfuscated namespaces).
Java.perform(function () {
    var PathClassLoader = Java.use('dalvik.system.PathClassLoader');
    PathClassLoader.$init.implementation = function (dexPath, parent) {
        this.$init(dexPath, parent);
        console.log('[dex] PathClassLoader:', dexPath);
    };

    var DexFile = Java.use('dalvik.system.DexFile');
    DexFile.loadClass.implementation = function (name, loader) {
        var cls = this.loadClass(name, loader);
        console.log('[dex] loadClass: ' + name);
        return cls;
    };

    // Dump the current path showcases all classpath entries
    var cl = Java.use('java.lang.ClassLoader');
    var getSystemLoader = cl.getSystemClassLoader();
    try {
        var path = getSystemLoader.getResource('').toString();
        console.log('[+] system classpath: ' + path);
    } catch (e) {}

    console.log('[+] log-dex.js loaded');
});