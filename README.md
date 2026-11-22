# Turbo VPN 4.3.2.2 — ad integration analysis

Static analysis of the `Turbo VPN.apk` package from the device:

- Package: `free.vpn.unblock.proxy.turbovpn`
- Version: `4.3.2.2` (`versionCode 2026102111`)
- SHA-256: `f674a22e5c28ceacd48dcff2253217780707d45013e0a414b051286ea28e13bb`

The APK is included only so the GitHub Actions runner can decompile it. No GitHub token or signing secret is stored in this repository.

## Run

Actions → **Decompile and analyze Turbo VPN ads** → **Run workflow**.

The workflow:

1. Verifies the APK hash and prints its manifest metadata.
2. Decodes `AndroidManifest.xml` and resources with Apktool.
3. Extracts `assets/` (including the local ad configuration and the `iads` WebView ad player).
4. Decompiles all six DEX files with JADX on the hosted runner.
5. Generates `reports/findings.md`, `reports/ad_ids.csv`, `reports/placements.csv`, and code/endpoint hit lists.
6. Uploads the decompiled tree and reports as the `turbo-vpn-4.3.2.2-analysis` artifact.

## What the report covers

- Manifest-declared ad SDK components and ad-related metadata.
- Bundled mediation/ad SDK footprint (AdMob, LevelPlay/IronSource, Unity Ads, Vungle, InMobi, Yandex, Bigo, TradPlus, Monetrix, Huawei, and others present in the APK).
- Local `platform_ad_config*.json` placement waterfalls and `platform_ad_id_config*.json` unit mappings.
- Ad units referenced by a placement but not defined in the local config (usually supplied by remote config).
- The in-house `assets/iads` player and its `api.aiadsapp.net` campaign/event/metric endpoints.
- App-side ad wrapper classes and call-site hotspots under `free.vpn.unblock.proxy.turbovpn` and `co.allconnected.lib.ad`.

## Scope

This is static analysis of an APK already on the user's device. It does not intercept traffic, bypass the VPN, or modify the app. Remote configuration can change the placement order and ad units at runtime, so the local JSON is a baseline rather than a live snapshot.
