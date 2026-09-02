PYTHON ?= python3
PORT ?= 4181
PDF_SOURCE ?= $(firstword $(wildcard *.pdf))

.PHONY: build check serve test

build:
	@test -n "$(PDF_SOURCE)" || (echo "PDF_SOURCE를 지정해주세요."; exit 1)
	$(PYTHON) parse_supervision_pdf.py --source "$(PDF_SOURCE)"

check:
	$(PYTHON) check_anomalies.py

serve:
	$(PYTHON) -m http.server $(PORT)

test:
	$(PYTHON) -m compileall -q parse_june4.py parse_supervision_pdf.py check_anomalies.py
	node --check script.js
	node --check schedule_data.js
	$(MAKE) check
