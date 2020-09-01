########### add a "python-littleshaman-ut" target to test python code and, if "coverage" is available,
# generate report on code coverage
if(USE_UNIT_TESTS)
    find_package(PyCoverage)
    if(PYCOVERAGE_EXEC AND USE_COVERAGE)
        add_custom_target(python-littleshaman-ut
            WORKING_DIRECTORY ${LITTLESHAMAN_SRC}
            DEPENDS install-littleshaman-lib
            COMMAND ${VIRT_PYTHON} -m coverage run -m unittest -v
            COMMAND ${VIRT_PYTHON} -m coverage xml --include="${LITTLESHAMAN_SRC}/*" --omit="*/tests/*, */__init__.py"  -o ${REPORTS_DIR}/pycoverage-littleshaman.xml
            COMMAND ${VIRT_PYTHON} -m coverage report --include="${LITTLESHAMAN_SRC}/*" --omit="*/tests/test*,*/__init__.py"
            COMMENT "Running Python unit tests for littleshaman library and generating code coverage report")
    else(PYCOVERAGE_EXEC AND USE_COVERAGE)
        add_custom_target(python-littleshaman-ut
            WORKING_DIRECTORY ${LITTLESHAMAN_SRC}
            DEPENDS install-littleshaman-lib
            COMMAND ${VIRT_PYTHON} -m unittest -v
            COMMENT "Running Python unit tests for little_shaman library")
    endif(PYCOVERAGE_EXEC AND USE_COVERAGE)
endif(USE_UNIT_TESTS)