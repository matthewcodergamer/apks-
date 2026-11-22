# Turbo VPN — ad removal, VIP unlock, and 4.3.2.2 analysis

## Download

Latest patched build:

**https://github.com/matthewcodergamer/apks-/releases/download/v4.3.2.2-ads-vip/turbo-vpn-4.3.2.2-arm64-ads-vip-log.apk**

- Size: `51,357,896` bytes
- SHA-256: `ed2e4072c65b98b262147ac2da89ec967c62366d368173ba235e4703022a5102`

Uninstall any older Turbo VPN build first (the signature is different). If the
connection still fails, the log panel opens automatically at the bottom of the
main screen and refreshes every 1.5 seconds. Tap **LOG** to toggle it, and
long-press the **LOG** button or the log panel to copy the log.

## Patched build (ads removed + locations unlocked)

`turbo-vpn-4.3.2.2-arm64.apk` is the complete standalone arm64-v8a build used
for the patched APK:

- Package: `free.vpn.unblock.proxy.turbovpn`
- Version: `4.3.2.2` (`versionCode 2026102111`)
- Architecture: `arm64-v8a`
- Includes `libovpnutil.so`, `libxray.so`, and the other native VPN libraries

This is the exact version installed on the device, with the ABI libraries that
the base APK was missing.

### Workflow

Actions → **Patch Turbo VPN ads** → **Run workflow**.

The workflow:

1. Disassembles `classes.dex` and `classes5.dex` with baksmali.
2. Removes the ad surfaces:
   - `co.allconnected.lib.ad.c.q(Context, boolean)` — platform ad-config loader
   - `co.allconnected.lib.ad.BannerAdAgent.f(int, int)` — banner config parser
   - `co.allconnected.lib.ad.AdShow.h(boolean)` — full-screen ad selection
   - `co.allconnected.lib.ad.AdShow.k(boolean)` — full-screen ad list
   - `D5.H.D()` — AppLuck hover-ad refresh
   - `VpnMainActivity.r4(String)` — `HomeAdActivity` deep-link launcher
3. Restores the API keys that `libovpnutil.so` normally derives from the
   original signing certificate. Re-signing makes the native check return
   `null`, which breaks activation and the server list:
   - `NativeUtils.getApiCipherKey(Context)` — API body-encryption key
   - `NativeUtils.getApiHeaderKey(Context)` — API auth-header key
   - `NativeUtils.getLocalCipherKey(Context)` — local cache key
4. Unlocks the VIP server locations:
   - `k2.A.v()` — always report a VIP user
   - `k2.A.q(Context)` — use the VIP server lists
   - `k2.A.i()` — report the maximum VIP level
   - `k2.A.t()` — disable trial-only restrictions
   - `k2.A.e()` — prevent VIP-list expiry cleanup
   - `ReqServersListBean.setIsVip(boolean)` — keep the server-list request on
     the free-user path so the server returns a usable list
   - `VpnServer.compareTo(VpnServer)` — sort free servers before VIP servers, so
     the default connection uses a free server while VIP locations stay in the
     list
5. Enables the app's own debug logging (`g2.g.k(int)`) and injects a **LOG**
   button into `VpnMainActivity`. The non-modal bottom overlay opens on launch
   and refreshes the last 400 logcat lines every 1.5 seconds. Tap **LOG** to
   toggle it; long-press **LOG** or the overlay to copy the log, so
   connection/API errors can be captured on the device without ADB.
6. Reassembles the two DEX files and replaces only those entries in the APK.
7. Removes the original signature, zipaligns, and signs with a debug key.
8. Verifies the signature, alignment, native libraries, every stub, the
   injected classes, and the LOG button hook.
9. Uploads `turbo-vpn-4.3.2.2-arm64-ads-vip-log.apk` plus `SHA256SUMS`.

VPN/native code and resources are left untouched. Because the APK is re-signed,
Google/Facebook sign-in and Play Billing will not work; the VPN connection is
unaffected. Uninstall the Play Store version before installing this one,
because Android refuses updates signed with a different key.

## Analysis of the installed 4.3.2.2 base

Static analysis of the `Turbo VPN.apk` package from the device:

- Package: `free.vpn.unblock.proxy.turbovpn`
- Version: `4.3.2.2` (`versionCode 2026102111`)
- SHA-256: `f674a22e5c28ceacd48dcff2253217780707d45013e0a414b051286ea28e13bb`

The base APK is included only so the GitHub Actions runner can decompile it. No
GitHub token or signing secret is stored in this repository.

### Run the analysis

Actions → **Decompile and analyze Turbo VPN ads** → **Run workflow**.

The analysis workflow:

1. Verifies the APK hash and prints its manifest metadata.
2. Decodes `AndroidManifest.xml` and resources with Apktool.
3. Extracts `assets/` (including the local ad configuration and the `iads` WebView ad player).
4. Decompiles all six DEX files with JADX on the hosted runner.
5. Generates `reports/findings.md`, `reports/ad_ids.csv`, `reports/placements.csv`, and code/endpoint hit lists.
6. Uploads the decompiled tree and reports as the `turbo-vpn-4.3.2.2-analysis` artifact.

### What the report covers

- Manifest-declared ad SDK components and ad-related metadata.
- Bundled mediation/ad SDK footprint (AdMob, LevelPlay/IronSource, Unity Ads, Vungle, InMobi, Yandex, Bigo, TradPlus, Monetrix, Huawei, and others present in the APK).
- Local `platform_ad_config*.json` placement waterfalls and `platform_ad_id_config*.json` unit mappings.
- Ad units referenced by a placement but not defined in the local config (usually supplied by remote config).
- The in-house `assets/iads` player and its `api.aiadsapp.net` campaign/event/metric endpoints.
- App-side ad wrapper classes and call-site hotspots under `free.vpn.unblock.proxy.turbovpn` and `co.allconnected.lib.ad`.

### Scope

This is static analysis of an APK already on the user's device. It does not
intercept traffic, bypass the VPN, or modify the app. Remote configuration can
change the placement order and ad units at runtime, so the local JSON is a
baseline rather than a live snapshot.
