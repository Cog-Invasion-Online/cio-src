cmake_minimum_required(VERSION 2.8.8 FATAL_ERROR)
project(ccoginvasion)

file (GLOB SRCS "source/*.cpp")
file (GLOB HEADERS "source/*.h")

source_group("Header Files" FILES ${HEADERS})
source_group("Source Files" FILES ${SRCS})

set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type.")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /DEBUG")
string(REPLACE "/DNDEBUG" "" CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE}")
string(REPLACE "/DNDEBUG" "" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")

if (DEFINED LINK_ALL_STATIC)
    set(P3BUILT built_x64_static)
else()
    set(P3BUILT built_x64)
endif ()
set(COG_PANDA3D_DIR ..\\cio-panda3d\\${P3BUILT})

add_definitions(-DBUILDING_CCOGINVASION -DWITHIN_PANDA)
if (DEFINED LINK_ALL_STATIC)
    set(LIB_TYPE STATIC)
    set(OUT_EXT .lib)
    add_definitions(-DLINK_ALL_STATIC)
else ()
    set(LIB_TYPE SHARED)
    set(OUT_EXT .pyd)
endif ()

include_directories(./source ${COG_PANDA3D_DIR}/python/include ${COG_PANDA3D_DIR}/include)
link_directories(${COG_PANDA3D_DIR}/lib ${COG_PANDA3D_DIR}/python/libs)

add_library(ccoginvasion ${LIB_TYPE} ${SRCS} ${HEADERS})

set_target_properties(ccoginvasion PROPERTIES SUFFIX ${OUT_EXT})

add_custom_command(TARGET ccoginvasion PRE_BUILD COMMAND interrogate.bat)

if (DEFINED LINK_ALL_STATIC)
    add_custom_command(TARGET ccoginvasion POST_BUILD COMMAND copy /Y ${CMAKE_BUILD_TYPE}\\ccoginvasion.lib ${COG_PANDA3D_DIR}\\lib\\ccoginvasion.lib)
else()
    add_custom_command(TARGET ccoginvasion POST_BUILD COMMAND copy /Y ${CMAKE_BUILD_TYPE}\\ccoginvasion.pyd ${COG_PANDA3D_DIR}\\bin\\ccoginvasion.pyd)
    add_custom_command(TARGET ccoginvasion POST_BUILD COMMAND copy /Y ${CMAKE_BUILD_TYPE}\\ccoginvasion.pdb ${COG_PANDA3D_DIR}\\bin\\ccoginvasion.pdb)
endif()

target_link_libraries(ccoginvasion
					  libpanda.lib
					  libpandaexpress.lib
					  libp3dtool.lib
					  libp3dtoolconfig.lib
                      libp3interrogatedb.lib
                      python27.lib)