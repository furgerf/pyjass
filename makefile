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
GT=
PID=
UUID=$(shell uuidgen)
TARGET=run
EID:=$(TARGET)-$(UUID)
THIS_EVAL_DIR:=$(EVAL_DIR)/$(EID)
EVAL_LOG:=$(THIS_EVAL_DIR)/evaluation_$(shell date '+%Y%m%d_%H%M%S').log

lc: SCORES := $(THIS_EVAL_DIR)/scores.csv
lc: CURVE_SCORES := $(THIS_EVAL_DIR)/curve_scores.csv
lint: LINT_FILES:=src/*.py test/*.py
combine-round-results: NAME=
combine-round-results: THIS_EVAL_DIR := $(EVAL_DIR)/$(NAME)-combined
create-multi-regressor: MULTI_NAME=
create-multi-regressor: REG_NAMES=

.PHONY: run train eval store link-model online-round offline-round lc lint test explore wait \
	20-round 21-round 22-round 23-round 24-round 25-round 26-round 27-round \
	combine-round-results create-multi-regressor \
	pause resume kill remove-eval archive archive-unnamed freeze install uninstall

run:
ifndef MOD
	$(error Must specify model)
endif
ifdef PID
	@$(MAKE) --no-print-directory wait
endif
	@mkdir -p $(MODELS_DIR)/$(MOD)
	@mkdir -p $(THIS_EVAL_DIR)
	$(UNBUF) $(NICE) $(BIN)/python src/run.py --eid=$(EID) --model=$(MOD) --regressor=$(REG) \
		--force-game-type=$(GT) $(ARGS) 2>&1 | tee $(EVAL_LOG); [ $${PIPESTATUS[0]} -eq 0 ]
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
	@# NOTE: batchsize/trainingint: maximum (regarding memory); chkres = batchsize; chkint/logint selected freely
	@$(MAKE) --no-print-directory run ARGS='--seed --procs --team1=mlp --team2=baseline --online --store-scores \
		--hands=4e6 --batchsize=2.5e4 --chkres=2.5e4 --chkint=2e5 --trainingint=1e5 --logint=2e5 $(ARGS)' TARGET=$@

store:
	@# NOTE: batchsize/trainingint: maximum (regarding memory); checkpoints "disabled"; logint selected freely
	@mkdir -p $(MODELS_DIR)/$(MOD)
	@$(MAKE) --no-print-directory run ARGS='--seed --procs=4 --team1=baseline --team2=baseline --store-data \
		--hands=4e6 --batchsize=2.5e4 --chkint=1e6 --trainingint=1e5 --logint=2e5 $(ARGS)' TARGET=$@

eval:
	@# NOTE: batchsize = logint / procs - doesn't keep any data; checkpoints "disabled"; logint selected freely
	@$(MAKE) --no-print-directory run ARGS='--seed --procs --team1=mlp --team2=baseline \
		--hands=5e5 --batchsize=5e4 --chkint=5e5 --logint=1e5 $(ARGS)' TARGET=$@

online-round:
ifndef MOD
	$(error Must specify model)
endif
ifndef ENC
	$(error Must specify encoding)
endif
ifndef NAME
	$(error Must specify regressor name)
endif
ifndef OTHER_NAME
	$(error Must specify name of other regressor)
endif
ifndef ROUND
	$(error Must specify round number)
endif
ifdef PID
	@$(MAKE) --no-print-directory wait
endif
	@# NOTE: this relies that the default hands for train is 4M and that it isn't overwritten
	@# TODO: move hands to a variable
	$(MAKE) --no-print-directory train PID= EID=$(MOD)-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl \
		ARGS='--load-training-file=$(ENC)-4m-$(OTHER_NAME)-round-$(shell echo $(ROUND)-1 | bc).bin \
		--store-data --store-training-file=$(ENC)-4m-$(NAME)-round-$(ROUND).bin \
		--store-game-type-file=$(ENC)-4m-$(NAME)-round-$(ROUND)-game-type-decisions.bin $(ARGS)' TARGET=$@
	$(MAKE) --no-print-directory link-model PID= EID=$(MOD)-$(NAME)-round-$(ROUND) REG=$(NAME)-round-$(ROUND).pkl TARGET=$@

offline-round:
ifndef MOD
	$(error Must specify model)
endif
ifndef ENC
	$(error Must specify encoding)
endif
ifndef NAME
	$(error Must specify regressor name)
endif
ifndef ROUND
	$(error Must specify round number)
endif
ifdef PID
	@$(MAKE) --no-print-directory wait
endif
	$(MAKE) --no-print-directory eval PID= EID=$(MOD)-$(NAME)-round-$(ROUND) REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl \
		ARGS='--load-training-file=$(ENC)-4m-combined-round-$(ROUND).bin $(ARGS)' TARGET=$@
	$(MAKE) --no-print-directory link-model PID= EID=$(MOD)-$(NAME)-round-$(ROUND) REG=$(NAME)-round-$(ROUND).pkl TARGET=$@

20-round:
ifeq ($(NAME), 3x100)
	@$(MAKE) --no-print-directory online-round MOD=20 ENC=13 OTHER_NAME=4x100 \
		GT=obenabe ARGS='--hands=2e6' TARGET=$@
else ifeq ($(NAME), 4x100)
	@$(MAKE) --no-print-directory online-round MOD=20 ENC=13 OTHER_NAME=3x100 \
		GT=obenabe ARGS='--hands=2e6' TARGET=$@
else ifeq ($(NAME), 5x100)
	@$(MAKE) --no-print-directory offline-round MOD=20 ENC=13 GT=obenabe TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

21-round:
ifeq ($(NAME), 4x100)
	@$(MAKE) --no-print-directory online-round MOD=21 ENC=14 OTHER_NAME=5x100 \
		GT=obenabe ARGS='--hands=2e6' TARGET=$@
else ifeq ($(NAME), 5x100)
	@$(MAKE) --no-print-directory online-round MOD=21 ENC=14 OTHER_NAME=4x100 \
		GT=obenabe ARGS='--hands=2e6' TARGET=$@
else ifeq ($(NAME), 6x100)
	@$(MAKE) --no-print-directory offline-round MOD=21 ENC=14 GT=obenabe TARGET=$@
else ifeq ($(NAME), 5x100-offline)
	@$(MAKE) --no-print-directory offline-round MOD=21 ENC=14 GT=obenabe TARGET=$@
else ifeq ($(NAME), 6x100-online-only)
	@$(MAKE) --no-print-directory train MOD=21 EID=21-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl GT=obenabe TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

22-round:
ifeq ($(NAME), 6x100)
	@$(MAKE) --no-print-directory online-round MOD=22 ENC=15 OTHER_NAME=7x100 \
		GT=obenabe ARGS='--hands=2e6' TARGET=$@
else ifeq ($(NAME), 7x100)
	@$(MAKE) --no-print-directory online-round MOD=22 ENC=15 OTHER_NAME=6x100 \
		GT=obenabe ARGS='--hands=2e6' TARGET=$@
else ifeq ($(NAME), 6x100-own-data)
	@$(MAKE) --no-print-directory online-round MOD=22 ENC=15 OTHER_NAME=6x100 GT=obenabe \
		ARGS='--no-store-data --store-training-file= --load-training-file=15-2m-6x100-round-$(ROUND).bin --hands=2e6' TARGET=$@
else ifeq ($(NAME), 4x200)
	@$(MAKE) --no-print-directory train MOD=22 EID=22-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl GT=obenabe TARGET=$@
	@$(MAKE) --no-print-directory link-model PID= MOD=22 EID=22-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(ROUND).pkl TARGET=$@
else ifeq ($(NAME), 300-200-300)
	@$(MAKE) --no-print-directory train MOD=22 EID=22-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl GT=obenabe TARGET=$@
	@$(MAKE) --no-print-directory link-model PID= MOD=22 EID=22-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(ROUND).pkl TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

23-round:
ifeq ($(NAME), 6x100)
	@$(MAKE) --no-print-directory online-round MOD=23 ENC=16 OTHER_NAME=7x100 GT=obenabe TARGET=$@
else ifeq ($(NAME), 7x100)
	@$(MAKE) --no-print-directory online-round MOD=23 ENC=16 OTHER_NAME=6x100 GT=obenabe TARGET=$@
else ifeq ($(NAME), 4x200)
	@$(MAKE) --no-print-directory train MOD=23 EID=23-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl GT=obenabe ARGS='--hands=8e6' TARGET=$@
	@$(MAKE) --no-print-directory link-model PID= MOD=23 EID=23-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(ROUND).pkl TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

24-round:
ifeq ($(NAME), 6x100)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=7x100 GT=obenabe TARGET=$@
else ifeq ($(NAME), 7x100)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=6x100 GT=obenabe TARGET=$@
else ifeq ($(NAME), 8x100)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=9x100 GT=obenabe TARGET=$@
else ifeq ($(NAME), 9x100)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=8x100 GT=obenabe TARGET=$@
else ifeq ($(NAME), 4x200)
	@$(MAKE) --no-print-directory train MOD=24 EID=24-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl GT=obenabe ARGS='--hands=8e6' TARGET=$@
	@$(MAKE) --no-print-directory link-model PID= MOD=24 EID=24-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(ROUND).pkl TARGET=$@
else ifeq ($(NAME), 4x200-unnenufe)
	@$(MAKE) --no-print-directory train MOD=24 EID=24-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(shell echo $(ROUND)-1 | bc).pkl GT=unnenufe ARGS='--hands=8e6' TARGET=$@
	@$(MAKE) --no-print-directory link-model PID= MOD=24 EID=24-$(NAME)-round-$(ROUND) \
		REG=$(NAME)-round-$(ROUND).pkl TARGET=$@
else ifeq ($(NAME), 5x200)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=3x300 GT=obenabe TARGET=$@
else ifeq ($(NAME), 3x300)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=5x200 GT=obenabe TARGET=$@
else ifeq ($(NAME), 5x200-spades)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=3x300-spades GT=trump_spades TARGET=$@
else ifeq ($(NAME), 3x300-spades)
	@$(MAKE) --no-print-directory online-round MOD=24 ENC=17 OTHER_NAME=5x200-spades GT=trump_spades TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

25-round:
ifeq ($(NAME), 10x100-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=25 ENC=18 OTHER_NAME=4x200-obenabe GT=obenabe TARGET=$@
else ifeq ($(NAME), 4x200-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=25 ENC=18 OTHER_NAME=10x100-obenabe GT=obenabe TARGET=$@
else ifeq ($(NAME), 5x200-spades)
	@$(MAKE) --no-print-directory online-round MOD=25 ENC=18 OTHER_NAME=3x300-spades GT=trump_spades TARGET=$@
else ifeq ($(NAME), 3x300-spades)
	@$(MAKE) --no-print-directory online-round MOD=25 ENC=18 OTHER_NAME=5x200-spades GT=trump_spades TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

26-round:
ifeq ($(NAME), 10x100-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=26 ENC=19 OTHER_NAME=4x200-obenabe GT=obenabe TARGET=$@
else ifeq ($(NAME), 4x200-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=26 ENC=19 OTHER_NAME=10x100-obenabe GT=obenabe TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

27-round:
ifeq ($(NAME), 10x100-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=27 ENC=20 OTHER_NAME=4x200-obenabe GT=obenabe TARGET=$@
else ifeq ($(NAME), 4x200-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=27 ENC=20 OTHER_NAME=10x100-obenabe GT=obenabe TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

28-round:
ifeq ($(NAME), 5x200-spades)
	@$(MAKE) --no-print-directory online-round MOD=28 ENC=21 OTHER_NAME=3x300-spades GT=trump_spades TARGET=$@
else ifeq ($(NAME), 3x300-spades)
	@$(MAKE) --no-print-directory online-round MOD=28 ENC=21 OTHER_NAME=5x200-spades GT=trump_spades TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

29-round:
ifeq ($(NAME), 5x200-spades)
	@$(MAKE) --no-print-directory online-round MOD=29 ENC=22 OTHER_NAME=3x300-spades GT=trump_spades TARGET=$@
else ifeq ($(NAME), 3x300-spades)
	@$(MAKE) --no-print-directory online-round MOD=29 ENC=22 OTHER_NAME=5x200-spades GT=trump_spades TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

30-round:
ifeq ($(NAME), 5x200-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=30 ENC=23 OTHER_NAME=3x300-obenabe GT=obenabe TARGET=$@
else ifeq ($(NAME), 3x300-obenabe)
	@$(MAKE) --no-print-directory online-round MOD=30 ENC=23 OTHER_NAME=5x200-obenabe GT=obenabe TARGET=$@
else ifeq ($(NAME), 5x200-spades)
	@$(MAKE) --no-print-directory online-round MOD=30 ENC=23 OTHER_NAME=3x300-spades GT=trump_spades TARGET=$@
else ifeq ($(NAME), 3x300-spades)
	@$(MAKE) --no-print-directory online-round MOD=30 ENC=23 OTHER_NAME=5x200-spades GT=trump_spades TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

31-round:
ifeq ($(NAME), 5x200-spades)
	@$(MAKE) --no-print-directory online-round MOD=31 ENC=24 OTHER_NAME=3x300-spades GT=trump_spades TARGET=$@
else ifeq ($(NAME), 3x300-spades)
	@$(MAKE) --no-print-directory online-round MOD=31 ENC=24 OTHER_NAME=5x200-spades GT=trump_spades TARGET=$@
else
	$(error Unknown name: $(NAME))
endif

# TODO: use better locale
combine-round-results:
ifndef NAME
	$(error Must specify name of the evaluation)
endif
	$(info Writing combined results to $(THIS_EVAL_DIR))
	@mkdir -p $(THIS_EVAL_DIR)
	@# loss
	@[ -f $(THIS_EVAL_DIR)/loss.csv ] && rm $(THIS_EVAL_DIR)/loss.csv || true
	@for eval in $(EVAL_DIR)/$(NAME)-round-*; do \
		[ ! -f $(THIS_EVAL_DIR)/loss.csv ] && head -n 1 $$eval/loss.csv > $(THIS_EVAL_DIR)/loss.csv; \
		[ -f $$eval/loss.csv ] \
			&& tail -n +3 $$eval/loss.csv >> $(THIS_EVAL_DIR)/loss.csv && echo "Processing $$eval/loss.csv" \
			|| echo "-> $$eval contains no loss file!"; \
	done
	@# scores
	@[ -f $(THIS_EVAL_DIR)/scores.csv ] && rm $(THIS_EVAL_DIR)/scores.csv || true
	@for eval in $(EVAL_DIR)/$(NAME)-round-*; do \
		[ -f $$eval/scores.csv -a ! -f $(THIS_EVAL_DIR)/scores.csv ] && head -n 1 $$eval/scores.csv > $(THIS_EVAL_DIR)/scores.csv; \
		[ -f $$eval/scores.csv ] \
			&& tail -n +3 $$eval/scores.csv >> $(THIS_EVAL_DIR)/scores.csv && echo "Processing $$eval/scores.csv" \
			|| echo "-> $$eval contains no scores file!"; \
	done

link-model:
ifndef MOD
	$(error Must specify model)
endif
ifndef REG
	$(error Must specify model name for symlink)
endif
ifdef PID
	@$(MAKE) --no-print-directory wait
endif
	@pushd $(MODELS_DIR)/$(MOD) > /dev/null; \
	if [ $$(ls -l ../../$(THIS_EVAL_DIR)/*.pkl | wc -l) -eq 1 ]; then \
		LINK_TARGETS=$$(ls ../../$(THIS_EVAL_DIR)/*.pkl); \
	else \
		LINK_TARGETS=$$(ls ../../$(THIS_EVAL_DIR)/final-*.pkl); \
	fi; \
	for reg in $$LINK_TARGETS; do \
		ln -s$(FORCE) ../../$(THIS_EVAL_DIR)/$$(basename $$reg) $(REG) && echo "Created symlink: $$(ls -l $(REG) | cut -d' ' -f 9-)" || \
			{ echo "FAILURE" && popd > /dev/null && exit 1; }; \
		test -f $(REG) || { echo "Created broken symlink!" && exit 1; }; \
	done; \
	popd > /dev/null

lc:
ifndef MOD
	$(error Must specify model)
endif
ifndef EID
	$(error Must specify evaluation ID)
endif
ifdef PID
	@$(MAKE) --no-print-directory wait
endif
	@> $(CURVE_SCORES)
	@count=0; \
	time (for reg in $(THIS_EVAL_DIR)/p1_MLPRegressor_*.pkl; do \
		reg_path=../../$(THIS_EVAL_DIR)/$$(basename $$reg); \
		echo "Processing $$reg..."; \
		# we want to write another evaluation to this directory \
		[ -f $(THIS_EVAL_DIR)/has-eval ] && rm $(THIS_EVAL_DIR)/has-eval; \
		# about the seed: always play the "same" game but do a different one than what was trained \
		$(UNBUF) $(NICE) $(BIN)/python src/run.py --eid=$(EID) --model=$(MOD) --seed2 --procs --store-scores \
			--hands=1e5 --chkint=1e5 --logint=1e5 --chkres=5e4 --batchsize=5e4 \
			--team1=mlp --regressor=$$reg_path $(ARGS) 2>&1 \
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
	done)

create-multi-regressor:
ifndef MOD
	$(error Must specify model)
endif
ifndef MULTI_NAME
	$(error Must name for multi-regressor)
endif
ifndef REG_NAMES
	$(error Must names of regressors to combine)
endif
	$(BIN)/python src/multi_reg_combiner.py --model=$(MOD) --multi-regressor-name=$(MULTI_NAME) --regressors=$(REG_NAMES)

lint:
	@PYTHONPATH="$$PYTHONPATH:src/" $(BIN)/pylint $(LINT_FILES) --ignore=venv/ -f colorized -r n \
		--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"

explore:
	$(BIN)/ipython --no-banner --no-confirm-exit -i src/explore.py

test:
	@PYTHONPATH="$$PYTHONPATH:src/" $(BIN)/python -m unittest discover test/ --locals --failfast

wait:
ifndef PID
	$(error Must specify pid)
endif
	$(info Waiting for process $(PID)...)
	@while [ -d /proc/$$PID ]; do \
		sleep 60; \
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
	@[ $$(command -v python3) ] || (echo 'python 3 is missing'; exit 1)
	@(( $$(readlink $$(which python3) | cut -d. -f2) >= 5 )) || (echo 'python >= 3.5 is required'; exit 1)
	virtualenv -p python3 $(VENV)

freeze: venv
	$(BIN)/pip freeze | grep -v "pkg-resources" > requirements.txt

install: venv
	$(BIN)/pip install -r requirements.txt
	mkdir -p $(DIRECTORIES)

uninstall:
	rm -rf $(VENV)

