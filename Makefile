.PHONY: show_docs live_docs docs proto dist

# some instructions and setup from the following blog:
# https://dmltquant.github.io/ply_sphinx_docs_github_pages/README.html#step-01-project-folder

# host the current ./docs folder locally
show_docs:
	python3 -m http.server 8000 --bind 127.0.0.1 --directory ./docs

# clean the current build then
# test build docs in local environment and
# start python http.server
live_docs:
	rm -rf docsource/_build
	make -C ./docsource html && python3 -m http.server 8000 --bind 127.0.0.1 --directory ./docsource/_build/html

# manual
docs:
	rm -rf docs
	rm -rf docsource/_autosummary
	rm -rf docsource/_build
	mkdir ./docs && touch ./docs/.nojekyll
	@make -C ./docsource html
	@cp -a ./docsource/_build/html/. ./docs

# automatic github action push or pull request
# github_action_docs:
# 	rm -rf docs
# 	mkdir docs && touch docs/.nojekyll
# 	rm -rf docsource/_build && mkdir docsource/_build
# 	rm -rf docsource/_autosummary
# 	pipx run sphinx-build -b html docsource docsource/_build/html
# 	@cp -a docsource/_build/html/* docs

proto:
	python3 -m grpc_tools.protoc --proto_path=proto --python_out=mcpq/_proto --grpc_python_out=mcpq/_proto proto/minecraft.proto

dist:
	rm -rf dist
	python3 -m build
