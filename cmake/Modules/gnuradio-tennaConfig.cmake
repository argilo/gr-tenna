find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_TENNA gnuradio-tenna)

FIND_PATH(
    GR_TENNA_INCLUDE_DIRS
    NAMES gnuradio/tenna/api.h
    HINTS $ENV{TENNA_DIR}/include
        ${PC_TENNA_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_TENNA_LIBRARIES
    NAMES gnuradio-tenna
    HINTS $ENV{TENNA_DIR}/lib
        ${PC_TENNA_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-tennaTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_TENNA DEFAULT_MSG GR_TENNA_LIBRARIES GR_TENNA_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_TENNA_LIBRARIES GR_TENNA_INCLUDE_DIRS)
