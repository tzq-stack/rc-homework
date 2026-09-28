cmake_minimum_required(VERSION 3.8)
project(cpp01_topic)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# 生成自定义消息接口
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/StudentInfo.msg"
)


rosidl_get_typesupport_target(cpp_typesupport_target "${PROJECT_NAME}" "rosidl_typesupport_cpp")


# ========== 第三步：安装编译出来的可执行文件 ==========
install(PROGRAMS
  scripts/publisher_node.py
  scripts/subscriber_node.py
  DESTINATION lib/${PROJECT_NAME}
)



if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()


install(PROGRAMS
  scripts/publisher_node.py
  scripts/subscriber_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()