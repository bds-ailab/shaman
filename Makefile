install: install-bbo install-iomodules install-little-shaman

install-citools:
	virtualenv .venv && \
	.venv/bin/python -m pip install -r ci-requirements.txt

install-bbo:
	cd bbo && \
	virtualenv .venv && \
	.venv/bin/python -m pip install .

install-iomodules:
	cd iomodules_handler && \
	virtualenv .venv && \
	.venv/bin/python -m pip install .

install-little-shaman:
	cd little_shaman && \
	virtualenv .venv && \
	.venv/bin/python -m pip install ../bbo/ && \
	.venv/bin/python -m pip install ../iomodules_handler && \
	.venv/bin/python -m pip install .

test-unit: test-bbo test-iomodules test-little-shaman generate-coverage

test-int: test-iomodules-integration

test-bbo:
	cd bbo && \
	.venv/bin/python -m coverage run --omit '.venv/*','tests/*' -m unittest discover -s tests/

test-iomodules:
	cd iomodules_handler && \
	.venv/bin/python -m coverage run --omit '.venv/*','tests/*','tests_integration/*' -m unittest discover -s tests/

test-iomodules-test-integration:
	cd iomodules_handler && \
	.venv/bin/python -m coverage run --omit '.venv/*','tests/*','tests_integration/*' -m unittest discover -s tests_integration/

test-little-shaman:
	cd little_shaman && \
	.venv/bin/python -m coverage run --omit '.venv/*','tests/*' -m unittest discover -s tests/

generate-coverage:
	mkdir -p coverage_files && \
	mv bbo/.coverage coverage_files/bbo.coverage && \
	mv iomodules_handler/.coverage coverage_files/iomodules_handler.coverage && \
	mv little_shaman/.coverage coverage_files/little_shaman.coverage && \
	cd coverage_files && \
	../.venv/bin/python -m coverage combine bbo.coverage iomodules_handler.coverage little_shaman.coverage && \
	../.venv/bin/python -m coverage report -m

linter:
	.venv/bin/python -m pylint --exit-zero -d duplicate-code bbo/bbo iomodules_handler/iomodules_handler little_shaman/little_shaman

clean-venv:
	rm -rf .venv
	rm -rf ./*/.venv

clean-coverage:
	rm -rf coverage_files

clean: clean-venv clean-coverage

ci: clean install-citools install test-unit linter
