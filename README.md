Introduction
------------

First very beasic bersion of a CLI for the DW script debugger API.

It is a command based debugger with supports for:

* Adding/removing breakpoints
* Step In
* Step Over
* Show stack trace
* Show variables at various stack frames

Implemented commands
--------------------

Connect
=======

Command: `connect`

This is the first command that should be issued. It creates a client resource on DW and allows all other fuctions to work.

<h3>Example</h3>
```
(dw) connect
<Response [204]>
```

Quit
====

Command: `q`

This command closes and cleans up the session, then quits the debugger

Help
====

Built-in help that lists commands and gives some (incomplete) information about them

Breakpoints
===========

Commands:

* Set: `bp <filepath> <line>`
* List `bp`, `sb`
* Delete: `db <id>` (&lt;id&gt; is provided by the previous command)

<h3>Example</h3>

```
(dw) bp /app_hrz_js/cartridge/controllers/Product.js 21
OK
(dw) bp /app_hrz_js/cartridge/controllers/Product.js 24
OK
(dw) bp /app_hrz_js/cartridge/controllers/Product.js 25
OK
(dw) bp
1: /app_hrz_js/cartridge/controllers/Product.js:21
2: /app_hrz_js/cartridge/controllers/Product.js:24
3: /app_hrz_js/cartridge/controllers/Product.js:25
(dw) db 1
OK
(dw) bp
1: /app_hrz_js/cartridge/controllers/Product.js:24
2: /app_hrz_js/cartridge/controllers/Product.js:25
```

Using threads
=============

Commands:

* List current threads: `t`
* Select a thread to debug: `use <id>`

<h3>Example</h3>

```
(dw) t
1026: running
(dw) t
1222: halted
    -toplevel-  // /app_hrz_js/cartridge/controllers/Product.js:1
```

Stack + Stack variables
=======================

Commands:

* View stack trace: `st`
* Show variables on top of the stack: `v`
* Show variables in non top level of the stack: `v <stack fram no>`

<h3>Example</h3>

```
(dw) v
arguments: org.mozilla.javascript.Arguments@180d1e1 (Type: org.mozilla.javascript.Arguments)
(dw) st
0: showFull() (/app_hrz_js/cartridge/controllers/Product.js:23)
1: -anonymous-() (/app_hrz_js/cartridge/scripts/guard.js:124)


    function showFull()
    {
>   	show('full');
    }
```

Navigating code
===============

Commands:

* Setp into: `s`
* Step over: `so`
