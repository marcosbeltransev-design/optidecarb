"""Run the hand-checkable Student Learning Lab examples without Streamlit."""
from __future__ import annotations

from industrial_energy_lab.learning import (
    battery_duration_hours,
    co2_from_grid_energy_tco2,
    crf_learning_example,
    energy_from_power,
    three_hour_battery_lab,
)


def main() -> None:
    print("OptiDecarb — Student examples")
    print(f"5 MW × 3 h = {energy_from_power(5, 3):.1f} MWh")
    print(f"4 MWh / 2 MW = {battery_duration_hours(4, 2):.1f} h")
    print(f"180 kgCO2/MWh × 1,000 MWh = {co2_from_grid_energy_tco2(1000, 180):.1f} tCO2")
    crf = crf_learning_example(0.05, 25, 1_000_000)
    print(f"CRF(5%, 25 y) = {crf['crf']:.5f} 1/year")
    print(f"€1,000,000 equivalent annual CAPEX = €{crf['annualized_capex_eur']:,.0f}/year")
    print("\nThree-hour battery lab:")
    print(three_hour_battery_lab()[[
        "load_kwh", "pv_generation_kwh", "battery_charge_kwh", "battery_discharge_kwh",
        "soc_kwh", "grid_import_kwh", "battery_losses_kwh",
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
