cmake_minimum_required(VERSION 3.20)
project(tiny_ttf_workbook LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

# In Debug, std::vector::operator[] and friends are bounds-checked, so an
# off-by-one stops with a clear message instead of printing wrong numbers.
add_compile_options(-Wall -Wextra -Wno-unused-parameter
                    $<$<CONFIG:Debug>:-D_GLIBCXX_ASSERTIONS>)
if(MINGW)
  add_link_options(-static)  # no runtime DLLs needed to run the programs
endif()
include_directories(include third_party/glm-1.0.1 third_party/stb)

# Code you share between checkpoints: every .cpp in solutions/common/ is compiled once
# and linked into each of your programs (not the reference ones). Include its headers as
# "common/name.h". New files are picked up on the next build.
file(GLOB COMMON_SOURCES CONFIGURE_DEPENDS ${CMAKE_SOURCE_DIR}/solutions/common/*.cpp)
if(COMMON_SOURCES)
  add_library(common OBJECT ${COMMON_SOURCES})
  target_include_directories(common PUBLIC solutions)
endif()

# One program per checkpoint: p<id> is yours, ref_p<id> is the reference (spoiler).
# A program is only added once its source file exists; `.\check` re-runs this
# configuration step when it finds a new one.
function(add_checkpoint id slug)
  if(EXISTS ${CMAKE_SOURCE_DIR}/solutions/p${id}_${slug}.cpp)
    add_executable(p${id} solutions/p${id}_${slug}.cpp)
    target_include_directories(p${id} PRIVATE solutions)
    if(TARGET common)
      target_link_libraries(p${id} PRIVATE common)
    endif()
  endif()
  if(EXISTS ${CMAKE_SOURCE_DIR}/_spoilers/reference/p${id}_${slug}.cpp)
    add_executable(ref_p${id} _spoilers/reference/p${id}_${slug}.cpp)
  endif()
endfunction()

add_checkpoint(01 byte_readers)
add_checkpoint(02 table_directory)
add_checkpoint(03 cmap)
add_checkpoint(04 loca)
add_checkpoint(05 metrics)
add_checkpoint(06 canvas)
add_checkpoint(07 simple_glyph)
add_checkpoint(08 outline_lines)
add_checkpoint(09 compound_glyph)
add_checkpoint(10 bezier)
add_checkpoint(11 outline_curves)
add_checkpoint(12 segment_intersection)
add_checkpoint(13 line_curve_intersection)
add_checkpoint(14 even_odd_fill)
add_checkpoint(15 bezier_min_y)
add_checkpoint(16 nonzero_lines)
add_checkpoint(17 nonzero_curves)
add_checkpoint(18 render_text)
