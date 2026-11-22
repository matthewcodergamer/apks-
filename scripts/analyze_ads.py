#!/usr/bin/env python3
"""Build a static ad-integration report for the Turbo VPN APK."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APK = ROOT / "Turbo VPN.apk"
DEC = ROOT / "decompiled"
APKTOOL = DEC / "apktool"
JADX = DEC / "jadx" / "sources"
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

ASSETS = DEC / "assets" / "assets"
if not ASSETS.is_dir():
    ASSETS = DEC / "assets"

AD_COMPONENT_RE = re.compile(
    r"(?i)(admob|unity|ironsource|levelplay|vungle|inmobi|yandex|bigo|"
    r"tradplus|monetrix|applovin|pangle|bytedance|mintegral|chartboost|"
    r"adcolony|facebook\.ads|amazon\.device\.ads|huawei\.hms\.ads|"
    r"(^|\.)ad\.|adactivity|adsactivity|adservice|adprovider|admanager|"
    r"fullscreenwebview)"
)
AD_META_RE = re.compile(
    r"(?i)(admob|unity|vungle|yandex|ads|ad_id|adid|advertising|"
    r"applovin|ironsource|inmobi|bigo|tradplus|monetrix|huawei\.hms.*ads)"
)
CODE_RE = re.compile(
    r"(?i)(showAd|loadAd|loadFull|showFull|openAd|interstitial|rewarded|"
    r"nativeAd|bannerAd|splashAd|placement|adConfig|adUnit|adIds|"
    r"frequency|cooldown|ad_load_error|AdManager|AdHelper|AdController|"
    r"AdListener|AdInfo|AdFormat)"
)
URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+")
AD_DOMAINS = (
    "aiadsapp.net",
    "tradplus",
    "vungle",
    "inmobi",
    "unity3d",
    "doubleclick",
    "googleads",
    "admob",
    "bigo",
    "yandex",
    "monetrix",
    "ironsource",
    "applovin",
    "pangle",
    "bytedance",
    "mintegral",
    "chartboost",
    "adcolony",
)

SDK_PREFIXES = [
    ("Google Mobile Ads / AdMob", ["com/google/android/gms/ads"]),
    ("Unity LevelPlay / ironSource", ["com/unity3d", "com/ironsource"]),
    ("Vungle / Liftoff", ["com/vungle"]),
    ("InMobi", ["com/inmobi"]),
    ("Yandex Mobile Ads", ["com/yandex/mobile/ads"]),
    ("Bigo Ads", ["sg/bigo/ads"]),
    ("TradPlus", ["com/tradplus/ads"]),
    ("Monetrix", ["com/monetrix/adsdk"]),
    ("Huawei Ads", ["com/huawei/hms/ads"]),
    ("Amazon Ads", ["com/amazon/device/ads"]),
    ("AppLovin MAX", ["com/applovin"]),
    ("Meta Audience Network", ["com/facebook/ads"]),
    ("Pangle / ByteDance", ["com/bytedance/sdk/openadsdk"]),
    ("Mintegral", ["com/mbridge/msdk"]),
    ("Chartboost", ["com/chartboost/sdk"]),
    ("AdColony", ["com/adcolony/sdk"]),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def md_table(headers, rows):
    def cell(value):
        text = str(value).replace("|", "\\|").replace("\n", " ")
        return text if len(text) <= 160 else text[:157] + "..."

    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        out.append("| " + " | ".join(cell(v) for v in row) + " |")
    return "\n".join(out)


def count_java(prefix: str) -> int:
    path = JADX / prefix
    if not path.is_dir():
        return 0
    return sum(1 for _ in path.rglob("*.java"))


def parse_manifest():
    text = read_text(APKTOOL / "AndroidManifest.xml")
    lines = text.splitlines()
    name_re = re.compile(r'android:name\([^)]*\)="([^"]+)"')
    components = []
    meta = []

    for index, line in enumerate(lines):
        component_match = re.match(r"\s*E: (activity|service|receiver|provider)\b", line)
        if component_match:
            for follow in lines[index + 1 : index + 10]:
                match = name_re.search(follow)
                if match:
                    name = match.group(1)
                    if AD_COMPONENT_RE.search(name):
                        components.append((component_match.group(1), name))
                    break

        if "E: meta-data" in line:
            name = None
            value_line = ""
            for follow in lines[index + 1 : index + 7]:
                if name is None:
                    match = name_re.search(follow)
                    if match:
                        name = match.group(1)
                if "android:value" in follow and not value_line:
                    value_line = follow.strip()
                if follow.strip().startswith("E: ") and follow is not lines[index + 1]:
                    break
            if name and (AD_META_RE.search(name) or AD_META_RE.search(value_line)):
                meta.append((name, value_line))

    deduped = []
    seen = set()
    for item in components:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped, meta


def collect_configs():
    id_rows = []
    id_files = sorted(ASSETS.glob("*ad_id_config*.json"))
    for path in id_files:
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        for key, value in (data.get("id_config") or {}).items():
            if not isinstance(value, dict):
                continue
            id_rows.append(
                {
                    "file": path.name,
                    "key": key,
                    "type": value.get("type", ""),
                    "id": value.get("id", ""),
                    "desc": value.get("desc", ""),
                }
            )

    placement_rows = []
    placement_files = sorted(ASSETS.glob("*ad_config*.json"))
    for path in placement_files:
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        for placement, value in (data.get("placements") or {}).items():
            if not isinstance(value, dict):
                continue
            for chain_index, chain in enumerate(value.get("ads") or [], start=1):
                if isinstance(chain, list):
                    placement_rows.append(
                        {
                            "file": path.name,
                            "placement": placement,
                            "chain": chain_index,
                            "keys": " > ".join(str(item) for item in chain),
                        }
                    )

    defined = {row["key"] for row in id_rows}
    referenced = set()
    for row in placement_rows:
        referenced.update(part.strip() for part in row["keys"].split(">") if part.strip())
    missing = sorted(referenced - defined)
    unused = sorted(defined - referenced)

    online = load_json(ASSETS / "config" / "online_config_defaults.json") or {}
    return id_rows, placement_rows, missing, unused, online


def collect_asset_urls():
    urls = set()
    for relative in ("iads/index.js", "iads/sdk_controller.min.gz.js", "iads/mobileController.html"):
        text = read_text(ASSETS / relative)
        for url in URL_RE.findall(text):
            url = url.rstrip(".,;")
            if any(domain in url for domain in AD_DOMAINS):
                urls.add(url)
    return urls


def collect_app_code():
    roots = [
        JADX / "free" / "vpn" / "unblock" / "proxy" / "turbovpn",
        JADX / "co" / "allconnected" / "lib" / "ad",
    ]
    java_files = sorted(
        path for root in roots if root.is_dir() for path in root.rglob("*.java")
    )

    named = [
        path
        for path in java_files
        if re.search(r"(?i)(ad|ads|monet|banner|interstitial|reward|splash|native|openad)", path.name)
    ]

    hits = []
    urls = set()
    for path in java_files:
        text = read_text(path)
        for url in URL_RE.findall(text):
            url = url.rstrip(".,;")
            if any(domain in url for domain in AD_DOMAINS):
                urls.add(url)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if CODE_RE.search(line):
                hits.append(
                    f"{path.relative_to(JADX)}:{line_number}: {line.strip()[:300]}"
                )
                if len(hits) >= 800:
                    break
        if len(hits) >= 800:
            break
    return java_files, named, hits, urls


def main():
    components, meta = parse_manifest()
    id_rows, placement_rows, missing, unused, online = collect_configs()
    app_files, app_named, app_hits, app_urls = collect_app_code()
    urls = sorted(collect_asset_urls() | app_urls)

    sdk_counts = []
    for name, prefixes in SDK_PREFIXES:
        count = sum(count_java(prefix) for prefix in prefixes)
        if count:
            sdk_counts.append((name, count))

    badging = read_text(REPORTS / "badging.txt")
    package_match = re.search(
        r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'",
        badging,
    )
    if package_match:
        package, version_code, version_name = package_match.groups()
    else:
        package, version_code, version_name = "unknown", "unknown", "unknown"

    sha = read_text(REPORTS / "apk.sha256").strip().split()[0] if (REPORTS / "apk.sha256").exists() else "unknown"

    with (REPORTS / "ad_ids.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "key", "type", "id", "desc"])
        writer.writeheader()
        writer.writerows(id_rows)

    with (REPORTS / "placements.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "placement", "chain", "keys"])
        writer.writeheader()
        writer.writerows(placement_rows)

    (REPORTS / "placements.txt").write_text(
        "\n".join(
            f"{row['file']} :: {row['placement']} :: {row['keys']}"
            for row in placement_rows
        )
        + "\n",
        encoding="utf-8",
    )
    (REPORTS / "ad_endpoints.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")
    (REPORTS / "app_ad_files.txt").write_text(
        "\n".join(str(path.relative_to(JADX)) for path in app_named) + "\n",
        encoding="utf-8",
    )
    (REPORTS / "app_ad_code_hits.txt").write_text("\n".join(app_hits) + "\n", encoding="utf-8")

    placements = sorted({row["placement"] for row in placement_rows})
    networks = sorted({row["type"] for row in id_rows if row["type"]})
    open_ad = online.get("open_ad_config", {}) if isinstance(online, dict) else {}
    sdk_names = [name for name, _ in sdk_counts]

    lines = []
    lines.append("# Turbo VPN 4.3.2.2 — static ad integration report")
    lines.append("")
    lines.append("## APK")
    lines.append("")
    lines.append(f"- Package: `{package}`")
    lines.append(f"- Version: `{version_name}` (`versionCode {version_code}`)")
    lines.append(f"- SHA-256: `{sha}`")
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    lines.append(
        f"- Bundled ad SDK families: **{len(sdk_names)}** — {', '.join(sdk_names)}."
    )
    lines.append(
        f"- Local config contains **{len(id_rows)} ad-unit mappings** in "
        f"**{len({row['file'] for row in id_rows})} files**, covering "
        f"**{len(placements)} placements**."
    )
    if missing:
        lines.append(
            f"- **{len(missing)} placement keys have no local unit mapping** "
            f"(likely supplied by remote config): {', '.join(missing)}."
        )
    else:
        lines.append("- Every locally referenced placement key has a local unit mapping.")
    lines.append(
        f"- The APK also ships a WebView ad player (`assets/iads`) and "
        f"**{len(urls)} extracted ad-related endpoints**, including the "
        f"`api.aiadsapp.net` in-house campaign/event/metric service."
    )
    if open_ad:
        lines.append(
            f"- Open-ad behavior includes back-button interception for "
            f"**{open_ad.get('intercept_millis', '?')} ms** "
            f"(`intercept_back_btn={open_ad.get('intercept_back_btn', '?')}`)."
        )
    lines.append("")
    lines.append("## Manifest-declared ad components")
    lines.append("")
    if components:
        lines.append(md_table(["Type", "Class"], components))
    else:
        lines.append("No ad components found in the decoded manifest.")
    lines.append("")
    lines.append("## Bundled SDK footprint")
    lines.append("")
    lines.append(
        "Counts are decompiled Java files under each SDK package; they show "
        "integration surface, not the number of ad calls made by the app."
    )
    lines.append("")
    lines.append(md_table(["SDK family", "Java files"], sdk_counts))
    lines.append("")
    lines.append("## Local ad-unit mappings")
    lines.append("")
    if id_rows:
        lines.append(
            md_table(
                ["Config", "Key", "Network type", "Unit ID", "Description"],
                [
                    (row["file"], row["key"], row["type"], row["id"], row["desc"])
                    for row in id_rows
                ],
            )
        )
    else:
        lines.append("No `*ad_id_config*.json` files were found.")
    lines.append("")
    lines.append("## Local placement waterfalls")
    lines.append("")
    if placement_rows:
        grouped = defaultdict(list)
        for row in placement_rows:
            grouped[(row["file"], row["placement"])].append(row)
        waterfall_rows = []
        for (config, placement), rows in sorted(grouped.items()):
            waterfall_rows.append(
                (config, placement, " | ".join(row["keys"] for row in rows))
            )
        lines.append(md_table(["Config", "Placement", "Waterfall (first choice first)"], waterfall_rows))
    else:
        lines.append("No `*ad_config*.json` placement files were found.")
    lines.append("")
    lines.append("## Config gaps and special cases")
    lines.append("")
    if missing:
        lines.append(
            "Referenced by a placement but absent from the local ID config: "
            + ", ".join(f"`{key}`" for key in missing)
            + "."
        )
    if unused:
        lines.append(
            "Defined locally but not referenced by a local placement: "
            + ", ".join(f"`{key}`" for key in unused)
            + "."
        )
    lines.append(
        "- `banner_all_config.json` has empty arrays for every banner slot, so "
        "banner IDs/placements are supplied remotely."
    )
    lines.append(
        "- `platform_ad_id_config_ir.json` adds InMobi and additional Vungle "
        "floor mappings for the Iran variant; the main Google config references "
        "some of those keys without defining them locally."
    )
    lines.append(
        "- `hms_platform_ad_config.json` is the Huawei-channel variant and uses "
        "Huawei Ads, Bigo, and Yandex placements."
    )
    lines.append("")
    lines.append("## In-house / WebView ad endpoints")
    lines.append("")
    lines.append(
        "The APK contains a separate ad player under `assets/iads/` "
        "(`index.html`, `index.js`, `mobileController.html`, and a minified SDK "
        "controller). The decompiled app code also contains an in-house "
        "`api.aiadsapp.net` campaign/event/metric service. Extracted endpoints:"
    )
    lines.append("")
    if urls:
        lines.append("\n".join(f"- `{url}`" for url in urls[:60]))
        if len(urls) > 60:
            lines.append(f"- … {len(urls) - 60} more in `reports/ad_endpoints.txt`")
    else:
        lines.append("- No ad-related URLs were extracted from the `iads` assets.")
    lines.append("")
    lines.append("## App-side ad code hotspots")
    lines.append("")
    lines.append(
        f"Scanned **{len(app_files)}** Java files in the app's own packages; "
        f"**{len(app_named)}** have ad-related filenames and "
        f"**{len(app_hits)}** matching call-site lines were recorded."
    )
    lines.append("")
    if app_named:
        lines.append("Ad-related app files (first 120):")
        lines.append("")
        lines.append("\n".join(f"- `{path.relative_to(JADX)}`" for path in app_named[:120]))
        if len(app_named) > 120:
            lines.append(f"- … {len(app_named) - 120} more in `reports/app_ad_files.txt`")
    lines.append("")
    lines.append("## Manifest ad metadata")
    lines.append("")
    if meta:
        lines.append(md_table(["Key", "Raw value line"], meta))
    else:
        lines.append("No ad-related meta-data found.")
    lines.append("")
    lines.append("## How the local configuration appears to drive ads")
    lines.append("")
    lines.append(
        "1. **Splash/open ad:** the `splash` placement tries open/ full-screen "
        "providers in order (Vungle, AdMob, Bigo) before the first screen is usable."
    )
    lines.append(
        "2. **VPN state changes:** `connected`, `disconnected`, and "
        "`return_app` placements run full-screen waterfalls after connect, "
        "disconnect, and return-to-foreground events."
    )
    lines.append(
        "3. **Server-list exit:** `go_out_server_list` runs a full-screen "
        "waterfall when the user leaves the server list."
    )
    lines.append(
        "4. **Preloading:** `app_launch`, `back_to_foreground`, "
        "`vpn_pre_connected`, `vpn_connected`, `go_to_background`, and "
        "`vpn_timer_task` timing entries preload the placements used by those events."
    )
    lines.append(
        "5. **Mediation:** the app has both direct SDK adapters and a "
        "LevelPlay/IronSource mediation path; the local waterfall order is the "
        "baseline, while remote config can change it."
    )
    lines.append(
        "6. **In-house ads:** app-side code uses `api.aiadsapp.net` for "
        "campaign, event, and metric calls; `assets/iads` is a separate WebView "
        "ad-player bundle that also carries Unity/ironSource player endpoints."
    )
    lines.append("")
    lines.append("## Artifact contents")
    lines.append("")
    lines.append("- `decompiled/apktool/` — decoded manifest and resources")
    lines.append("- `decompiled/jadx/sources/` — decompiled Java")
    lines.append("- `decompiled/assets/assets/` — extracted APK assets")
    lines.append("- `reports/findings.md` — this report")
    lines.append("- `reports/ad_ids.csv`, `placements.csv` — machine-readable config")
    lines.append("- `reports/app_ad_code_hits.txt` — app-side ad call sites")
    lines.append("- `reports/ad_endpoints.txt` — extracted ad URLs")
    lines.append("")

    (REPORTS / "findings.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORTS / 'findings.md'}")
    print(
        f"{len(id_rows)} ad units, {len(placement_rows)} waterfall rows, "
        f"{len(app_hits)} code hits, {len(urls)} URLs"
    )


if __name__ == "__main__":
    main()
