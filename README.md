# AI-Native E2E Testing with Alumnium — LLM-Driven Automation

A production-shaped demonstration of **AI-powered end-to-end testing** using
[Alumnium](https://alumnium.ai) on top of Selenium, running **fully offline** on a
local Ollama model, with **Dockerized infrastructure**, **CI/CD**, and **Allure reporting**.

> **The one-line pitch:** the same user journey, written as brittle selectors *and*
> as natural-language intent — so you can watch the selector version rot while the
> AI version keeps passing, all with **zero API keys and zero cloud calls**.

---

## Why this is interesting (the interview angle)

Alumnium is an AI layer that sits **on top of** your existing framework
(Selenium / Playwright / Appium). It reads the page's **accessibility tree**, hands a
compacted view to an LLM, and turns natural-language instructions into real browser
actions and assertions. It doesn't replace your stack — it lets you retire the fragile
parts of it, test by test.

**Before — brittle, selector-bound:**
```python
driver.find_element(By.ID, "user-name").send_keys("standard_user")
driver.find_element(By.ID, "password").send_keys("secret_sauce")
driver.find_element(By.ID, "login-button").click()
assert "Products" in driver.find_element(By.CSS_SELECTOR, ".title").text
```

**After — intent-driven, self-describing:**
```python
al.do("log in as 'standard_user' with password 'secret_sauce'")
al.check("the products page is displayed")
```

When a developer renames `#login-button` or restructures `.title`, the first test goes
red and someone re-hunts selectors. The second one keeps working because it reasons about
*what the page means*, not *where an element used to be*.

---

## Architecture

```
                ┌───────────────────────────────────────────────┐
                │                 docker compose                 │
                │                                                │
  pytest ──────▶│  tests (Alumnium + pytest + allure-pytest)     │
   -m smoke     │        │                    │                  │
                │        │ WebDriver          │ accessibility    │
                │        ▼                    │ tree + intent    │
                │  selenium/standalone-        ▼                 │
                │  chromium  (real Chromium)  ollama  (qwen3.6)  │
                │   :4444 / noVNC :7900       :11434  local LLM  │
                └───────────────────────────────────────────────┘
                                    │
                                    ▼
                        allure-results ──▶ Allure HTML report
                                            (published to GitHub Pages in CI)
```

Everything the AI needs is a model endpoint. Here that endpoint is a **local Ollama
container** — nothing leaves the machine.

## Tech stack

| Layer            | Choice                                              |
|------------------|-----------------------------------------------------|
| AI test layer    | Alumnium (`al.do` / `al.check` / `al.get`)          |
| Browser driver   | Selenium 4, `selenium/standalone-chromium`          |
| LLM              | Ollama `qwen3.6`, fully local (no keys)             |
| Runner           | pytest + markers (`ai`, `classic`, `smoke`)         |
| Reporting        | Allure (steps, screenshots-on-failure, env, history)|
| Infra            | Docker + docker-compose, Makefile                   |
| CI/CD            | GitHub Actions → Allure report on GitHub Pages      |

## Project layout

```
.
├── conftest.py                 # driver/al fixtures, Allure screenshot hook, env metadata
├── tests/
│   ├── ai_steps.py             # wraps al.do/check/get as Allure steps (human-readable log)
│   ├── test_login.py           # AI login: valid + locked-out user
│   ├── test_checkout.py        # AI end-to-end purchase + al.get() data extraction
│   ├── test_comparison.py      # ⭐ brittle selectors vs AI intent, side by side
│   └── pages/inventory_page.py # classic Page Object (the maintenance liability)
├── docker-compose.yml          # ollama + model-pull + selenium + runner
├── Dockerfile                  # test-runner image
├── .github/workflows/ci.yml    # CI/CD + Allure publish
├── Makefile                    # test / smoke / report / demo targets
└── .env.example
```

---

## Run it

### Option A — fully offline, in Docker (recommended)
```bash
cp .env.example .env
make test          # builds runner, starts Ollama + Selenium, pulls qwen3.6, runs suite
make report        # open the Allure report (needs the Allure CLI locally)
```
First run downloads the `qwen3.6` weights into a named volume; later runs are faster.
Watch the AI drive the real browser live at **http://localhost:7900** (noVNC password: `secret`).

### Option B — live headed demo (no Docker)
Great for screen-sharing in the interview. Needs local Chrome + a local Ollama:
```bash
ollama pull qwen3.6
cp .env.example .env          # ALUMNIUM_MODEL=ollama, SELENIUM_URL empty
HEADLESS=false pytest -m ai -k comparison
```

---

## CI/CD strategy (and an honest note)

`.github/workflows/ci.yml` brings the same stack up in Actions, runs the **smoke**
subset, then builds an Allure report **with trend history** and publishes it to
**GitHub Pages** (enable Pages → deploy from `gh-pages`).

**The honest part an interviewer will respect:** local LLM inference on a CPU-only
GitHub-hosted runner didn't just turn out *slow* — it turned out infeasible at every
size tried. The full-fidelity `qwen3.6:35b` (~23GB) doesn't fit the 16GB RAM a
standard public-repo runner gets; a `qwen3:4b` that does fit can't finish a planning
call inside Alumnium's fixed 120s HTTP client timeout; and a `qwen3:1.7b` fast enough
to answer in time isn't reliable enough to actually drive the real login form.

So CI runs on the **GitHub Models API** instead (`docker-compose.ci.yml`, applied via
`docker compose -f docker-compose.yml -f docker-compose.ci.yml run ...`) —
`ALUMNIUM_MODEL=github`, authenticated with the workflow's own `GITHUB_TOKEN` via the
`models: read` permission, so no secret to provision. `make test` and the live demo
are untouched and still use the offline `qwen3.6` default. That's exactly the
provider-swap design decoupling *test intent* from *model* was meant to demonstrate:
same test code, one env var, zero code changes to fall back to a hosted model where
local CPU inference can't cut it. CI also runs `-m smoke`, not the full suite.

Two more ways to scale it further — worth mentioning as design judgment:

1. **Self-hosted / GPU runner** for a nightly full run against the full-fidelity
   `qwen3.6` model, fully offline.
2. **A different hosted provider**, e.g. `ALUMNIUM_MODEL=google` (Google AI Studio,
   needs a `GOOGLE_API_KEY` secret) — useful if GitHub Models' rate limits or model
   choice become a constraint.

---

## Talking points for the interview

- **Incremental adoption, not rip-and-replace.** Alumnium coexists with existing
  Selenium suites and CI — you migrate the flaky bits one test at a time.
- **Maintenance cost.** Natural-language steps survive most UI refactors that shatter
  selector-based tests; `test_comparison.py` makes that contrast concrete.
- **Self-documenting reports.** Every AI step becomes an Allure step, so the report reads
  like a manual test case — no parallel step descriptions to maintain.
- **Deterministic where it matters.** `al.get()` returns typed values, so you still make
  hard, exact assertions (`assert count == 1`) rather than trusting fuzzy prose.
- **Cost & privacy.** Running on local Ollama means no per-run API spend and no page
  content leaving the network — relevant for regulated or sensitive apps.
- **Known trade-offs (say them first).** LLM latency vs. selectors; non-determinism to
  budget for; Alumnium/Ollama support is still maturing. Good SDETs name the risks.

## Notes & tuning

- Model tag follows Alumnium's docs (`qwen3.6`). If your Ollama registry differs, run
  `ollama list` and adjust the tag in `docker-compose.yml` and `.env`.
- If your Alumnium version needs a provider extra, install `alumnium[ollama]` in
  `requirements.txt`.
- System under test is public [SauceDemo](https://www.saucedemo.com); swap `BASE_URL` to
  point the whole suite at your own app.
