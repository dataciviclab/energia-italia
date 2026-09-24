# Energia Italia — Makefile
# Pipeline toolkit (dataset.yml) + script analitici.
TOOLKIT = toolkit

# --- Dataset del repo -------------------------------------------------------
DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)

# --- Run toolkit ------------------------------------------------------------

.PHONY: run
run:
	$(TOOLKIT) run --batch batch.txt

.PHONY: run-all
run-all:
	@find datasets -name dataset.yml | sort > batch.txt; \
	$(TOOLKIT) run --batch batch.txt

# --- Validazione config ------------------------------------------------------

.PHONY: check
check:
	@for f in $(DATASETS); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

# --- Script analitici -------------------------------------------------------

.PHONY: reconcile
reconcile:
	python3 scripts/reconcile.py

# --- Pipeline completa: toolkit + reconcile + test ---------------------------

.PHONY: all
all: run-all reconcile test

# --- Test --------------------------------------------------------------------

.PHONY: test
test:
	python3 -m pytest tests/ -v

# --- Registry ----------------------------------------------------------------

.PHONY: registry registry-write
registry:
	$(TOOLKIT) registry build --prefix energia_italia

registry-write:
	$(TOOLKIT) registry build --prefix energia_italia --write

# --- Pulizia -----------------------------------------------------------------

.PHONY: clean
clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
