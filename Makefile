.PHONY: show_docs live_docs all docs proto dist upload

# some instructions and setup from the following blog:
# https://dmltquant.github.io/ply_sphinx_docs_github_pages/README.html#step-01-project-folder

show_docs:
	@echo "Serving ./docs on http://127.0.0.1:8000/"
	@python3 -m http.server 8000 --bind 127.0.0.1 --directory ./docs

live_docs: | docs show_docs

all: | dist docs

docs:
	rm -rf docs
	rm -rf docsource/_autosummary
	rm -rf docsource/_build
	mkdir ./docs && touch ./docs/.nojekyll
	@make -C ./docsource html
	@cp -a ./docsource/_build/html/. ./docs

proto:
	python3 -m grpc_tools.protoc --proto_path=proto --python_out=mcpq/_proto --grpc_python_out=mcpq/_proto proto/minecraft.proto

dist:
	rm -rf dist
	python3 -m build
	python3 -m twine check dist/*

upload:
	@test -f ~/.pypirc || echo "~/.pypirc does not exist, add PyPi and TestPyPi tokens!"
	@test -f ~/.pypirc
	@test -f /tmp/mcpq_warnup || echo "Do NOT forget to first 'git tag vX.Y.Z', then 'make all', then 'git commit' (to commit docs)!"
	@test -f /tmp/mcpq_warnup || (touch /tmp/mcpq_warnup && test)
	python3 -m twine check dist/*
	@test ! -f /tmp/mcpq_testup || echo "Package will now be uploaded to REAL PyPi!"
	@test -f /tmp/mcpq_testup || echo "Package will first be uploaded to TestPyPi!"
	@echo "Are you sure you want to upload?"
	@echo "(Upload will start in 10 seconds, abort with Ctrl+C...)"
	@sleep 10
	@test ! -f /tmp/mcpq_testup || python3 -m twine upload dist/*
	@test -f /tmp/mcpq_testup || python3 -m twine upload --repository testpypi dist/*
	@rm /tmp/mcpq_testup 2> /dev/null || touch /tmp/mcpq_testup
