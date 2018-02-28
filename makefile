VENV=venv
BIN=$(VENV)/bin
NICE=nice -n 19
UNBUF=unbuffer

DATA_DIR=data
MODELS_DIR=models
EVAL_DIR=evaluations
OLD_EVAL_DIR=old-evaluations
DIRECTORIES=$(DATA_DIR) $(MODELS_DIR) $(EVAL_DIR) $(OLD_EVAL_DIR)

# TODO: PID file for STOP/CONT

run:
ifndef EID
	$(eval EID := $(shell uuidgen))
endif
	$(eval EID_ARG := --eid=$(EID))
	$(eval THIS_EVAL_DIR := $(EVAL_DIR)/$(EID))
	$(eval EVAL_LOG := $(THIS_EVAL_DIR)/evaluation_$(shell date '+%Y%m%d_%H%M%S').log)
	mkdir -p $(THIS_EVAL_DIR)
	$(eval MOD_ARG := --model=$(MOD))
	$(UNBUF) $(NICE) $(BIN)/python src/run.py $(EID_ARG) $(MOD_ARG) $(ARGS) 2>&1 | tee $(EVAL_LOG)

run-args:
	$(MAKE) run --args # placeholder for "simplified" invocation

lint:
	$(eval LINT_FILES := src/*.py)
	$(BIN)/pylint $(LINT_FILES) --ignore=venv/ -f colorized -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"

explore:
	$(BIN)/ipython -m src.explore -i


archive:
	for eval in $(EVAL_DIR)/*; do \
		tar -czf $$eval.tar.gz -C $(EVAL_DIR) $$(basename $$eval); \
		rm -r $$eval; \
		mv $$eval.tar.gz $(OLD_EVAL_DIR); \
		echo "archived $$(basename $$eval)"; \
	done


venv:
	virtualenv -p python3 $(VENV)

freeze: venv
	$(BIN)/pip freeze | grep -v "pkg-resources" > requirements.txt

install: venv
	$(BIN)/pip install -r requirements.txt
	mkdir -p $(DIRECTORIES)


clean:
	find . -type f -name '*.pyc' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +

uninstall:
	rm -rf $(VENV)

