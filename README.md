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

### Manual source-version and release lifecycle

**Bump version** is a manual patch/minor/major operation on an explicitly selected
branch. It checks out the immutable dispatch `github.sha`, requires clean source
metadata and an exact remote branch match, and commits only the three source
metadata files. Its mandatory executable pre-push guard checks the advertised old
SHA, literal new SHA/HEAD, exactly one direct parent, target branch and exactly one
update. Late advances, ancestor rewinds, deletions and same-result races fail closed.
The guard is checked both initially and immediately before pushing. The push is
non-force, with `push.followTags=false` and `--no-follow-tags`; it creates no tags
and does not trigger Build.

The existing coordinated version contract is authoritative: all three Xcode
configurations' `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION`, source
`Info.plist` and localized `English.lproj/InfoPlist.strings` must agree on strict
`X.Y.Z`. Supported Xcode references are preserved and resolved; absent optional
keys are not added. The old Bump header promised coordinated marketing/current
versions, and modernization commit `181de63` set both to `2.0.0`; bump `cc6f0c0`
advanced marketing/source plist to `2.0.1` but left current/localization stale.
This migration repairs only those stale source fields to the existing `2.0.1`
authority, without incrementing the release version. Prebuilt bundle metadata,
4D databases/counters, localization schema, API/dependencies and Windows projects
are excluded. Byte order marks, line endings, references and file modes are preserved.

**Build** has only `workflow_dispatch`, with zero inputs and no automatic push,
tag or PR trigger. Select the desired ref in Actions; every checkout uses that
run's immutable `github.sha`. It validates source metadata and checks remote tags
plus authenticated, paginated releases (including drafts) before native work.
Publication is serialized repository-wide across branches without canceling a
running Build. After all native/package/sign/notary/staple gates, it repeats the
complete availability checks immediately before creating a new `vX.Y.Z` tag at
the selected SHA. API/auth/network/malformed responses fail closed, including
404 and failures on later pages. Tag creation is create-only and remotely
verified; even a same-SHA race is rejected. Release creation is a separate POST
with the exact tag/SHA/name, `draft=false`, `prerelease=false` and the original
empty-notes policy. ZIP/DMG assets are uploaded separately to the returned new
release ID, without replacement.

The native job remains macOS-only: Apple Mail/ScriptingBridge, Cocoa/AppKit and
CoreGraphics frameworks, the committed 4D API, universal arm64/x86_64 output,
macOS 11.5 deployment target, resource/architecture checks, Developer ID signing,
ZIP/DMG packaging, notarytool submission and DMG stapling are unchanged. There
are no third-party prebuilt-library gates or Windows compilation to invent.
The committed Windows64 binary, documentation and QuickLook resources ship as-is;
only the stale MacOS binary directory and Default output are removed before
building. Existing notarytool `--wait` submissions and DMG stapling remain the
gates. Existing caveats: the job does not independently parse notarytool's
`Accepted` status, the ZIP is not stapled (only the DMG is), and the prebuilt
Windows payload is not rebuilt or architecture-verified. These are documented,
not bypassed or silently changed; native execution is outside this migration.
Signing requires the existing secret names `APPLE_DEVELOPER_ID_CERTIFICATE`,
`APPLE_DEVELOPER_ID_CERTIFICATE_PASSWORD`, `KEYCHAIN_PASSWORD`,
`NOTARYTOOL_APPLE_ID`, `NOTARYTOOL_TEAM_ID` and `NOTARYTOOL_PASSWORD`.

**Recovery:** no publication step deletes, patches, clobbers, rolls back or
retries remote state. If tag creation, release creation, verification or upload
fails, inspect the error and retained remote tag/release/assets manually. A
partial tag/release blocks another Build for that version; do not rerun expecting
overwrite or automatic repair. Maintainers must explicitly resolve partial
state under their release policy, or choose a new source version through Bump
and dispatch a new Build. A branch that moved during Bump must be freshly
selected for another dispatch.

Local lifecycle checks (no native/signing execution):
`python3 -B -m unittest discover -s .github/tests -v` and
`actionlint .github/workflows/*.yml`.

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
