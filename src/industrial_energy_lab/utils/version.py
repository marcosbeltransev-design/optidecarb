"""Version identifiers kept separate from package release numbering."""

# Current physical model release.
MODEL_VERSION = "0.2.0"
DATASET_VERSION = "demo-v1"
SCENARIO_CASE_VERSION = "golden-v2"

# Frozen identifiers retained so Iteration 1's golden regression remains historical.
BASELINE_MODEL_VERSION = "0.1.0"
BASELINE_CASE_VERSION = "golden-v1"

# Backward-compatible alias for code that needs the current scenario case.
CASE_VERSION = SCENARIO_CASE_VERSION
