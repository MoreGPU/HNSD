.PHONY: venv install run clean

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python

venv:
	uv venv --python=3.12

install: venv
	uv pip install -e .

clean:
	rm -rf $(VENV_DIR) .uv
