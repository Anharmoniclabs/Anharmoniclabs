cmake_minimum_required(VERSION 3.16)
project(anharmonic_structured C)

option(ANHARMONIC_STRUCTURED_ENABLE_SANITIZERS "Build with address/undefined sanitizers" OFF)

add_library(anharmonic_structured SHARED anharmonic_structured.c)
target_compile_features(anharmonic_structured PRIVATE c_std_11)
target_include_directories(anharmonic_structured PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../upstream_abi
)
target_link_libraries(anharmonic_structured PRIVATE m)
set_target_properties(anharmonic_structured PROPERTIES
    OUTPUT_NAME anharmonic_structured
    C_VISIBILITY_PRESET default
)

if(MSVC)
    target_compile_options(anharmonic_structured PRIVATE /W4)
else()
    target_compile_options(anharmonic_structured PRIVATE -Wall -Wextra -Wpedantic)
    if(ANHARMONIC_STRUCTURED_ENABLE_SANITIZERS)
        target_compile_options(anharmonic_structured PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
        target_link_options(anharmonic_structured PRIVATE -fsanitize=address,undefined)
    endif()
endif()
