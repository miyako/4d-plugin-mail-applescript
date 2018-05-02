# 4d-plugin-mail-applescript
Get the source (MIME) of selected emails from Apple Mail via [Scripting Bridge](https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/ScriptingBridgeConcepts/Introduction/Introduction.html)

### Platform

| carbon | cocoa | win32 | win64 |
|:------:|:-----:|:---------:|:---------:|
|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|||

### Version

<img src="https://cloud.githubusercontent.com/assets/1725068/18940649/21945000-8645-11e6-86ed-4a0f800e5a73.png" width="32" height="32" /> <img src="https://cloud.githubusercontent.com/assets/1725068/18940648/2192ddba-8645-11e6-864d-6d5692d55717.png" width="32" height="32" />

### Releases

[2.0](https://github.com/miyako/4d-plugin-mail-applescript/releases/tag/2.0)

## Syntax

```
selection:=Mail Get selection (mode)
```

Parameter|Type|Description
------------|------------|----
mode|LONGINT|``Mail selection source`` or ``Mail selection subject``
selection|TEXT|``JSON`` array (collection or object, see below)

### Discussion

The objective is to import email directly from the Mail app via drag and drop. 

In applescript one could do something like this:

```applescript
tell application "Mail"
	set ss to {}
	repeat with s in selection as list
		copy {source:source of s, id:id of s} to the end of ss
	end repeat
	ss
end tell
```

Note that ``selection`` must be cast to a [``list``](https://developer.apple.com/library/content/documentation/AppleScript/Conceptual/AppleScriptLangGuide/reference/ASLR_classes.html#//apple_ref/doc/uid/TP40000983-CH1g-BBCDBHIE) in order to be used in a [``repeat``](https://developer.apple.com/library/content/documentation/AppleScript/Conceptual/AppleScriptLangGuide/reference/ASLR_control_statements.html#//apple_ref/doc/uid/TP40000983-CH6g-128481).

The reason why ``copy {source:source of s, id:id of s} to the end of ss`` is faster than ``set ss to ss & {source:source of s, id:id of s}`` is explained in the [documentation](https://developer.apple.com/library/content/documentation/AppleScript/Conceptual/AppleScriptLangGuide/reference/ASLR_classes.html#//apple_ref/doc/uid/TP40000983-CH1g-BBCDBHIE).

The plugin does a similar thing but using [SBApplication](https://developer.apple.com/documentation/scriptingbridge/sbapplication?language=objc). 

``sdef`` and ``sdp`` were used to export the ``obj-c`` interface.

```bash
sdef /Applications/Mail.app | sdp -fh --basename mail
```

The code to obtain the list of ``sources`` or ``subject`` looks like this:

```objc
mailApplication *application = [SBApplication applicationWithBundleIdentifier:@"com.apple.mail"];
SBElementArray *selection = [application selection];
NSArray *sources = [selection arrayByApplyingSelector:@selector(source)];
``` 

The reason why it is good to use ``SBElementArray`` to create a filtered array is explained in the [documentation](https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/ScriptingBridgeConcepts/ImproveScriptingBridgePerf/ImproveScriptingBridgePerf.html#//apple_ref/doc/uid/TP40006104-CH6-SW1).

The code to obtain the list of ``id`` is somewhat different:

```objc
mailApplication *application = [SBApplication applicationWithBundleIdentifier:@"com.apple.mail"];
SBElementArray *selection = [application selection];
NSArray *identifiers = [selection valueForKey:@"id"];
``` 

This is because ``id`` is a special keyword in ``objc`` and throws an error.

**Note**: The above code evidently only works in the first database opened by 4D. If a database is reopened without restarting 4D, the app will crash. For this reason, the option ``id`` is disbled since ``2.0``.

If ``Mail selection source`` **or** ``Mail selection subject`` is passed, a JSON array of string is returned. You can use ``JSON Parse`` with ``Is collection`` to parse it as a collection. (default=``Mail selection source``)

If ``Mail selection source`` **and** ``Mail selection subject`` are passed (added), a JSON array of object is returned. You can use JSON PARSE ARRAY to parse it as an object array. This option is for versions that do not support objection notation or collections. This mode is somewhat inefficient compared to using collections.

```
C_COLLECTION($s;$i)
ARRAY OBJECT($m;0)

$json:=Mail Get selection (Mail selection subject | Mail selection source)
JSON PARSE ARRAY($json;$m)

$json:=Mail Get selection (Mail selection source)
$s:=JSON Parse($json;Is collection)
```
