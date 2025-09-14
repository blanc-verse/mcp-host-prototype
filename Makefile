.PHONY: dev, test

dev:
	uv run chainlit run main.py -w

test: 
	adk web ./clients