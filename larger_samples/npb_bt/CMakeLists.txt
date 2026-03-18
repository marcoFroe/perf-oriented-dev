cmake_minimum_required(VERSION 3.11)
project(perf_prog_npb_bt)

set_property(GLOBAL PROPERTY C_STANDARD 11)

# Add an option to enable/disable profiling
option(PROFILING "Enable profiling with gprof" OFF)

if(PROFILING)
  message(STATUS "Profiling enabled")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -pg")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -pg")
endif()

if(MSVC)
  add_compile_options(/W4)
else()
  add_compile_options(-Wall -Wextra -Wno-unknown-pragmas -Wno-unused-parameter)
endif()

file(GLOB_RECURSE SOURCE_FILES CONFIGURE_DEPENDS src/*.c src/*.h)

link_libraries(m)

# Define a function to add profiling to a target
function(add_profiling target_name)
  if(PROFILING)
    target_compile_options(${target_name} PRIVATE -pg)
    target_link_options(${target_name} PRIVATE -pg)
  endif()
endfunction()

# Add executables and optionally enable profiling
add_executable(npb_bt_w ${SOURCE_FILES})
target_include_directories(npb_bt_w PRIVATE src/w)
add_profiling(npb_bt_w)

add_executable(npb_bt_s ${SOURCE_FILES})
target_include_directories(npb_bt_s PRIVATE src/s)
add_profiling(npb_bt_s)

add_executable(npb_bt_a ${SOURCE_FILES})
target_include_directories(npb_bt_a PRIVATE src/a)
add_profiling(npb_bt_a)

add_executable(npb_bt_b ${SOURCE_FILES})
target_include_directories(npb_bt_b PRIVATE src/b)
add_profiling(npb_bt_b)

add_executable(npb_bt_c ${SOURCE_FILES})
target_include_directories(npb_bt_c PRIVATE src/c)
add_profiling(npb_bt_c)