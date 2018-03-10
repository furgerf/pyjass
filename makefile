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
# - Target to clean eval directory by EID
# - Special archiving for (tracked) evaluations
# - PID file for STOP/CONT, targets to work with them

ARGS=
MOD=
UUID=$(shell uuidgen)
TARGET=run
EID:=$(TARGET)-$(UUID)
THIS_EVAL_DIR:=$(EVAL_DIR)/$(EID)
EVAL_LOG:=$(THIS_EVAL_DIR)/evaluation_$(shell date '+%Y%m%d_%H%M%S').log

learning-curve: SCORES := $(THIS_EVAL_DIR)/scores.csv
learning-curve: CURVE_SCORES := $(THIS_EVAL_DIR)/curve_scores.csv
lint: LINT_FILES:=src/*.py
wait: PID=

run:
	mkdir -p $(THIS_EVAL_DIR)
ifndef MOD
	$(error Must specify model)
endif
	$(UNBUF) $(NICE) $(BIN)/python src/run.py --eid=$(EID) --model=$(MOD) $(ARGS) 2>&1 \
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
		--trainingint=1e5 --chkint=5e5 --logint=5e5 --batchsize=1e3 $(ARGS)' TARGET=$@

eval:
	@# NOTE: batch size = hands / logint / procs
	@$(MAKE) run ARGS='--seed --procs --team1=mlp --team1-best --hands=5e5 \
		--trainingint=5e5 --chkint=5e5 --logint=1e5 --batchsize=5e4 $(ARGS)' TARGET=$@

store:
	# TODO

initial-training:
	# TODO

link-model:
ifndef MOD
	$(error Must specify model)
endif
ifndef MOD_NAME
	$(error Must specify model name for symlink)
endif
	@for reg in $(THIS_EVAL_DIR)/final-*.pkl; do \
		pushd $(MODELS_DIR)/$(MOD) > /dev/null; \
		ln -s ../../$(THIS_EVAL_DIR)/$$(basename $$reg) $(MOD_NAME); \
		popd > /dev/null; \
		echo "Created symlink: $$(ls -l $(MODELS_DIR)/$(MOD)/$(MOD_NAME) | cut -d' ' -f 9-)"; \
	done

learning-curve:
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
	$(BIN)/ipython -m src.explore -i

wait:
ifndef PID
	$(error Must specify pid)
endif
	@while [ -d /proc/$$PID ]; do \
		sleep 1; \
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

clean:
	find . -type f -name '*.pyc' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +

uninstall:
	rm -rf $(VENV)

