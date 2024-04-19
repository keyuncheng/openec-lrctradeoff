cmake_minimum_required(VERSION 3.1)

project(LRCTradeoff)

add_subdirectory(util)
add_subdirectory(model)
add_subdirectory(comm)

aux_source_directory(. DIR_SRCS)

add_executable(GenECStripe GenECStripe.cc)
add_executable(Controller Controller.cc)
add_executable(Gateway Gateway.cc)
add_executable(Agent Agent.cc)

target_link_libraries(GenECStripe model comm util isal)
target_link_libraries(Controller comm util model pthread sockpp)
target_link_libraries(Gateway comm util model pthread sockpp)
target_link_libraries(Agent comm util model pthread sockpp isal)