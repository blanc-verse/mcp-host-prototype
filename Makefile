.PHONY: dev, test

dev:
	uv run python -m chainlit run main.py -w

test: 
	adk web ./clients