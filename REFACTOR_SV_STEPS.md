checklist you can follow to refactor your script. it’s tailored to the exact functions you pasted, with file paths and explicit TODOs.

# repo layout to create (no code yet)

serp\_agent/

* **init**.py
* config/

  * settings.py
  * constants.py
* logging/

  * logger.py
* proxy/

  * extension\_builder.py
  * env\_proxy.py
* browser/

  * driver\_factory.py
  * history.py
  * consent.py
  * actions.py
  * diagnostics.py
* net/

  * url\_utils.py
* serp/

  * base.py
  * google.py
  * bing.py
  * scan\_strategies.py
  * challenge.py
  * router.py
* runner/

  * run\_task.py
  * cli.py
* errors.py
* types.py
  tests/
  docs/

---

# migration checklist (step-by-step)

## 1) bootstrap the package

* create the folder structure above.
* in `logging/logger.py`: move the current `log(msg: str)` function here.

  * TODO: ensure every future module imports `log` from this file only.

## 2) extract pure helpers first (safe moves)

* create `net/url_utils.py`.

  * TODO: move `extract_final_url` and `url_matches_domain` here.
  * TODO: add small docstrings describing inputs/outputs.
* create `config/constants.py`.

  * TODO: centralize static strings and numbers (UA strings, default window sizes, default timeouts like SERP wait, scroll step).
  * TODO: define device profiles names: “desktop”, “mobile/pixel5”.

## 3) configuration model

* create `config/settings.py`.

  * TODO: define conceptual configs (names only, no code):

    * BrowserConfig: device, headless, user\_data\_dir, profile\_directory, language, UA, window size.
    * ProxyConfig: enabled flag, proxy\_url (already encoded).
    * SearchConfig: engine, max\_pages, scroll\_steps\_per\_batch, timeouts.
    * PathsConfig: snapshot\_dir, history\_wipe\_enabled.
    * Settings: {browser, proxy, search, paths}.
  * TODO: plan a `from_env` loader that reads the same env vars your script uses:

    * SEARCH\_QUERY, TARGET\_DOMAIN, DEVICE, HEADLESS, MAX\_PAGES, SCROLLS\_PER\_BATCH, ENGINE, USER\_DATA\_DIR, PROFILE\_DIRECTORY.
    * PROXY\_USERNAME, PROXY\_PASSWORD, PROXY\_HOST, PROXY\_PORT.

## 4) proxy pieces

* `proxy/extension_builder.py`

  * TODO: move `build_proxy_extension` here (unchanged behavior).
  * TODO: ensure it returns a ZIP path string (as today).
* `proxy/env_proxy.py`

  * TODO: move `build_proxy_url_from_env` here.
  * TODO: keep masking of username in logs.
  * TODO: ensure this file is the only one touching dotenv.

## 5) browser setup & utilities

* `browser/driver_factory.py`

  * TODO: move `build_driver` here.
  * TODO: replace direct calls to proxy builder with a parameter that accepts `proxy_url`; do not import dotenv here.
  * TODO: pull UA strings and device metrics from `config/constants.py`.
  * TODO: keep CDP anti-automation tweaks here.
* `browser/history.py`

  * TODO: move `wipe_browsing_history` here.
* `browser/consent.py`

  * TODO: move `accept_cookies_if_present` here.
* `browser/actions.py`

  * TODO: move `click_safely`, `robust_tap`, and `find_more_results_control` here.
* `browser/diagnostics.py`

  * TODO: move `dump_serp_snapshot` here.
  * TODO: include optional viewport/UA logging.

## 6) search (SERP) layer

* `serp/base.py`

  * TODO: define the surface (names only):

    * SearchEngine interface: `prepare(driver)`, `perform_query(driver, query)`, `find_and_click_target(driver, target_domain) → SearchStatus`.
    * SearchStatus enum: CLICKED, NOT\_FOUND, CHALLENGE, ERROR.
* `serp/challenge.py`

  * TODO: move `is_google_challenge` here.
* `serp/scan_strategies.py`

  * TODO: move `progressive_scroll_and_scan` and `attempt_load_more_or_next` here.
  * TODO: have them depend on `browser/actions.py` and `net/url_utils.py`.
* `serp/google.py`

  * TODO: move Google-specific pieces:

    * `ensure_serp_loaded`
    * `search_and_click_domain_google` (split internally across `prepare`, `perform_query`, `find_and_click_target`).
    * use `serp/challenge.py` for challenge checks.
* `serp/bing.py`

  * TODO: move `search_and_click_domain_bing` here and adapt to the base interface.
* `serp/router.py`

  * TODO: move `search_and_click_domain` logic here:

    * if engine == google → use GoogleSearchEngine
    * if engine == bing → use BingSearchEngine
    * if auto → try Google; on CHALLENGE fall back to Bing.

## 7) errors and protocols

* `errors.py`

  * TODO: declare names for `ChallengeDetected`, `NavigationError`, `ConfigError` to replace ambiguous returns where useful.
* `types.py`

  * TODO: declare minimal `DriverProtocol` and `ElementProtocol` (method names only) to help with testing/mocking later.

## 8) runner and CLI

* `runner/run_task.py`

  * TODO: move `run_task` here. It should orchestrate:

    * build Settings (incoming args or env)
    * obtain `proxy_url` from `proxy/env_proxy.py` (respect “proxy off” if missing)
    * call `browser/driver_factory.build_driver`
    * pick engine via `serp/router`
    * run prepare → perform\_query → find\_and\_click\_target
    * log outcome
    * teardown: `driver.quit()` then `browser/history.wipe_browsing_history` if enabled
* `runner/cli.py`

  * TODO: parse env/args into `Settings` and call `run_task`.
  * TODO: keep existing environment variable names for backwards compatibility.

