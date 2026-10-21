cmake_minimum_required(VERSION 3.20)
project(tiny_ttf LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

# Debug builds bounds-check std::vector and friends, so an off-by-one stops with a
# clear message instead of quietly producing wrong numbers.
add_compile_options(-Wall -Wextra -Wno-unused-parameter
                    $<$<CONFIG:Debug>:-D_GLIBCXX_ASSERTIONS>)
if(MINGW)
  add_link_options(-static)  # the programs run without the compiler's DLLs
endif()

# The renderer: every .cpp under src/ except main.cpp. Headers are included from src/,
# e.g. #include "font/ByteReader.h", and from third_party/ (stb_image_write.h, for PNG files).
# New files are picked up on the next build.
file(GLOB_RECURSE CORE_SOURCES CONFIGURE_DEPENDS ${CMAKE_SOURCE_DIR}/src/*.cpp)
list(REMOVE_ITEM CORE_SOURCES ${CMAKE_SOURCE_DIR}/src/main.cpp)
if(CORE_SOURCES)
  add_library(tiny_ttf_core STATIC ${CORE_SOURCES})
  target_include_directories(tiny_ttf_core PUBLIC src third_party)
else()
  add_library(tiny_ttf_core INTERFACE)  # only headers so far
  target_include_directories(tiny_ttf_core INTERFACE src third_party)
endif()

# The command-line program: tiny_ttf <font.ttf> "<text>" <out.png> [pixel-height]
if(EXISTS ${CMAKE_SOURCE_DIR}/src/main.cpp)
  add_executable(tiny_ttf src/main.cpp)
  target_link_libraries(tiny_ttf PRIVATE tiny_ttf_core)
endif()

# One small program per checkpoint (checkpoints/p07_simple_glyph.cpp -> p07). Each reads
# a test input, calls the renderer and writes what it found; the workbook's checker runs them.
file(GLOB CHECKPOINT_SOURCES CONFIGURE_DEPENDS ${CMAKE_SOURCE_DIR}/checkpoints/p*.cpp)
foreach(source ${CHECKPOINT_SOURCES})
  get_filename_component(name ${source} NAME_WE)
  string(REGEX MATCH "^p[0-9]+" target ${name})
  add_executable(${target} ${source})
  target_link_libraries(${target} PRIVATE tiny_ttf_core)
endforeach()
