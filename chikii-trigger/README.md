# Chikii decompile trigger

Pushing a change under `chikii-trigger/` starts the **Decompile Chikii** workflow.
The workflow downloads the original 4.16.0 APK release asset, runs jadx and
apktool on the GitHub runner, and uploads the decompiled output as the
`chikii-decompiled` artifact.

Run: 2
