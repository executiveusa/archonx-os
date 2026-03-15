---
triggers:
- browse
- qa
- test site
- screenshot
- persistent browser
- gstack
- click through
- automated testing
---
# GStack Workflows — FrankenClaw Browser Integration

You are operating Darya's FrankenClaw persistent browser engine.
Use PersistentBrowserEngine from `archonx/tools/browser_agent.py`.

## Key Behaviors

**ALWAYS use the persistent browser singleton:**
```python
from archonx.tools.browser_agent import PersistentBrowserEngine
engine = await PersistentBrowserEngine.get_instance()
# Browser stays alive — 100-200ms per action, not 3-5s
```

## Workflow Commands

### /browse <url>
Navigate to URL, screenshot, extract key elements, report back.
```python
await engine.navigate(url)
screenshot = await engine.screenshot()
content = await engine.get_content()
```

### /qa <route>
Test a route automatically after code changes:
1. Navigate to the affected route
2. Click through primary user flows
3. Screenshot before/after
4. Check for console errors via evaluate()
5. Report: pass/fail + screenshots

### /login-test <url> <selector_map>
Log in and verify auth flow persists across tabs.
Cookies and session stay active — no re-login between commands.

### /screenshot-diff
Capture full-page screenshot, compare to last baseline.
Highlight visual regressions.

## Guardrails
- Never store credentials in browser context beyond session
- Screenshot every destructive action (delete, submit, purchase)
- Max 50 browser actions per BMAD sprint before checkpoint
- Auto-stop after 30min idle (built into engine)
