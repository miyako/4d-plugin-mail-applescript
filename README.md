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

## Native string ownership audit

The bounded audit baseline is `d637ce67cacaab7add0c73de8941942f559dd771`.
The first-party `Classes/C_PICTURE.cpp` helper now clears its shallowly assigned
path argument once, retains the loaded picture before clearing the output
argument, releases a temporary picture after retaining it, and avoids allocating
empty owners that a shallow setter would overwrite. Conversion output lengths
are bytes and are divided by `sizeof(PA_Unichar)` before constructing UTF-16.
Borrowed picture inputs are still detached before argument cleanup; owning
copy/grayscale/thumbnail returns remain the caller's responsibility.

### Inventory and reachability

All paths below are tracked native sources, not a manifest-based exclusion:

| Surface | Ownership trace / build reachability |
|---|---|
| `4DPlugin.cpp`, `4DPlugin.h` | `FourDPackex` -> `PluginMain` -> `CommandDispatcher` -> command 1, `Mail_Get_selection`. The sole command is `Mail Get selection(&L):T` in both source and bundled `manifest.json`; no text arrays are exported. `C_LONGINT` copies the mode. Foundation JSON serialization creates an owned `NSString`, `C_TEXT` copies its content, then the string is released; the return uses the SDK content setter, not scalar descriptor assignment. Mail/ScriptingBridge is inspected statically only. |
| `Mail.h`, `4D Plugin_Prefix.pch` | Generated ScriptingBridge declarations and Carbon prefix header. No first-party PA string allocator/consumer implementation in the generated declarations; no Mail code is compiled into the regression executable. |
| `4D Plugin API/4DPluginAPI.c`, `.h`, `.def` | Complete bundled engine boundary and exported `FourDPackex`; includes every wrapper header. No SDK production edits. |
| `4D Plugin API/EntryPoints.h`, `Flags.h`, `PrivateTypes.h`, `PublicTypes.h` | Actual selectors, platform flags, packed engine block and variable/string/handle layouts used by the compiled SDK and shim. |
| `4D Plugin API/Classes/C_TEXT.{cpp,h}`, `ARRAY_TEXT.{cpp,h}`, `C_TYPES.h` | Independent C++ UTF-16 buffers; scalar content setters and copied borrowed input; array copies include element zero, and each output creates its own transferred descriptor. No post-transfer disposal is present. Foundation/CF conversion and string-copy helpers are also inspected. |
| `4D Plugin API/Classes/C_PICTURE.{cpp,h}` | `CPicture` and forwarding `C_PICTURE`: path, bytes, format copy, grayscale, dimensions, thumbnail, parameter/result, representation enumeration and native image adapters. Compiled but dormant from the current Mail dispatcher. Defects fixed here, including related empty-owner/refcount leaks. |
| `4D Plugin API/Classes/C_POINTER.{cpp,h}` | Pointer metadata copying and pointer-value helper; ambiguous engine metadata ownership deferred below. Dormant from the Mail command. |
| `4D Plugin API/Classes/C_BLOB.{cpp,h}` | `CBytes` and `C_BLOB` own vectors/handles; hex/base64 helpers copy through `C_TEXT`, not transferred PA string descriptors. Non-string allocation failures are outside this correction. |
| `4D Plugin API/Classes/C_DATE.{cpp,h}`, `C_INTEGER.{cpp,h}`, `C_LONGINT.{cpp,h}`, `C_REAL.{cpp,h}`, `C_TIME.{cpp,h}` | Scalar value wrappers; parameter/return copying and scalar setters, no PA string allocation/transfer. |
| `4D Plugin API/Classes/ARRAY_BOOLEAN.{cpp,h}`, `ARRAY_DATE.{cpp,h}`, `ARRAY_INTEGER.{cpp,h}`, `ARRAY_LONGINT.{cpp,h}`, `ARRAY_REAL.{cpp,h}`, `ARRAY_TIME.{cpp,h}` | Typed numeric/date/time vector copies and array allocation/resize; no PA string element ownership. |
| `Mail (AppleScript).xcodeproj/project.pbxproj`, both `.vcxproj` and `.filters` | Xcode compiles the dispatcher, SDK and all 16 wrapper implementations, including dormant helpers. Both VS projects list the same sources; Windows compilation is not claimed (the dispatcher is Mac-only). Headers are included via API/Classes search paths. Existing projects/configurations/filters are unchanged. |
| `manifest.json`, `constants.xlf`, bundled manifest/constants, `Info.plist`, localization/resources | Static command/resource metadata; no native implementation. Existing source metadata and committed bundle/database/binary bytes and modes remain unchanged. |

### Exact SDK contracts and provenance

Guidance: `miyako/skills`, `4d-skills/skills/4dplugin/SKILL.md` at
`e6b492fcb81e5e1a7f7db723594b420e63bf6eb9`.
The local SDK files were introduced at repository commit
`181de6302c19786d5d4cc0cf95609602043b4ba8`; the C file's `v14` and header's
`v13` comments are not independently verified upstream release identities.
At the audit baseline the Git blob identities are:

| File in `4D Plugin API/` | Git blob |
|---|---|
| `4DPluginAPI.c` | `29788ed041effaf67269ccd93f971e8aee2ce5f8` |
| `4DPluginAPI.h` | `9054b45ffc7ff6f5b8d57529a3788a55d977b314` |
| `4DPluginAPI.def` | `996ecc4ab11ad165de9192eba2e7478db141c757` |
| `EntryPoints.h` | `730f2f77ff2713fb2fe4b7d6562baeedf5f664cb` |
| `Flags.h` | `10a83185333dac06a62dda61b9f9428243d1e2ee` |
| `PrivateTypes.h` | `77053dc0c0a3718d2d3b6f158371a6af78c6ae66` |
| `PublicTypes.h` | `2bb392e73e9c556c274fe0a75b3a6b83e310b77c` |

