VENV=venv
BIN=$(VENV)/bin
NICE=nice -n 19
UNBUF=unbuffer

DATA_DIR=data
MODELS_DIR=models
EVAL_DIR=evaluations
OLD_EVAL_DIR=old-evaluations
CURRENT_MODEL=current-model
DIRECTORIES=$(DATA_DIR) $(MODELS_DIR) $(EVAL_DIR) $(OLD_EVAL_DIR)

run:
ifndef EID
	$(eval EID := $(shell uuidgen))
endif
	$(eval EID_ARG := --eid=$(EID))
	$(eval THIS_EVAL_DIR := $(EVAL_DIR)/$(EID))
	$(eval EVAL_LOG := $(THIS_EVAL_DIR)/evaluation_$(shell date '+%Y%m%d_%H%M%S').log)
	mkdir -p $(THIS_EVAL_DIR)
	$(UNBUF) $(NICE) $(BIN)/python run.py $(EID_ARG) $(ARGS) 2>&1 | tee $(EVAL_LOG)

run-args:
	$(MAKE) run --args # placeholder for "simplified" invocation

lint:
	$(eval LINT_FILES := *.py models/)
	$(BIN)/pylint $(LINT_FILES) --ignore=venv/ -f colorized -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"

explore:
	$(BIN)/ipython -m explore -i


archive:
	for eval in $(EVAL_DIR)/*; do \
		tar -czf $$eval.tar.gz -C $(EVAL_DIR) $$(basename $$eval); \
		rm -r $$eval; \
		mv $$eval.tar.gz $(OLD_EVAL_DIR); \
		echo "archived $$(basename $$eval)"; \
	done

select-model: unselect-model
	ln -s $(MODELS_DIR)/$(MOD) $(CURRENT_MODEL)
	ls -l $(CURRENT_MODEL)

unselect-model:
	test -L $(CURRENT_MODEL) && unlink $(CURRENT_MODEL) || exit 0


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

