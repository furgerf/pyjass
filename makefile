VENV=venv
BIN=$(VENV)/bin
NICE=nice -n 19
UNBUF=unbuffer
SHELL=/bin/bash

DATA_DIR=data
MODELS_DIR=models
EVAL_DIR=evaluations
OLD_EVAL_DIR=old-evaluations
DIRECTORIES=$(DATA_DIR) $(MODELS_DIR) $(EVAL_DIR) $(OLD_EVAL_DIR)

REGRESSORS=SGDRegressor MLPRegressor

# TODO
# - Special archiving for (tracked) evaluations

ARGS=
MOD=
REG=
UUID=$(shell uuidgen)
TARGET=run
EID:=$(TARGET)-$(UUID)
THIS_EVAL_DIR:=$(EVAL_DIR)/$(EID)
EVAL_LOG:=$(THIS_EVAL_DIR)/evaluation_$(shell date '+%Y%m%d_%H%M%S').log

lc: SCORES := $(THIS_EVAL_DIR)/scores.csv
lc: CURVE_SCORES := $(THIS_EVAL_DIR)/curve_scores.csv
lint: LINT_FILES:=src/*.py
wait: PID=

.PHONY: run train eval store store-simple initial-training initial-training-simple \
	link-model lc lint explore wait \
	pause resume kill remove-eval archive archive-unnamed venv freeze install uninstall

run:
	mkdir -p $(THIS_EVAL_DIR)
ifndef MOD
	$(error Must specify model)
endif
	$(UNBUF) $(NICE) $(BIN)/python src/run.py --eid=$(EID) --model=$(MOD) --regressor=$(REG) $(ARGS) 2>&1 \
		| tee $(EVAL_LOG); [ $${PIPESTATUS[0]} -eq 0 ]
	@for reg in $(REGRESSORS); do \
		unset -v latest; \
		for pkl in $(THIS_EVAL_DIR)/p*_"$$reg"_*.pkl; do \
			[[ $$pkl -nt $$latest ]] && latest=$$pkl; \
		done; \
		[ -z "$$latest" ] && continue; \
		ln -s $$(basename $$latest) $(THIS_EVAL_DIR)/final-$$reg.pkl; \
		echo "Created symlink for final $$reg: $$(ls -l $(THIS_EVAL_DIR)/final-$$reg.pkl | cut -d' ' -f 10-)"; \
	done

train:
	@$(MAKE) run ARGS='--seed --procs --team1=mlp --online --hands=1e7 \
		--trainingint=1e5 --chkint=2e5 --logint=5e5 --batchsize=1e4 $(ARGS)' TARGET=$@

eval:
	@# NOTE: batch size = hands / logint / procs - doesn't keep any data
	@$(MAKE) run ARGS='--seed --procs --team1=mlp --team1-best --hands=5e5 \
		--trainingint=5e5 --chkint=5e5 --logint=1e5 --batchsize=5e4 $(ARGS)' TARGET=$@

store:
	mkdir -p $(MODELS_DIR)/$(MOD)
	@$(MAKE) run ARGS='--seed --procs --team1=mlp --team1-best --hands=2e6 --store-data \
		--trainingint=1e5 --chkint=2e6 --logint=5e5 --batchsize=1e4 $(ARGS)' TARGET=$@

store-simple:
	mkdir -p $(MODELS_DIR)/$(MOD)
	@$(MAKE) run ARGS='--seed --procs --store-data --hands=1e6 \
		--trainingint=1e5 --chkint=1e6 --logint=1e5 --batchsize=1e4 $(ARGS)' TARGET=$@

initial-training:
	@$(MAKE) run ARGS='--seed --procs --team1=mlp --online --hands=8e6 \
		--trainingint=1e5 --chkint=2e5 --logint=5e5 --batchsize=1e4 $(ARGS)' TARGET=$@

initial-training-simple:
	@$(MAKE) run ARGS='--seed --procs --team1=mlp --online --hands=9e6 \
		--trainingint=1e5 --chkint=2e5 --logint=5e5 --batchsize=1e4 $(ARGS)' TARGET=$@

link-model:
ifndef MOD
	$(error Must specify model)
endif
ifndef REG
	$(error Must specify model name for symlink)
endif
	@pushd $(MODELS_DIR)/$(MOD) > /dev/null; \
	for reg in $(THIS_EVAL_DIR)/final-*.pkl; do \
		ln -s ../../$(THIS_EVAL_DIR)/$$(basename $$reg) $(REG) && echo "Created symlink: $$(ls -l $(REG) | cut -d' ' -f 9-)" || true; \
	done; \
	popd > /dev/null

lc:
ifndef MOD
	$(error Must specify model)
endif
ifndef EID
	$(error Must specify evaluation ID)
endif
	@> $(CURVE_SCORES)
	@count=0; \
	for reg in $(THIS_EVAL_DIR)/p1_MLPRegressor_*.pkl; do \
		reg_path=../../$(THIS_EVAL_DIR)/$$(basename $$reg); \
		echo "Processing $$reg..."; \
		# we want to write another evaluation to this directory \
		[ -f $(THIS_EVAL_DIR)/has-eval ] && rm $(THIS_EVAL_DIR)/has-eval; \
		# about the seed: always play the "same" game but do a different one than what was trained \
		$(UNBUF) $(NICE) $(BIN)/python src/run.py --eid=$(EID) --model=$(MOD) --seed2 --procs --store-scores \
			--hands=1e5 --chkint=1e5 --logint=1e5 --chkres=5e4 --batchsize=5e4 \
			--team1=mlp --team1-best --regressor=$$reg_path $(ARGS) 2>&1 \
			| tee $(THIS_EVAL_DIR)/curve_$$(basename $$reg).log; [ $${PIPESTATUS[0]} -eq 0 ]; \
		# fail if we don't have exactly 3 lines in the scores file (header + 2 batch results) \
		[[ $$(wc -l < $(SCORES)) != 3 ]] && echo "Unexpected number of lines in score file!" && exit 1; \
		# if we've just run the first evaluation, copy the header from the scores file \
		[ -s $(CURVE_SCORES) ] || head -n 1 $(SCORES) > $(CURVE_SCORES); \
		# manually keep track of the "number of played hands" \
		count=$$(($$count+$$(tail -n 1 $(SCORES) | cut -d, -f1))); \
		echo -n "$$count," >> $(CURVE_SCORES); \
		# append sum of the two batch scores\
		tail -n +2 $(SCORES) | awk -F, 'NR%2 { split($$0, a); next } { for (i=2; i<NF-1; i++) printf "%d,", a[i]+$$i; for (i=NF-1; i<NF; i++) printf "%d,\n", $$i }' >> $(CURVE_SCORES); \
	done

lint:
	@$(BIN)/pylint $(LINT_FILES) --ignore=venv/ -f colorized -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"

explore:
	$(BIN)/ipython --no-banner --no-confirm-exit -i src/explore.py

wait:
ifndef PID
	$(error Must specify pid)
endif
	@while [ -d /proc/$$PID ]; do \
		sleep 30; \
	done

pause:
ifndef PID
	$(error Must specify pid)
endif
	kill -STOP $(PID) $$(ps -o pid= --ppid $(PID))

resume:
ifndef PID
	$(error Must specify pid)
endif
	kill -CONT $(PID) $$(ps -o pid= --ppid $(PID))

kill:
ifndef PID
	$(error Must specify pid)
endif
	kill -TERM $(PID) $$(ps -o pid= --ppid $(PID))

clean-eval:
ifndef EID
	$(error Must specify evaluation ID)
endif
	ls -l $(THIS_EVAL_DIR)
	rm -r $(THIS_EVAL_DIR)

archive-unnamed:
	for eval in $(EVAL_DIR)/*; do \
		if [[ $$(basename $$eval) =~ ^\{?([[:alpha:]-]+-)?[[:xdigit:]]{8}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{12}\}?$$ ]]; then \
			tar -czf $$eval.tar.gz -C $(EVAL_DIR) $$(basename $$eval); \
			rm -r $$eval; \
			mv $$eval.tar.gz $(OLD_EVAL_DIR); \
			echo "archived $$(basename $$eval)"; \
		fi; \
	done

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

uninstall:
	rm -rf $(VENV)

