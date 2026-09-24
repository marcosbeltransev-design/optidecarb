# OptiDecarb deployment recovery

This runbook exists so the public CV link can be restored without reconstructing the deployment setup from memory.

## Production configuration

- Repository: `marcosbeltransev-design/optidecarb`
- Branch: `main`
- Streamlit entrypoint: `app.py`
- Public technical app: `https://optidecarb.streamlit.app`
- App version: `1.3.2`
- Optimization model: `0.3.0`
- Python requirement: `>=3.11`
- CI Python: `3.13`; the deployed Community Cloud Python version is not yet verified (requires authenticated app settings/logs).
- Streamlit: `1.62.0`
- SciPy / HiGHS interface: `1.17.0` (pinned for regression reproducibility)
- Install file: `requirements.txt` → `-e .[app]`

The current `app.py` routes to the v1.3.2 evidence/data-forensics learning layer. It builds on the validated v1.3.1 UI and keeps Optimization Model v0.3.0 unchanged.

## If the Streamlit app is unavailable

1. Open Streamlit Community Cloud and locate OptiDecarb.
2. Check whether the app is sleeping/hibernating before changing code.
3. If there is an application/build error, open **Manage app → Logs** and read the real exception first.
4. Verify repository=`marcosbeltransev-design/optidecarb`, branch=`main`, entrypoint=`app.py`.
5. If configuration and code are correct, use **Reboot app** and wait for the build to finish.
6. If a stale build is suspected, make a harmless dependency-file comment on a recovery branch, run CI, merge, and let Community Cloud rebuild from `main`.
7. Delete/recreate the Streamlit app only as a last resort. Preserve the subdomain `optidecarb` because it is used externally.

## Before merging any recovery change

Require the existing CI checks to pass: unit tests, integration tests, Streamlit AppTest, Golden v1/v2/v3 and `ceramic-castellon-v1` regressions. Do not modify model equations or update goldens to make a deployment pass.

## CV / portfolio fallback

The static portfolio is intentionally separate from the technical app. It contains no optimizer or runtime calculations and should remain available even when Streamlit is sleeping.

Expected static URL after GitHub Pages is enabled for this repository:

`https://marcosbeltransev-design.github.io/optidecarb/`

The landing links back to the live Streamlit app, GitHub, the Castellón case and methodology.

## Verified public state — 2026-09-24

The public Streamlit URL opened as a visitor on App 1.3.2 / Model 0.3.0. A fresh
8,760-hour optimization of ceramic-castellon-v1 completed: PV 2.972 MWp,
battery 0 MWh, electrical CO2 reduction 30.4%, annualized cost about EUR 880k.
No reboot, dependency update or rebuild marker was needed. This observation
does not establish the cause of any earlier outage.

Main 99b374d6c8408f6d6769c74aeb327314e0a97d33 passed CI run 34265883626:
compile, both dataset reproducibility checks, 112 unit tests, 14 non-Streamlit
integration tests, Streamlit AppTest and all four isolated regression suites.
PR #6 was already merged. PR #8 was reviewed and merged after its complete CI
run 34266263957 passed; it only changes the Pages workflow.

The public portfolio returned 404: "There isn't a GitHub Pages site here."
The failed deployment run 34265883572 reported:
"Create Pages site failed. Error: Resource not accessible by integration".
The Actions token could not perform initial Pages enablement. A green skipped
Pages workflow is NOT proof that the portfolio is published.

### Complete initial Pages enablement

1. Sign in as a repository administrator.
2. Open repository Settings -> Pages -> Build and deployment.
3. Set Source to GitHub Actions.
4. Open Actions -> Deploy portfolio fallback -> Run workflow on main.
5. Inspect the completed deployment and open the public portfolio URL as a visitor.
6. Only after that public check, use the portfolio URL as the primary CV link.

Until that check passes, the repository README is an independent static project
reference; do not advertise the Pages URL as live.

### Verify the deployed runtime

In authenticated Streamlit Community Cloud, open OptiDecarb's settings and logs.
Record the actual repository, branch, entrypoint and Python version before changing
them. The repository configuration above is the intended configuration, not a
substitute for observing Cloud settings. Preserve the optidecarb subdomain.

### Installed-site access on Windows

Edge: Settings and more -> More tools -> Apps -> Install this site as an app.
In edge://apps, open Details for OptiDecarb and choose Pin to taskbar.
Chrome: More -> Cast, save, and share -> Install page as app.
After opening it, right-click its Windows taskbar icon -> Pin to taskbar.
This is an online browser-installed site, not a new offline PWA.
