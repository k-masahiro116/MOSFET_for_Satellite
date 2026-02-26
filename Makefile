.PHONY: all validate build plot analyze

all: validate build plot analyze

validate:
	uv run python src/01_validate_data.py

build:
	uv run python src/02_build_layer_timeseries.py

plot:
	uv run python src/03_plot_stacked_market.py

analyze:
	uv run python src/04_generate_analysis.py
