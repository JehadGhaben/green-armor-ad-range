.PHONY: doctor up down reset status shell score test smoke
PYTHON ?= python3

doctor:
	$(PYTHON) armorlab.py doctor
up:
	$(PYTHON) armorlab.py up
down:
	$(PYTHON) armorlab.py down
reset:
	$(PYTHON) armorlab.py reset --yes
status:
	$(PYTHON) armorlab.py status
shell:
	$(PYTHON) armorlab.py shell
score:
	$(PYTHON) armorlab.py score
test:
	$(PYTHON) -m unittest discover -s tests -v
smoke:
	$(PYTHON) scripts/smoke-test.py
