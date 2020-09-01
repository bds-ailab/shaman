############  Set the path of the iomodules_handler library.
set(IOMODULESHANDLER_SRC ${IOANALYTICS_SRC}/iomodules_handler)

########### target to install the iomodules_handler library ############
add_custom_target(install-iomoduleshandler-lib
    DEPENDS python-virt-env
    WORKING_DIRECTORY ${IOMODULESHANDLER_SRC}
    COMMAND env ${ENV_PROXY} ${IOANALYTICS_RPM_VERSION} ${VIRT_PYTHON} -m pip install . ${PIP_OPT})

########### target to download the iomodules_handler dependencies ############
set(EXTERNAL_DEPS ${CMAKE_CURRENT_BINARY_DIR}/external_deps.txt)
add_custom_command(OUTPUT ${EXTERNAL_DEPS}
    WORKING_DIRECTORY ${IOMODULESHANDLER_SRC}
    COMMAND grep -ivEh ${LOCAL_LIBS} requirements.txt > ${EXTERNAL_DEPS} VERBATIM)
    
add_custom_target(download-iomoduleshandler-deps
    DEPENDS create-deps-repo ${EXTERNAL_DEPS}
    WORKING_DIRECTORY ${IOMODULESHANDLER_SRC}
    COMMAND env ${ENV_PROXY} pip download -r ${EXTERNAL_DEPS} -d ${PY_DEPS_DIR} VERBATIM)

########### targets to byte-compile the iomodules_handler library ############
add_custom_target(compile-iomoduleshandler
    WORKING_DIRECTORY ${IOANALYTICS_SRC_COPY}/iomodules_handler
    DEPENDS python-src-copy
    COMMAND python -m compileall -b -f .
    COMMENT echo "Byte-compiling all python modules present in the iomodules_handler source dir")

add_custom_target(select-compiled-iomoduleshandler
    WORKING_DIRECTORY ${IOANALYTICS_SRC_COPY}/iomodules_handler
    DEPENDS compile-iomoduleshandler
    COMMAND find . -type f -name \"*.py\" ! -name \"__init__.py\" ! -name \"setup.py\" -delete
    COMMENT "Remove all iomodules_handler sources .py files except for __init__ file which are required for packaging")

add_subdirectory(tests)
