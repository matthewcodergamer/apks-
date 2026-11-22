#!/usr/bin/env python3
"""Remove Turbo VPN ad surfaces and unlock VIP locations in the complete
4.3.2.2 arm64 APK.

The script disassembles the two DEX files that contain the ad and VIP code,
replaces the targeted methods with harmless stubs, reassembles the DEX files,
updates the APK, aligns it, and signs it with uber-apk-signer.

VPN/native code and resources are intentionally left untouched.
"""

from __future__ import annotations

import argparse
import hashlib
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

    for dex, specs in PATCHES.items():
        root = work / f"smali_{dex.removesuffix('.dex')}"
        for spec in specs:
            patch_method(root / spec["file"], spec)

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
        classes = ",".join(dict.fromkeys(spec["class"] for spec in specs))
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
