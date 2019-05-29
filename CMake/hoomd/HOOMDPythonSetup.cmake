# use pybind11's tools to find python and create python modules
list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/hoomd/extern/pybind/tools)

# for installed hoomd with external plugins
if (HOOMD_INCLUDE_DIR)
    list(APPEND CMAKE_MODULE_PATH ${HOOMD_INCLUDE_DIR}/hoomd/extern/pybind/tools)
endif()

# find_package(pybind11 NO_MODULE)
include(pybind11Tools)

# set python installation location
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import site; print(site.getsitepackages()[0], end='')"
                    OUTPUT_VARIABLE _python_site_dir)
    set(CMAKE_INSTALL_PREFIX ${_python_site_dir} CACHE PATH "HOOMD installation path" FORCE)
endif(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)

set(PYTHON_SITE_INSTALL_DIR "hoomd")
