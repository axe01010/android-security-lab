// sqlite-sieve.js — log SQL statements executed by the app (SQLite).
Java.perform(function () {
    var SQLiteDatabase = Java.use('android.database.sqlite.SQLiteDatabase');
    try {
        SQLiteDatabase.execSQL.overload('java.lang.String').implementation = function (sql) {
            console.log('[sql] execSQL: ' + sql);
            return this.execSQL(sql);
        };
    } catch (e) {}

    try {
        SQLiteDatabase.query.overload('java.lang.String', '[Ljava.lang.String;', 'java.lang.String',
            '[Ljava.lang.String;', 'java.lang.String', 'java.lang.String', 'java.lang.String').implementation = function (t, cols, sel, args, g, h, o) {
            console.log('[sql] SELECT from ' + t + ' where ' + (sel || '-'));
            return this.query(t.apply(this, arguments));
        };
    } catch (e) {}

    // rawQuery used by many ORMs
    try {
        var RQ = Java.use('android.database.sqlite.SQLiteDatabase');
        RQ.rawQuery.overload('java.lang.String', '[Ljava.lang.String;').implementation = function (sql, args) {
            console.log('[sql] raw: ' + sql);
            return this.rawQuery(sql, args);
        };
    } catch (e) {}

    console.log('[+] sqlite-sieve.js loaded');
});