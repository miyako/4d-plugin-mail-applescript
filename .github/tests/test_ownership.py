"""Actual wrappers and unchanged SDK, with synthetic engine calls and no Mail."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("OWNERSHIP_SOURCE_ROOT", ROOT)).resolve()


@unittest.skipUnless(sys.platform == "darwin", "macOS framework shim")
class OwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.executed = 0
        cls.passed = 0
        cls.temp = tempfile.TemporaryDirectory(prefix="mail-ownership-")
        cls.binary = Path(cls.temp.name) / "ownership"
        api = SOURCE / "4D Plugin API"
        sdk_blobs = {
            "4DPluginAPI.c": "29788ed041effaf67269ccd93f971e8aee2ce5f8",
            "4DPluginAPI.h": "9054b45ffc7ff6f5b8d57529a3788a55d977b314",
            "4DPluginAPI.def": "996ecc4ab11ad165de9192eba2e7478db141c757",
            "EntryPoints.h": "730f2f77ff2713fb2fe4b7d6562baeedf5f664cb",
            "Flags.h": "10a83185333dac06a62dda61b9f9428243d1e2ee",
            "PrivateTypes.h": "77053dc0c0a3718d2d3b6f158371a6af78c6ae66",
            "PublicTypes.h": "2bb392e73e9c556c274fe0a75b3a6b83e310b77c",
        }
        for name, pinned in sdk_blobs.items():
            sdk = (api / name).read_bytes()
            blob = hashlib.sha1(f"blob {len(sdk)}\0".encode() + sdk).hexdigest()
            if blob != pinned:
                cls.temp.cleanup()
                raise AssertionError(f"Re-audit {name} before changing its pinned hash")
        # Deliberately exclude 4DPlugin.cpp, Mail.h and ScriptingBridge. The only
        # dispatcher is the synthetic host in ownership_host.mm.
        command = [
            "clang++", "-std=c++14", "-x", "objective-c++",
            "-include", "Carbon/Carbon.h", "-I", str(api),
            "-I", str(api / "Classes"), "-fsanitize=address,undefined",
            "-fno-sanitize=alignment", "-fno-omit-frame-pointer", "-g",
            "-Wno-deprecated-declarations", "-Wno-return-type-c-linkage",
            "-Wno-ignored-attributes", "-Wno-writable-strings",
            str(api / "4DPluginAPI.c"),
            *map(str, sorted((api / "Classes").glob("*.cpp"))),
            str(ROOT / ".github/tests/ownership_host.mm"),
            "-framework", "Cocoa", "-framework", "Carbon",
            "-o", str(cls.binary),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            cls.temp.cleanup()
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
        print(f"OWNERSHIP_CASES executed={cls.executed} passed={cls.passed} "
              f"failed={cls.executed - cls.passed}", flush=True)

    def run_case(self, case, text="", empty="allocated"):
        result = subprocess.run(
            [str(self.binary), case, text, empty],
            env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0",
                 "UBSAN_OPTIONS": "halt_on_error=1"},
            capture_output=True, text=True,
        )
        self.__class__.executed += 1
        if result.returncode == 0 and "strings=0 pictures=0 handles=0" in result.stdout:
            self.__class__.passed += 1
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("strings=0 pictures=0 handles=0", result.stdout)

    def test_path_single_disposal_and_retained_output(self):
        for text in ("ASCII", "\u65e5", "\U0001f600", ""):
            for empty in ("allocated", "null"):
                with self.subTest(text=text, empty=empty):
                    self.run_case("path", text, empty)

    def test_setbytes_temporary_release(self):
        self.run_case("bytes")

    def test_copy_byte_unit_boundary(self):
        for text in (".png", "\u65e5", "\U0001f600"):
            with self.subTest(text=text):
                self.run_case("copy", text, "null")

    def test_copy_initial_empty_owners(self):
        self.run_case("copy", "")

    def test_grayscale_initial_empty_owner(self):
        self.run_case("gray")

    def test_size_borrowed_input_and_empty_owner(self):
        self.run_case("size")

    def test_thumbnail_borrowed_input_and_owning_return(self):
        self.run_case("thumbnail")

    def test_array_transfers_copies_replacement_shrink_clear_rejection(self):
        for empty in ("allocated", "null"):
            with self.subTest(empty=empty):
                self.run_case("arrays", "", empty)

    def test_scalar_borrowed_copy_and_content_setter_returns(self):
        for text in ("ASCII", "\u65e5", "\U0001f600", ""):
            for empty in ("allocated", "null"):
                with self.subTest(text=text, empty=empty):
                    self.run_case("scalar", text, empty)

    def test_exact_utf8_utf16_and_nsstring_copy(self):
        for text in ("ASCII", "\u65e5", "\U0001f600", ""):
            for empty in ("allocated", "null"):
                with self.subTest(text=text, empty=empty):
                    self.run_case("encoding", text, empty)

    def test_command_handle_failure_preserves_argument_owners(self):
        for case in ("path", "copy", "gray", "size", "thumbnail"):
            with self.subTest(case=case):
                self.run_case(case + "-handle-failure", "")


if __name__ == "__main__":
    unittest.main()