## 9) main stub

* root `__main__` or small script (optional)

  * TODO: replace old inline `if __name__ == "__main__":` with a call into `runner/cli.py`.

## 10) import replacement pass (mechanical)

Search/replace in the codebase:

* `log` → `from serp_agent.logging.logger import log`
* `build_proxy_extension` → `from serp_agent.proxy.extension_builder import build_proxy_extension`
* `build_proxy_url_from_env` → `from serp_agent.proxy.env_proxy import build_proxy_url_from_env`
* `build_driver` → `from serp_agent.browser.driver_factory import build_driver`
* `wipe_browsing_history` → `from serp_agent.browser.history import wipe_browsing_history`
* `accept_cookies_if_present` → `from serp_agent.browser.consent import accept_cookies_if_present`
* `click_safely`, `robust_tap`, `find_more_results_control` → `from serp_agent.browser.actions import ...`
* `dump_serp_snapshot` → `from serp_agent.browser.diagnostics import dump_serp_snapshot`
* `extract_final_url`, `url_matches_domain` → `from serp_agent.net.url_utils import ...`
* Google/Bing search functions → referenced via `serp.router` not directly.

---

# function-by-function TODO map

logging/logger.py

* keep current print-based `log`.
* later: optional toggle for debug level.

proxy/extension\_builder.py

* take `proxy_url` and return ZIP path.
* ensure MV3 manifest/permissions unchanged.

proxy/env\_proxy.py

* read environment, URL-encode credentials, assemble proxy URL.
* keep masked logging of username and host/port.
* gracefully return None when incomplete.

browser/driver\_factory.py

* accept: proxy\_url, device, headless, user\_data\_dir, profile\_directory.
* apply device emulation (desktop vs pixel5) using constants.
* inject CDP anti-automation script.
* verify viewport after launch (as you already do).

browser/consent.py

* keep cookie acceptance logic with top-level and iframe paths.

browser/actions.py

* `click_safely`: scroll into view + normal/JS click fallback.
* `robust_tap`: blur, scroll center, normal click, JS click, synthetic events, CDP touch.
* `find_more_results_control`: multi-locator lookup, return visible element.

browser/diagnostics.py

* keep UA/viewport logs and HTML snapshot saver.

net/url\_utils.py

* `extract_final_url` for Google redirectors.
* `url_matches_domain` using netloc endswith.

serp/challenge.py

* `is_google_challenge` heuristics.

serp/scan\_strategies.py

* `progressive_scroll_and_scan`: stepwise scroll, scan anchors, match domain, click.
* `attempt_load_more_or_next`: desktop “Next”, mobile “More results”, infinite scroll, snapshot on failure.

serp/google.py

* `prepare`: open ncr, accept cookies.
* `perform_query`: type query char-by-char, submit, wait for SERP or challenge.
* `find_and_click_target`: loop pages calling scan strategy; stop on match; handle timeouts.

serp/bing.py

* same shape; simpler pagination; reuse url utils and actions.

serp/router.py

* route by engine; implement “auto” fallback when Google returns CHALLENGE.

runner/run\_task.py

* glue everything; ensure teardown order: quit → history wipe.

---

# config & env mapping checklist

map existing env vars to Settings:

* SEARCH\_QUERY → Search input
* TARGET\_DOMAIN → Target domain
* DEVICE (“desktop”|“mobile”) → BrowserConfig.device
* HEADLESS (“true”/“false”) → BrowserConfig.headless
* MAX\_PAGES → SearchConfig.max\_pages
* SCROLLS\_PER\_BATCH → SearchConfig.scroll\_steps\_per\_batch
* ENGINE (“auto”|“google”|“bing”) → SearchConfig.engine
* USER\_DATA\_DIR → BrowserConfig.user\_data\_dir
* PROFILE\_DIRECTORY → BrowserConfig.profile\_directory
* PROXY\_USERNAME / PROXY\_PASSWORD / PROXY\_HOST / PROXY\_PORT → ProxyConfig via env\_proxy

centralize timeouts in `config/constants.py`:

* SERP load timeout
* element wait time
* scroll step size
* jitter delays

---

# test checklist (no browser required where possible)

unit (pure functions)

* url\_utils: google redirect extraction; domain match for subdomains, ports, creds in netloc.
* challenge: detect “unusual traffic” and captcha markers with sample titles/snippets.
* scan\_strategies: run against a fake driver object that records scrolls/clicks and returns synthetic anchors.
* router: given statuses, ensure fallback from Google→Bing happens exactly once.

integration (optional)

* smoke run with headless on a benign query; verify status transitions and that teardown wipes history files in a temp profile dir.

---

# smoke-test run order (manual)

1. run without proxy: ensure it reaches SERP and scans.
2. run with proxy env populated: ensure the extension loads (check logs).
3. run mobile device: verify viewport log shows expected DPR and size.
4. force a Google challenge (if reproducible): confirm Bing fallback triggers.
5. verify history files removed post-quit when user\_data\_dir is set.

---

# guardrails to prevent future breakage

* only `runner/run_task.py` is allowed to call `driver.quit()` and `history.wipe_browsing_history`.
* only `proxy/env_proxy.py` touches environment and dotenv.
* only `logging/logger.py` prints; everything else imports `log`.
* `serp/*` must not import `browser/driver_factory.py` or proxy modules directly.
* tune knobs (timeouts/UA/scroll) live only in `config/constants.py` and `config/settings.py`.

---

# docs to add

* `docs/architecture.md`: module diagram + sequence flow from `run_task` through router to engines.
* `docs/developing.md`: how to run, env variables, adding a new engine, where to tune timeouts.

---


