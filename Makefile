PYTHON=.venv/Scripts/python.exe
MANAGE=$(PYTHON) manage.py

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

test:
	.venv/Scripts/pytest.exe

seed:
	$(MANAGE) seed_demo

shell:
	$(MANAGE) shell

static:
	$(MANAGE) collectstatic --noinput
