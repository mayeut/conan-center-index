cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(tomlplusplus REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE tomlplusplus::tomlplusplus)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(NOT DEFINED TOMLPP_BUILD_SINGLE_ONLY)
    add_executable(${PROJECT_NAME}_multi test_package_multi.cpp)
    target_link_libraries(${PROJECT_NAME}_multi PRIVATE tomlplusplus::tomlplusplus)
    target_compile_features(${PROJECT_NAME}_multi PRIVATE cxx_std_17)
endif()
