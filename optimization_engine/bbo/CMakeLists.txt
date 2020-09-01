############  Set the path of the bbo library.
set(BBO_SRC ${IOANALYTICS_SRC}/bbo)

########### target to install the bbo library ############
add_custom_target(install-bbo-lib
    DEPENDS python-virt-env
    WORKING_DIRECTORY ${BBO_SRC}
    COMMAND env ${ENV_PROXY} ${IOANALYTICS_RPM_VERSION} ${VIRT_PYTHON} -m pip install . ${PIP_OPT})

########### target to download the bbo dependencies ############
set(EXTERNAL_DEPS ${CMAKE_CURRENT_BINARY_DIR}/external_deps.txt)
add_custom_command(OUTPUT ${EXTERNAL_DEPS}
    WORKING_DIRECTORY ${BBO_SRC}
    COMMAND grep -ivEh ${LOCAL_LIBS} requirements.txt > ${EXTERNAL_DEPS} VERBATIM)

add_custom_target(download-bbo-deps
    DEPENDS create-deps-repo ${EXTERNAL_DEPS}
    WORKING_DIRECTORY ${BBO_SRC}
    COMMAND env ${ENV_PROXY} pip download -r ${EXTERNAL_DEPS} -d ${PY_DEPS_DIR} VERBATIM)

########### targets to byte-compile the bbo library ############
add_custom_target(compile-bbo
    WORKING_DIRECTORY ${IOANALYTICS_SRC_COPY}/bbo
    DEPENDS python-src-copy
    COMMAND python -m compileall -b -f .
    COMMENT echo "Byte-compiling all python modules present in the bbo source dir")

add_custom_target(select-compiled-bbo
    WORKING_DIRECTORY ${IOANALYTICS_SRC_COPY}/bbo
    DEPENDS compile-bbo
    COMMAND find . -type f -name \"*.py\" ! -name \"__init__.py\" ! -name \"setup.py\" -delete
    COMMENT "Remove all bbo sources .py files except for __init__ file which are required for packaging")

add_subdirectory(tests)
