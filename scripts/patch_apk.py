#!/usr/bin/env python3
"""Remove Turbo VPN ad surfaces, unlock VIP locations, and restore the API
keys in the complete 4.3.2.2 arm64 APK.

The script disassembles the two DEX files that contain the ad, VIP, and API
code, replaces the targeted methods with harmless stubs, injects a small
in-app log viewer, reassembles the DEX files, updates the APK, aligns it, and
signs it with uber-apk-signer.

The native libovpnutil.so derives the API encryption keys from the APK signing
certificate and returns null after re-signing. The three NativeUtils methods
are therefore replaced with the hard-coded keys for this package.

VPN/native code and resources are otherwise left untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Each patch replaces the entire method body. Matching is by method name and
# parameter descriptor, so it also tolerates R8 renaming the return type.
PATCHES: dict[str, list[dict]] = {
    "classes.dex": [
        # --- ads ---------------------------------------------------------
        {
            "file": "co/allconnected/lib/ad/c.smali",
            "class": "Lco/allconnected/lib/ad/c;",
            "method": "q",
            "params": "Landroid/content/Context;Z",
            "registers": 3,
            "body": ["return-void"],
            "why": "platform ad-config loader",
        },
        {
            "file": "co/allconnected/lib/ad/BannerAdAgent.smali",
            "class": "Lco/allconnected/lib/ad/BannerAdAgent;",
            "method": "f",
            "params": "II",
            "registers": 3,
            "body": ["return-void"],
            "why": "banner-ad config parser",
        },
        {
            "file": "co/allconnected/lib/ad/AdShow.smali",
            "class": "Lco/allconnected/lib/ad/AdShow;",
            "method": "h",
            "params": "Z",
            "registers": 3,
            "body": ["const/4 v0, 0x0", "return-object v0"],
            "why": "full-screen ad selection",
        },
        {
            "file": "co/allconnected/lib/ad/AdShow.smali",
            "class": "Lco/allconnected/lib/ad/AdShow;",
            "method": "k",
            "params": "Z",
            "registers": 3,
            "body": [
                "new-instance v0, Ljava/util/ArrayList;",
                "invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V",
                "return-object v0",
            ],
            "why": "full-screen ad list",
        },
        # --- VIP / all locations ----------------------------------------
        {
            "file": "k2/A.smali",
            "class": "Lk2/A;",
            "method": "v",
            "params": "",
            "registers": 1,
            "body": ["const/4 v0, 0x1", "return v0"],
            "why": "treat user as VIP",
        },
        {
            "file": "k2/A.smali",
            "class": "Lk2/A;",
            "method": "q",
            "params": "Landroid/content/Context;",
            "registers": 2,
            "body": ["const/4 v0, 0x1", "return v0"],
            "why": "use the VIP server lists",
        },
        {
            "file": "k2/A.smali",
            "class": "Lk2/A;",
            "method": "i",
            "params": "",
            "registers": 1,
            "body": ["const/16 v0, 0x1e", "return v0"],
            "why": "report maximum VIP level",
        },
        {
            "file": "k2/A.smali",
            "class": "Lk2/A;",
            "method": "t",
            "params": "",
            "registers": 1,
            "body": ["const/4 v0, 0x0", "return v0"],
            "why": "disable trial-only restrictions",
        },
        {
            "file": "k2/A.smali",
            "class": "Lk2/A;",
            "method": "e",
            "params": "",
            "registers": 0,
            "body": ["return-void"],
            "why": "prevent VIP-list expiry cleanup",
        },
        {
            "file": "co/allconnected/lib/model/VpnServer.smali",
            "class": "Lco/allconnected/lib/model/VpnServer;",
            "method": "compareTo",
            "params": "Lco/allconnected/lib/model/VpnServer;",
            "registers": 7,
            "body": [
                "iget-boolean v0, p0, Lco/allconnected/lib/model/VpnServer;->isVipServer:Z",
                "iget-boolean v1, p1, Lco/allconnected/lib/model/VpnServer;->isVipServer:Z",
                "const/4 v2, 0x1",
                "const/4 v3, -0x1",
                "if-ne v0, v1, :cond_2c",
                "invoke-virtual {p0}, Lco/allconnected/lib/model/VpnServer;->getScore()I",
                "move-result v0",
                "invoke-virtual {p1}, Lco/allconnected/lib/model/VpnServer;->getScore()I",
                "move-result v1",
                "invoke-static {p0}, Lk2/J;->J(Lco/allconnected/lib/model/VpnServer;)Z",
                "move-result v4",
                "invoke-static {p1}, Lk2/J;->J(Lco/allconnected/lib/model/VpnServer;)Z",
                "move-result p1",
                "if-eqz v4, :cond_1c",
                "if-nez p1, :cond_20",
                ":cond_1c",
                "if-nez v4, :cond_28",
                "if-nez p1, :cond_28",
                ":cond_20",
                "if-le v0, v1, :cond_23",
                "return v3",
                ":cond_23",
                "if-ne v0, v1, :cond_27",
                "const/4 p1, 0x0",
                "return p1",
                ":cond_27",
                "return v2",
                ":cond_28",
                "if-eqz v4, :cond_2b",
                "return v2",
                ":cond_2b",
                "return v3",
                ":cond_2c",
                "if-eqz v0, :cond_2f",
                "return v2",
                ":cond_2f",
                "return v3",
            ],
            "why": "sort free servers before VIP servers so the default connection uses a free server",
        },
        # --- diagnostics -------------------------------------------------
        {
            "file": "g2/g.smali",
            "class": "Lg2/g;",
            "method": "k",
            "params": "I",
            "registers": 2,
            "body": ["const/4 v0, 0x1", "return v0"],
            "why": "enable app debug logging for the in-app log viewer",
        },
        {
            "file": "co/allconnected/lib/model/ReqServersListBean.smali",
            "class": "Lco/allconnected/lib/model/ReqServersListBean;",
            "method": "setIsVip",
            "params": "Z",
            "registers": 3,
            "body": [
                "const/4 v0, 0x0",
                "iput-boolean v0, p0, Lco/allconnected/lib/model/ReqServersListBean;->isVip:Z",
                "return-object p0",
            ],
            "why": "keep the server-list request on the free-user path",
        },
        # --- API keys ----------------------------------------------------
        # libovpnutil.so only returns these keys when the APK carries the
        # original signing certificate. Re-signing makes getCipherKey() return
        # null, which breaks activation and the server list. These are the
        # hard-coded turbovpn keys selected by the native code.
        {
            "file": "co/allconnected/lib/openvpn/NativeUtils.smali",
            "class": "Lco/allconnected/lib/openvpn/NativeUtils;",
            "method": "getApiCipherKey",
            "params": "Landroid/content/Context;",
            "registers": 2,
            "body": [
                'const-string v0, "w:SzR%Qd8.=ouuwpVz;JqNA9/]867@qj"',
                "return-object v0",
            ],
            "why": "restore the API body-encryption key",
        },
        {
            "file": "co/allconnected/lib/openvpn/NativeUtils.smali",
            "class": "Lco/allconnected/lib/openvpn/NativeUtils;",
            "method": "getApiHeaderKey",
            "params": "Landroid/content/Context;",
            "registers": 2,
            "body": [
                'const-string v0, "7Yg3gQbUjYPF3/RHVmbO3tO3H/g="',
                "return-object v0",
            ],
            "why": "restore the API auth-header key",
        },
        {
            "file": "co/allconnected/lib/openvpn/NativeUtils.smali",
            "class": "Lco/allconnected/lib/openvpn/NativeUtils;",
            "method": "getLocalCipherKey",
            "params": "Landroid/content/Context;",
            "registers": 2,
            "body": [
                'const-string v0, "43a41a300d06092a864886f70d01010505003"',
                "return-object v0",
            ],
            "why": "restore the local cache key",
        },
    ],
    "classes5.dex": [
        # --- ads ---------------------------------------------------------
        {
            "file": "D5/H.smali",
            "class": "LD5/H;",
            "method": "D",
            "params": "",
            "registers": 1,
            "body": ["return-void"],
            "why": "AppLuck hover-ad refresh",
        },
        {
            "file": "free/vpn/unblock/proxy/turbovpn/activity/VpnMainActivity.smali",
            "class": "Lfree/vpn/unblock/proxy/turbovpn/activity/VpnMainActivity;",
            "method": "r4",
            "params": "Ljava/lang/String;",
            "registers": 2,
            "body": ["return-void"],
            "why": "HomeAdActivity deep-link launcher",
        },
    ],
}

# Code inserted at the start of an existing method instead of replacing it.
INJECTIONS: dict[str, list[dict]] = {
    "classes.dex": [
        {
            "file": "co/allconnected/lib/VpnAgent.smali",
            "class": "Lco/allconnected/lib/VpnAgent;",
            "method": "E0",
            "params": "Lco/allconnected/lib/model/VpnServer;Z",
            "code": [
                "invoke-static {p1}, Lfree/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker;->a(Lco/allconnected/lib/model/VpnServer;)Lco/allconnected/lib/model/VpnServer;",
                "move-result-object p1",
            ],
            "why": "replace a VIP server with a free server right before connecting",
        }
    ],
    "classes5.dex": [
        {
            "file": "free/vpn/unblock/proxy/turbovpn/activity/StartupActivity.smali",
            "class": "Lfree/vpn/unblock/proxy/turbovpn/activity/StartupActivity;",
            "method": "onCreate",
            "params": "Landroid/os/Bundle;",
            "code": [
                "invoke-static {p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a(Landroid/app/Activity;)V"
            ],
            "why": "show the log overlay on the first activity, before the VPN permission dialog",
        },
        {
            "file": "free/vpn/unblock/proxy/turbovpn/activity/VpnMainActivity.smali",
            "class": "Lfree/vpn/unblock/proxy/turbovpn/activity/VpnMainActivity;",
            "method": "onResume",
            "params": "",
            "code": [
                "invoke-static {p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a(Landroid/app/Activity;)V"
            ],
            "why": "show the log overlay on the main activity",
        },
    ],
}

# Extra smali classes copied into a DEX before assembly.
EXTRA_SMALI: dict[str, list[tuple[str, str]]] = {
    "classes.dex": [
        (
            "free/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker.smali",
            "FreeServerPicker.smali",
        ),
    ],
    "classes5.dex": [
        (
            "free/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper.smali",
            "DebugLogHelper.smali",
        ),
        (
            "free/vpn/unblock/proxy/turbovpn/debug/DebugLogTask.smali",
            "DebugLogTask.smali",
        ),
    ],
}

PATCH_DIR = Path(__file__).resolve().parent.parent / "patches"

REQUIRED_LIBS = [
    "lib/arm64-v8a/libovpnutil.so",
    "lib/arm64-v8a/libxray.so",
]


def log(message: str) -> None:
    print(message, flush=True)


def run(cmd: list, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    printable = " ".join(str(part) for part in cmd)
    log(f"+ {printable}")
    return subprocess.run([str(part) for part in cmd], cwd=cwd, check=check)


def method_range(lines: list[str], name: str, params: str) -> tuple[int, int]:
    matches = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith(".method "):
            continue
        signature = stripped.split()[-1]
        if "(" not in signature:
            continue
        found_name, rest = signature.split("(", 1)
        found_params = rest.split(")", 1)[0]
        if found_name == name and found_params == params:
            matches.append(index)

    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one method {name}({params}), found {len(matches)}"
        )

    start = matches[0]
    for end in range(start + 1, len(lines)):
        if lines[end].strip() == ".end method":
            return start, end
    raise RuntimeError(f"no .end method for {name}({params})")


def patch_method(path: Path, spec: dict) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = method_range(lines, spec["method"], spec["params"])
    header = lines[start]
    block = [header, f"    .registers {spec['registers']}"]
    block.extend(f"    {instruction}" for instruction in spec["body"])
    block.append(".end method")
    lines[start : end + 1] = block
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"  patched {path}: {header.strip()}  [{spec['why']}]")


def assert_stub(path: Path, spec: dict) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = method_range(lines, spec["method"], spec["params"])
    actual = [line.strip() for line in lines[start + 1 : end] if line.strip()]
    expected = [f".registers {spec['registers']}", *spec["body"]]
    if actual != expected:
        raise RuntimeError(
            f"stub verification failed for {path} {spec['method']}({spec['params']}):\n"
            f"expected {expected}\nactual   {actual}"
        )
    log(f"  verified {path}: {spec['method']}({spec['params']})")


def inject_code(path: Path, spec: dict) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = method_range(lines, spec["method"], spec["params"])
    insert_at = None
    for index in range(start + 1, end):
        stripped = lines[index].strip()
        if stripped.startswith(".registers") or stripped.startswith(".locals"):
            insert_at = index + 1
            break
    if insert_at is None:
        raise RuntimeError(
            f"no .registers/.locals in {path} {spec['method']}({spec['params']})"
        )
    block = [f"    {instruction}" for instruction in spec["code"]]
    lines[insert_at:insert_at] = block
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"  injected {path}: {spec['method']}({spec['params']})  [{spec['why']}]")


def _parameter_register_count(descriptor: str, is_static: bool) -> int:
    """Count the registers occupied by a method's parameters.

    Wide parameters (J/D) use two registers, objects and arrays use one, and
    instance methods reserve p0 for ``this``.
    """
    inside = descriptor[1 : descriptor.index(")")]
    count = 0
    index = 0
    while index < len(inside):
        char = inside[index]
        if char == "[":
            while index < len(inside) and inside[index] == "[":
                index += 1
            if index < len(inside) and inside[index] == "L":
                index = inside.index(";", index)
            index += 1
            count += 1
        elif char == "L":
            index = inside.index(";", index) + 1
            count += 1
        elif char in "JD":
            count += 2
            index += 1
        else:
            count += 1
            index += 1
    return count + (0 if is_static else 1)


def validate_parameter_registers(path: Path) -> None:
    """Reject pN/vN references outside a method's register file.

    smali accepts p1 in a one-parameter method with .registers 4, but ART then
    rejects the class with a VerifyError.  This catches that class of bug before
    the APK is assembled and again after the signed DEX is disassembled.
    """
    method: str | None = None
    is_static = False
    parameter_registers = 0
    total_registers: int | None = None

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        stripped = line.strip()
        if stripped.startswith(".method "):
            method = stripped
            is_static = " static " in f" {stripped} "
            descriptor = re.search(r"\([^)]*\)", stripped)
            parameter_registers = (
                _parameter_register_count(descriptor.group(0), is_static)
                if descriptor
                else 0
            )
            total_registers = None
            continue

        if method is None:
            continue

        if stripped.startswith(".registers "):
            total_registers = int(stripped.split()[1])
            if total_registers < parameter_registers:
                raise RuntimeError(
                    f"{path}:{line_number}: {method} has .registers "
                    f"{total_registers} but needs {parameter_registers} for "
                    "its parameters"
                )
        elif stripped.startswith(".locals "):
            total_registers = int(stripped.split()[1]) + parameter_registers
        elif stripped.startswith(".end method"):
            method = None
            total_registers = None
        elif total_registers is not None:
            code = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped)
            code = code.split("#", 1)[0]
            for match in re.finditer(r"(?<![\w/$>])p(\d+)(?![\w/$])", code):
                if int(match.group(1)) >= parameter_registers:
                    raise RuntimeError(
                        f"{path}:{line_number}: {method} has only "
                        f"{parameter_registers} parameter register(s) but "
                        f"uses p{match.group(1)}"
                    )
            for match in re.finditer(r"(?<![\w/$>])v(\d+)(?![\w/$])", code):
                if int(match.group(1)) >= total_registers:
                    raise RuntimeError(
                        f"{path}:{line_number}: {method} has .registers "
                        f"{total_registers} but uses v{match.group(1)}"
                    )


def assert_injected(path: Path, spec: dict) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = method_range(lines, spec["method"], spec["params"])
    actual = [line.strip() for line in lines[start + 1 : end]]
    for instruction in spec["code"]:
        if instruction not in actual:
            raise RuntimeError(
                f"injection verification failed for {path} "
                f"{spec['method']}({spec['params']}): missing {instruction}"
            )
    log(f"  verified injection {path}: {spec['method']}({spec['params']})")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", required=True, help="complete input APK")
    parser.add_argument("--out", required=True, help="output signed APK")
    parser.add_argument(
        "--signer",
        default="uber-apk-signer.jar",
        help="path to uber-apk-signer.jar",
    )
    parser.add_argument(
        "--work",
        default="build/patchwork",
        help="working directory for disassembly and signing",
    )
    parser.add_argument(
        "--skip-disassemble",
        action="store_true",
        help="reuse existing smali directories in --work",
    )
    parser.add_argument(
        "--keep-work",
        action="store_true",
        help="keep the working directory after a successful build",
    )
    args = parser.parse_args()

    apk = Path(args.apk).resolve()
    out = Path(args.out).resolve()
    signer = Path(args.signer).resolve()
    work = Path(args.work).resolve()

    for required in (apk, signer):
        if not required.is_file():
            raise SystemExit(f"missing required file: {required}")

    if work.exists() and not args.skip_disassemble:
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    log(f"input : {apk}")
    log(f"output: {out}")
    log(f"work  : {work}")

    with zipfile.ZipFile(apk) as archive:
        names = set(archive.namelist())
        for dex in PATCHES:
            if dex not in names:
                raise SystemExit(f"{apk} does not contain {dex}")
            archive.extract(dex, work)

    for dex in PATCHES:
        smali_dir = work / f"smali_{dex.removesuffix('.dex')}"
        if smali_dir.exists() and args.skip_disassemble:
            log(f"reusing {smali_dir}")
            continue
        if smali_dir.exists():
            shutil.rmtree(smali_dir)
        log(f"disassembling {dex} -> {smali_dir}")
        run(["baksmali", "d", work / dex, "-o", smali_dir])

    for dex in list(INJECTIONS) + list(EXTRA_SMALI):
        if dex not in PATCHES:
            raise SystemExit(f"{dex} has injections/extra smali but no patch entry")

    for dex, specs in PATCHES.items():
        root = work / f"smali_{dex.removesuffix('.dex')}"
        for spec in specs:
            patch_method(root / spec["file"], spec)

    for dex, entries in EXTRA_SMALI.items():
        root = work / f"smali_{dex.removesuffix('.dex')}"
        for relative, source in entries:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PATCH_DIR / source, destination)
            validate_parameter_registers(destination)
            log(f"  added {destination}")

    for dex, specs in INJECTIONS.items():
        root = work / f"smali_{dex.removesuffix('.dex')}"
        for spec in specs:
            inject_code(root / spec["file"], spec)

    build = work / "build"
    if build.exists():
        shutil.rmtree(build)
    build.mkdir()
    for dex in PATCHES:
        root = work / f"smali_{dex.removesuffix('.dex')}"
        log(f"assembling {root} -> {build / dex}")
        run(["smali", "a", root, "-a", "29", "-o", build / dex])

    unsigned = work / "unsigned.apk"
    shutil.copy2(apk, unsigned)

    # Remove the original v1 signature. The old v2/v3 block is invalidated by
    # the zip update and replaced when the APK is re-signed.
    run(
        [
            "zip",
            "-q",
            "-d",
            unsigned,
            "META-INF/*.SF",
            "META-INF/*.RSA",
            "META-INF/*.DSA",
            "META-INF/*.EC",
            "META-INF/MANIFEST.MF",
        ],
        check=False,
    )

    # Replace only the two patched DEX entries. All other entries, including
    # resources.arsc and the native libraries, are copied unchanged.
    run(["zip", "-q", "-X", unsigned, *PATCHES.keys()], cwd=build)

    aligned = work / "aligned.apk"
    if aligned.exists():
        aligned.unlink()
    run(["zipalign", "-f", "-p", "4", unsigned, aligned])
    run(["zipalign", "-c", "-p", "4", aligned])

    signed_dir = work / "signed"
    if signed_dir.exists():
        shutil.rmtree(signed_dir)
    run(
        [
            "java",
            "-jar",
            signer,
            "--apks",
            aligned,
            "--out",
            signed_dir,
            "--allowResign",
            "--skipZipAlign",
        ]
    )

    signed_apks = sorted(signed_dir.glob("*.apk"))
    if len(signed_apks) != 1:
        raise SystemExit(f"expected one signed APK, found: {signed_apks}")
    signed = signed_apks[0]

    log("verifying signature and alignment")
    run(
        [
            "java",
            "-jar",
            signer,
            "--apks",
            signed,
            "--onlyVerify",
            "--skipZipAlign",
            "--verbose",
        ]
    )
    run(["zipalign", "-c", "-p", "4", signed])

    log("verifying patched DEX methods in the signed APK")
    verify_root = work / "verify"
    if verify_root.exists():
        shutil.rmtree(verify_root)
    for dex, specs in PATCHES.items():
        verify_dir = verify_root / dex.removesuffix(".dex")
        class_names = [spec["class"] for spec in specs]
        class_names.extend(spec["class"] for spec in INJECTIONS.get(dex, []))
        for relative, _ in EXTRA_SMALI.get(dex, []):
            class_names.append("L" + relative.removesuffix(".smali") + ";")
        classes = ",".join(dict.fromkeys(class_names))
        run(
            [
                "baksmali",
                "d",
                f"{signed}/{dex}",
                "--classes",
                classes,
                "-o",
                verify_dir,
            ]
        )
        for spec in specs:
            assert_stub(verify_dir / spec["file"], spec)
        for spec in INJECTIONS.get(dex, []):
            assert_injected(verify_dir / spec["file"], spec)
        for relative, _ in EXTRA_SMALI.get(dex, []):
            if not (verify_dir / relative).is_file():
                raise RuntimeError(f"extra class missing from signed APK: {relative}")
            validate_parameter_registers(verify_dir / relative)
            log(f"  verified extra class {relative}")

    with zipfile.ZipFile(signed) as archive:
        bad_entry = archive.testzip()
        if bad_entry is not None:
            raise SystemExit(f"corrupt zip entry: {bad_entry}")
        archive_names = set(archive.namelist())
        for lib in REQUIRED_LIBS:
            if lib not in archive_names:
                raise SystemExit(f"signed APK is missing {lib}")

    shutil.copy2(signed, out)
    log("")
    log(f"built  : {out}")
    log(f"size   : {out.stat().st_size} bytes")
    log(f"sha256 : {sha256(out)}")

    if not args.keep_work:
        shutil.rmtree(work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
