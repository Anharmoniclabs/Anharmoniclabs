cmake_minimum_required(VERSION 3.16)
project(quantonium_qsc C)

option(QSC_ENABLE_SANITIZERS "Build with address/undefined sanitizers" OFF)

add_library(quantonium_qsc SHARED quantum_symbolic_compression.c)
target_compile_features(quantonium_qsc PRIVATE c_std_11)
target_include_directories(quantonium_qsc PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
)
target_link_libraries(quantonium_qsc PRIVATE m)
set_target_properties(quantonium_qsc PROPERTIES
    OUTPUT_NAME quantonium_qsc
    C_VISIBILITY_PRESET default
)

if(MSVC)
    target_compile_options(quantonium_qsc PRIVATE /W4)
else()
    target_compile_options(quantonium_qsc PRIVATE -Wall -Wextra -Wpedantic)
    if(QSC_ENABLE_SANITIZERS)
        target_compile_options(quantonium_qsc PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
        target_link_options(quantonium_qsc PRIVATE -fsanitize=address,undefined)
    endif()
endif()
