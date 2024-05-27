db: # Run Postgres
	docker run -d --rm \
	-p 5432:5432 \
	--name postgres \
	-e POSTGRES_USER=devUser \
	-e POSTGRES_PASSWORD=devPassword \
	-e POSTGRES_DB=library_db \
	-e TZ=Asia/Manila \
	-v $(PWD)/data:/var/lib/postgresql/data \
	postgres:16.3-alpine3.19

venv:
	`which python3` -m venv venv
	venv/bin/pip install -U pip pip-tools wheel --no-cache-dir

reqs: # Update requirements
	venv/bin/pip-compile -o requirements.txt --upgrade requirements.in

dev: reqs # Run reqs and install dependencies
	venv/bin/pip install -r requirements.txt --no-cache-dir
	venv/bin/pre-commit install

run: # Run app
	venv/bin/streamlit run src/user.py

admin: # Run admin app
	venv/bin/streamlit run src/admin.py