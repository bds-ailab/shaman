########### add a "python-iomoduleshandler-ut" target to test python code and, if "coverage" is available,
# generate report on code coverage
if(USE_UNIT_TESTS)
    find_package(PyCoverage)
    if(PYCOVERAGE_EXEC AND USE_COVERAGE)
        add_custom_target(python-iomoduleshandler-ut
            WORKING_DIRECTORY ${IOMODULESHANDLER_SRC}
            DEPENDS install-iomoduleshandler-lib
            COMMAND ${VIRT_PYTHON} -m coverage run -m unittest discover -s ${IOMODULESHANDLER_SRC}/tests -v
            COMMAND ${VIRT_PYTHON} -m coverage xml --include="${IOMODULESHANDLER_SRC}/*" --omit="*/tests/*, */__init__.py"  -o ${REPORTS_DIR}/pycoverage-iomoduleshandler.xml
            COMMAND ${VIRT_PYTHON} -m coverage report --include="${IOMODULESHANDLER_SRC}/*" --omit="*/tests/test*,*/__init__.py"
            COMMENT "Running Python unit tests for iomoduleshandler library and generating code coverage report")
    else(PYCOVERAGE_EXEC AND USE_COVERAGE)
        add_custom_target(python-iomoduleshandler-ut
            WORKING_DIRECTORY ${IOMODULESHANDLER_SRC}
            DEPENDS install-iomoduleshandler-lib
            COMMAND ${VIRT_PYTHON} -m unittest -v
            COMMENT "Running Python unit tests for iomoduleshandler library")
    endif(PYCOVERAGE_EXEC AND USE_COVERAGE)
endif(USE_UNIT_TESTS)