---
name: effort-low
description: Internal Claude-only low effort control. Invoke only after native support and scoped user preferences permit this override; never override an explicit effort choice or use in Codex. Skip short answers and redundant switches.
effort: low
user-invocable: false
---

Continue the authorized task at low effort where supported. Keep the same scope, permissions and required checks. Escalate if material uncertainty or consequential behavior appears. This native override lasts for the current turn; it does not change saved settings. Follow the core's model-routing policy. This does not select a model or prove the effective effort; host caps and overrides still apply. Report a blocked or materially different result from native evidence, not self-identification.
