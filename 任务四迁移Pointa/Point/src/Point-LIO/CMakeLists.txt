cmake_minimum_required(VERSION 3.8)
project(point_lio)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra)
endif()

set(CMAKE_BUILD_TYPE "Debug")

add_compile_options(-std=c++14 )
set( CMAKE_CXX_FLAGS "-std=c++14 -O3" )

add_definitions(-DROOT_DIR=\"${CMAKE_CURRENT_SOURCE_DIR}/\")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fexceptions" )
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -pthread -fexceptions")

message("Current CPU archtecture: ${CMAKE_SYSTEM_PROCESSOR}")
if(CMAKE_SYSTEM_PROCESSOR MATCHES "(x86)|(X86)|(amd64)|(AMD64)" )
  include(ProcessorCount)
  ProcessorCount(N)
  message("Processer number:  ${N}")
  if(N GREATER 5)
    add_definitions(-DMP_EN)
    add_definitions(-DMP_PROC_NUM=4)
    message("core for MP:  3")
  elseif(N GREATER 3)
    math(EXPR PROC_NUM "${N} - 2")
    add_definitions(-DMP_EN)
    add_definitions(-DMP_PROC_NUM="${PROC_NUM}")
    message("core for MP:  ${PROC_NUM}")
  else()
    add_definitions(-DMP_PROC_NUM=1)
  endif()
else()
  add_definitions(-DMP_PROC_NUM=1)
endif()

find_package(OpenMP QUIET)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}   ${OpenMP_C_FLAGS}")

# 注释Python相关，避免ros2 python版本冲突
#find_package(PythonLibs REQUIRED)
#find_path(MATPLOTLIB_CPP_INCLUDE_DIRS "matplotlibcpp.h")

# ========= ROS2 ament 依赖 =========
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(pcl_ros REQUIRED)
find_package(tf2_ros REQUIRED)
#find_package(livox_ros_driver2 REQUIRED)
#find_package(eigen_conversions REQUIRED)
find_package(builtin_interfaces REQUIRED)

# ========= 第三方库 =========
find_package(Eigen3 REQUIRED)
find_package(PCL 1.8 REQUIRED)

message(Eigen: ${EIGEN3_INCLUDE_DIR})

# ========= 生成自定义消息（使用真实存在的msg文件） =========
#rosidl_generate_interfaces(${PROJECT_NAME}
 # msg/LocalSensorExternalTrigger.msg
 # DEPENDENCIES geometry_msgs
#)

# ========= 可执行文件 =========
add_executable(pointlio_mapping
  src/laserMapping.cpp
  src/li_initialization.cpp
  src/parameters.cpp
  src/preprocess.cpp
  src/Estimator.cpp
  src/IMU_Processing.cpp
)

# target 头文件
target_include_directories(pointlio_mapping PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  ${EIGEN3_INCLUDE_DIR}
  ${PCL_INCLUDE_DIRS}
  #${PYTHON_INCLUDE_DIRS}
)

# ament只填ROS相关包
ament_target_dependencies(pointlio_mapping
  rclcpp
  geometry_msgs
  nav_msgs
  sensor_msgs
  std_msgs
  pcl_ros
  tf2_ros
  builtin_interfaces
  #livox_ros_driver2
  #eigen_conversions
)

# 第三方库手动链接
target_link_libraries(pointlio_mapping
  ${PCL_LIBRARIES}
  #${PYTHON_LIBRARIES}
  OpenMP::OpenMP_CXX
)

# ========= install 安装规则 =========
install(TARGETS
  pointlio_mapping
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  config
  launch
  rviz_cfg
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

