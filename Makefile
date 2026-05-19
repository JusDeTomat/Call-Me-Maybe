UV				= uv
V_PYTHON		= $(UV) run python
V_PIP			= $(UV) pip
MAIN			= src/__main__.py
VENV			= .venv
SRC 			= src

MYPY_FLAGS		= --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
DEPENDENCIES	= pytest flake8 mypy pydantic
FLAKE			= $(V_PYTHON) -m flake8
MYPY			= $(V_PYTHON) -m mypy

all: run

$(VENV):
	$(UV) venv

run: install
	$(V_PYTHON) -m src

install: $(VENV)
	$(V_PIP) install torch --index-url https://download.pytorch.org/whl/cpu
	$(V_PIP) install $(DEPENDENCIES)


debug: install
	$(V_PYTHON) -m pdb $(MAIN)

clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache .pytest_cache
	rm -rf data/output/

lint: install
	$(FLAKE) $(SRC)
	$(MYPY) $(MYPY_FLAGS) $(SRC)

lint-strict: install
	$(FLAKE) '$(SRC)'
	$(MYPY) $(MYPY_FLAGS) --strict '$(SRC)'

.PHONY: install run debug clean lint lint-strict