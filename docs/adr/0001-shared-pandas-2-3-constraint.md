# Use a Shared Pandas 2.3 Constraint Across Agent Repos

`data-analyst-agent` composes `data-cleaning-agent` and `eda-workflow` in the same Python environment, and `data-cleaning-agent` depends on stable `datacompy`, whose stable releases currently cap pandas at `<=2.3.3`. We use `pandas>=2.3.0,<=2.3.3` across the three projects and keep the analyst repo's uv override aligned with that constraint until stable `datacompy` supports pandas 3.