`PA_CreateUnistring`/`PA_SetUnistring`/`PA_DisposeUnistring` forward to engine
selectors (C lines 244-270). `C_TEXT` uses the content setter, as does
`PA_ReturnString`; neither is `PA_SetStringVariable`'s shallow assignment
(3826-3831). `PA_CreateVariable(eVK_Unistring/Picture)` allocates an empty owner;
use Undefined before assigning an existing owner. `PA_GetPictureVariable`
explicitly borrows (3730-3736); `PA_DuplicatePicture(p, 1)` retains (447-454).
Shallow picture arguments therefore require either detachment for a borrow or
an explicit ownership handoff; retaining and then clearing the original owner
balances loaded output.

`PA_GetStringInArray` borrows (4266-4286). `PA_SetStringInArray` (4444-4459)
accepts exactly Unicode-array type, non-null data, `0 <= i <= fNbElements` and
non-null input descriptor. It disposes the old element then shallow-assigns.
Rejections retain caller ownership, including wrong type, negative/high index
and null data. Index zero is valid. `ARRAY_TEXT` makes independent copies before
mutating the destination, and does not dispose transferred strings.

`PA_ExecuteCommandByID` returns a raw `fType == 0` sentinel when its handle
allocation fails (5257-5294); normalization misclassifies it as string.
The picture procedures ignore that return rather than inspecting/clearing it.
Their output arguments remain independently owned even when no dispatch occurs.
`PA_ExecuteMethodByID` uses Undefined on handle failure, a different contract.
The SDK has no JSON property/element APIs; Foundation serialization does not
introduce PA JSON ownership. SDK-only application-path/representation strings
and `C_POINTER::getVariable` metadata have insufficient engine-ownership evidence;
no speculative cleanup has been added.

### Safe regression and limits

Run `python3 -B -m unittest discover -s .github/tests -p test_ownership.py -v`
on macOS. This compiles **all actual wrapper implementations and the complete
unchanged SDK** with ASan/UBSan, using a synthetic `gCall4D` engine boundary.
Alignment instrumentation is excluded for the bundled packed ABI; LSan is
unavailable on this macOS setup, so string allocations, picture references and
handles are explicitly counted and must all reach zero.
`4DPlugin.cpp`, `Mail.h` and ScriptingBridge are deliberately excluded before
compilation; the replacement `PluginMain` is inert. All command selectors are
handled locally using synthetic text/pictures. No AppleScript, AppleEvents,
Mail/app activation, user files, permissions dialogs, signing, packaging or
publication is executed. New **Native ownership** CI is scoped unsigned testing
on `macos-latest`; existing manual Build/Bump workflows are untouched.

The host derives array/scalar ownership, command argument forwarding and retain
semantics from this SDK, not a replacement SDK implementation. It models content
setters as engine copies, conversion results as bytes, UTF-16 capacity including
the terminator, allocated and null empty strings, and poisoned failed
picture-representation outputs. The immutable harness reference is
`miyako/4d-plugin-jpegoptim` at
`e49adcd32bd5500cf3de680faa3649b32463ff5e`,
`.github/tests/{ownership_host.mm,test_ownership.py}`; the target SDK and source
paths were independently checked.

The same harness can target a `git archive` extraction of the immutable baseline
using `OWNERSHIP_SOURCE_ROOT`; it does not rewrite production sources. Coverage
includes exact ASCII/BMP/supplementary/empty UTF-8 bytes and UTF-16 units,
termination/capacity, scalar copied-input/content-return controls, independent
array element allocations (including identical values), replacement, shrink,
clear, Undefined destination creation, rejected transfers, retained output and
owning-handoff survival, repeated byte replacement, poisoned failed outputs,
command-handle failures and raw-sentinel controls.

With the same final harness and unchanged SDK, the archived baseline executes
39 scenarios: 18 pass and 21 fail. Failures are the eight path fixture/empty
variants, five command-handle-failure variants, three format-copy variants,
empty-format initial owners, grayscale, repeated bytes, dimensions and thumbnail.
The `.png` format-copy case reports an ASan heap-buffer-overflow; the path
cases expose duplicate disposal or invalidated picture references, and the
other failures expose unbalanced string/picture ownership. The corrected actual
sources execute all 39 scenarios successfully (11 unittest methods), with zero
live strings/picture references/handles after each scenario. Scalar, encoding
and array controls pass on both revisions. This is a source differential, not
a reproduction of the live Mail reopening crash.

Initial string allocation failure remains **deferred**, not certified safe:
`PA_CreateUnistring` exposes an unchecked engine descriptor and does not establish
an error channel in this bundled implementation. The void wrapper boundaries
cannot safely fabricate an empty success or replace caller bytes on failure.
Array allocation failure and SDK resize-OOM count corruption are also not fixed:
`PA_ResizeArray` updates the element count even after failed handle resize
(4087-4131). Passing normal/rejected-array cases is not evidence of OOM safety.
Non-string/CBytes allocation failures, engine-owned representation/metadata
contracts and native image APIs remain outside verified coverage.
These sanitizer/shim results do not certify a real 4D host, Windows, live Mail,
or the previously documented database-reopening crash.

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
