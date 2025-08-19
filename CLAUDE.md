blueprint you can follow to split things up, clarify responsibilities, and add features without cross-breaking.

# high-level goals

* single responsibility per module: browser setup, proxy, search logic, helpers, orchestration.
* clean public API: a small set of dataclasses/configs + one or two “runner” entry points.
* dependency inversion: core logic depends on interfaces (e.g., “SearchEngine”, “DriverFactory”), not concrete selenium bits.
* testability: most logic testable without launching a real browser.

# proposed package layout

serp\_agent/

* **init**.py
* config/

  * settings.py              (all configuration dataclasses + env loading)
  * constants.py             (timeouts, UA strings, device metrics)
* logging/

  * logger.py                (log function; optional structured logging)
* proxy/

  * extension\_builder.py     (build\_proxy\_extension)
  * env\_proxy.py             (build\_proxy\_url\_from\_env)
* browser/

  * driver\_factory.py        (build\_driver + device emulation)
  * history.py               (wipe\_browsing\_history)
  * consent.py               (accept\_cookies\_if\_present)
  * actions.py               (click\_safely, robust\_tap)
  * diagnostics.py           (dump\_serp\_snapshot)
* net/

  * url\_utils.py             (extract\_final\_url, url\_matches\_domain)
* serp/

  * base.py                  (abstract SearchEngine interface, common helpers)
  * google.py                (google engine: ensure\_serp\_loaded, challenge detect, pagination)
  * bing.py                  (bing engine)
  * scan\_strategies.py       (progressive\_scroll\_and\_scan, load-more/next strategy)
  * challenge.py             (is\_google\_challenge)
  * router.py                (engine selection: auto/google/bing)
* runner/

  * run\_task.py              (orchestrates: build driver → run search → teardown)
  * cli.py                   (arg/env parsing and a console entrypoint)
* errors.py                  (custom exceptions: ChallengeDetected, NavigationError, ConfigError)
* types.py                   (protocols/interfaces for driver & elements to ease mocking)
* tests/                     (unit + integration; mocks for driver/actions)
* docs/

  * architecture.md          (diagram, sequence flows, config reference)
  * developing.md            (how to run, test, extend)

# responsibilities & boundaries

config/settings.py

* define cohesive settings objects: BrowserConfig, ProxyConfig, SearchConfig, PathsConfig, RuntimeFlags.
* a composite Settings that holds them all and a single “from\_env()” loader.
* centralize defaults (device, headless, max\_pages, timeouts, profile paths).

logging/logger.py

* single log() function (and optionally a structured logger). ensure every module imports from here, not print directly.

proxy/extension\_builder.py

* only knows how to generate the MV3 ZIP from a full proxy url.
* no selenium, no dotenv here.

proxy/env\_proxy.py

* reads dotenv, builds and returns a proxy url string (also masks username when logging).

browser/driver\_factory.py

* creates and configures the undetected chromedriver instance.
* applies device emulation based on BrowserConfig (desktop vs pixel profile).
* injects CDP anti-automation tweaks.
* returns a webdriver implementing a small DriverProtocol (defined in types.py).
* never performs search; just setup/tear-down concerns.

browser/history.py

* wipes history files after the driver closes (path logic isolated here).

browser/consent.py

* cookie/consent handling, including iframes.
* no direct logging of DOM except via logger.

browser/actions.py

* scrolling/tapping/click helpers, including robust\_tap and click\_safely.
* strictly UI interaction utilities.

browser/diagnostics.py

* dump\_serp\_snapshot, viewport/UA dumps.

net/url\_utils.py

* final URL extraction and domain matching, pure functions.

serp/base.py

* define a SearchEngine interface with methods like:

  * prepare(driver)
  * perform\_query(driver, query)
  * find\_and\_click\_target(driver, target\_domain) → bool/status
* define a SearchStatus enum (CLICKED / NOT\_FOUND / CHALLENGE / ERROR).
* keep engine-agnostic helpers here if they’re truly shared.

serp/google.py

* concrete GoogleSearchEngine implementing base interface.
* ensure\_serp\_loaded, challenge detection, pagination/“More results”.
* uses scan\_strategies for scanning—no hardcoded loops here.

serp/bing.py

* concrete BingSearchEngine, simpler pagination/anchor scanning.

serp/scan\_strategies.py

* progressive\_scroll\_and\_scan strategy encapsulated with tunables:

  * step\_px, max\_steps, throttle pattern, and a SeenLinks registry.
* attempt\_load\_more\_or\_next strategy for both desktop/mobile.

serp/challenge.py

* is\_google\_challenge and related heuristics isolated for clarity/testing.

serp/router.py

* engine selection logic:

  * “google” → GoogleSearchEngine
  * “bing” → BingSearchEngine
  * “auto” → try Google; on CHALLENGE fall back to Bing
* owns the retry/fallback policy; other modules don’t branch on engine.

runner/run\_task.py

