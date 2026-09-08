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