* orchestration:

  1. load Settings (env or args)
  2. make proxy url if configured
  3. build driver
  4. pick engine via router
  5. run engine flow: prepare → perform\_query → find\_and\_click\_target
  6. log final status
  7. teardown: quit driver, wipe history if enabled
* single, clean function callable from code.

runner/cli.py

* turns env/args into Settings and calls run\_task.
* defines the console script entry point.

errors.py

* canonical exceptions to avoid stringly-typed error handling.
* use for predictable control flow (e.g., challenge surfaced as ChallengeDetected).

types.py

* DriverProtocol & ElementProtocol (minimal subset of selenium you actually use).
* makes unit-testing possible with a FakeDriver.

# public API (what outside code is allowed to touch)

* serp\_agent.run(query, target, settings) or runner.run\_task.run(search\_query, target\_domain, settings)
* config Settings/BrowserConfig/SearchConfig constructors or from\_env
* nothing else—keep internals private to reduce coupling.

# data & configuration model (no code, just shape)

* BrowserConfig: device (“desktop”|“mobile”), headless, user\_data\_dir, profile\_directory, language, UA, window size.
* ProxyConfig: url (already encoded), enabled flag.
* SearchConfig: engine (“auto”|“google”|“bing”), max\_pages, scroll\_steps\_per\_batch, timeouts.
* PathsConfig: output paths for snapshots, temp dirs; history wipe toggle.
* Settings: {browser, proxy, search, paths}.

# control flow (sequence overview)

1. settings loaded (env → Settings)
2. proxy url built (if env present) → BrowserConfig gets extension path via proxy module
3. driver\_factory builds driver with device emulation
4. router chooses search engine
5. engine.prepare: navigate to engine landing page, accept cookies
6. engine.perform\_query: type query, wait for results or challenge
7. engine.find\_and\_click\_target:

   * scan\_strategies.progressive\_scroll\_and\_scan with domain match
   * if not found, scan\_strategies.attempt\_load\_more\_or\_next
   * repeat until max\_pages or click success
8. engine returns SearchStatus
9. runner logs outcome, quits driver, optionally wipes history

# extension points (future-proofing)

* add a new search engine: implement SearchEngine and register in router.
* swap scanning logic: new strategy class injected via SearchConfig.
* device profiles: add profiles in constants.py and pick by name in BrowserConfig.
* proxy modes: add “system proxy” or “no-auth proxy” builder alongside extension.

# testing strategy

unit tests (fast, no browser):

* url\_utils: final URL extraction and domain matching.
* challenge heuristics: feed HTML snippets to predicate functions.
* scan\_strategies: use a FakeDriver that exposes a synthetic DOM and records scroll/click calls.
* router: engine selection outcomes for various statuses.

integration tests (optional, slower):

* spin a headless driver once; test basic query on a benign engine with mocks for target matches (or against a local test page).
* verify that history wipe deletes expected files on teardown (guarded by tmp profile dirs).

# guardrails to reduce cross-breakage

* no module reaches “across the stack”. browser/\* never imports serp/*; serp/* never reaches proxy/\* directly (only via Settings).
* all timeouts, waits, and tuning knobs centralized in constants.py and SearchConfig.
* only runner calls driver.quit and history wipe.
* logger is the only place that prints; keep log messages consistent (“\[serp]”, “\[driver]”, etc.) for quick grepping.

# migration plan (stepwise refactor)

1. create package skeleton and copy the existing log() into logging/logger.py. update all references to import from there.
2. move pure helpers first:

   * net/url\_utils.py
   * errors.py
   * config/constants.py
3. split proxy pieces:

   * proxy/extension\_builder.py
   * proxy/env\_proxy.py
4. extract browser modules:

   * driver\_factory.py (build\_driver)
   * history.py (wipe)
   * consent.py, actions.py, diagnostics.py
5. carve out serp:

   * base.py (interface + status enum)
   * google.py (move: ensure\_serp\_loaded, challenge detect, google search flow)
   * scan\_strategies.py (progressive scrolling, load-more/next)
   * bing.py
   * router.py (auto fallback policy)
6. introduce config/settings.py with the shapes above and replace scattered env reads.
7. build runner/run\_task.py that wires everything via Settings.
8. keep the original **main** stub but reduce it to build Settings → call runner.
9. add the first unit tests for url\_utils and challenge detection.
10. delete dead imports and duplicate helpers; freeze the public API.

# observability (optional but helpful)

* structured logs: engine, device, page\_idx, scroll\_step, action (“click”, “load\_more”), outcome, elapsed\_ms.
* diagnostic snapshots behind a “debug” flag in Settings.

# docs for future contributors (docs/architecture.md)

* module graph: config → proxy → browser → serp → runner.
* sequence diagram for “auto” engine with Google → challenge → Bing fallback.
* configuration matrix: desktop vs mobile, headless vs headed, proxy on/off.

# what you gain

* clarity: each module does one thing, names match the behavior.
* safer changes: add a new engine or tweak scrolling without touching driver setup.
* testability: most logic decoupled from a live browser.
* portability: a clean entry point you can call from other scripts or a CLI.

