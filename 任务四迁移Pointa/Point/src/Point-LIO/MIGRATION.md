Point-LIO：ROS1 → ROS2 迁移文档
0.report 本次ROS1向ROS2的功能包迁移由我独立完成，过程中使用AI大模型作为辅助工具。大部分代码修改、报错排查由ai自主完成,因为这个好多功能我不了解，其中部分复杂代码模块，仅凭我个人能力难以直接完成迁移，参考了AI给出的修改方案。我对许多地方都改动进行阅读、理解，并且亲自编译调试，其中package和mkelist还有一部分cpp代码都是我手动修改编译，记录迁移过程中的问题与解决办法，量力而行做到最好，如果我能进入视觉组，我一定会进一步了解学习ros的迁移，把时间投入当中，目前这个人ros2的src可以使用但是我剔除了雷达模块，可以编译执行，节点可以正常接受消息，但是要有雷达IMU才能出结果，没数据时 rviz 是空/黑的，激光雷达输入点云应该就可以可视化了
1. 工程介绍
Point-LIO 是港大 Mars Lab开源的高带宽 LiDAR-Inertial Odometry，基于 IESKF + IKFoM 框架，逐点更新输出高带宽位姿。支持 Velodyne / Ouster / Hesai / Livox 多种雷达
原始工程使用 ROS1（catkin + roscpp + tf），本次迁移到 ROS2（ament_cmake + rclcpp + tf2）。源码位于 `~/Point/src/Point-LIO`
选择的理由就是这个src里面pacakage和cmake很少，cpp更多一些，像egoplanner里面13个功能包每个都有package和cmakelist修改配置太过繁琐，point相对就只用改cpp文件，配置文件较少方便修改
2. 迁移概括

|    | ROS1 | ROS2 |
| 构建 | catkin | ament_cmake |
| 核心库 | roscpp / `ros::NodeHandle` | rclcpp / `rclcpp::Node` |
| 消息头 | `sensor_msgs/Imu.h` | `sensor_msgs/msg/imu.hpp` |
| 命名空间 | `sensor_msgs::Imu` | `sensor_msgs::msg::Imu` |
| 智能指针 | `::ConstPtr`/`::Ptr` | `::ConstSharedPtr`/`::SharedPtr` |
| TF | `tf::TransformBroadcaster` | `tf2_ros::TransformBroadcaster` |
| 日志 | `ROS_WARN/INFO` | `RCLCPP_WARN/INFO` |
| 参数 | `nh.param<T>()` | `declare_parameter`+`get_parameter` |
| launch | XML `.launch` | Python `.launch.py` |
| 雷达 | Livox + Velodyne/Ouster/Hesai | **仅 Velodyne/Ouster/Hesai** |

备注：代码无条件依赖未安装的 `livox_ros_driver2`，实际用 Velodyne/Ouster/Hesai，故移除全部 livox/AVIA 代码

3. 逐文件改动


TF 重写：

```diff
- static tf::TransformBroadcaster br;
- tf::StampedTransform(transform, stamp, "camera_init", "body")
+ geometry_msgs::msg::TransformStamped t;
+ t.header.frame_id="camera_init"; t.child_frame_id="body";
+ t.transform.rotation = odom.pose.pose.orientation;
+ tf_broadcaster_->sendTransform(t);
```

main 重写：

```diff
- ros::init(argc, argv, "laserMapping");
- ros::NodeHandle nh("~"); ros::AsyncSpinner spinner(0);
+ rclcpp::init(argc, argv);
+ auto node = std::make_shared<rclcpp::Node>("pointlio_mapping");
- nh.subscribe(lid_topic, 200000, cb) / nh.advertise<T>(...)
+ node->create_subscription<T>(lid_topic, rclcpp::SensorDataQoS(), cb)
+ node->create_publisher<T>(...)
- ros::Rate(500); ros::spinOnce(); ros::ok()
+ rclcpp::Rate(500); rclcpp::spin_some(node); rclcpp::ok()
```

全文 `.toSec()` → `stamp_to_sec()`；`ros::Time().fromSec()` → `sec_to_stamp()`；末尾加 `rclcpp::shutdown()`

### Estimator.cpp — 补回纯算法

原文件为空（链接失败），纯数学实现无 ROS 依赖，直接从 ROS1 源码复制补回。

### package.xml

```diff
   <buildtool_depend>ament_cmake</buildtool_depend>
-  <buildtool_depend>rosidl_default_generators</buildtool_depend>
   <depend>rclcpp</depend>
   <depend>geometry_msgs</depend>
   <depend>nav_msgs</depend>
   <depend>sensor_msgs</depend>
   <depend>std_msgs</depend>
   <depend>pcl_ros</depend>
   <depend>tf2_ros</depend>
-  <depend>rosidl_default_runtime</depend>
+  <depend>builtin_interfaces</depend>
```

`rosidl_default_generators/runtime` 仅用于生成自定义消息（本包未用）→ 移除；`builtin_interfaces` 提供 `Time` 消息类型

### CMakeLists.txt

```diff
  find_package(ament_cmake REQUIRED)
  find_package(rclcpp REQUIRED)
  find_package(geometry_msgs REQUIRED)
  find_package(nav_msgs REQUIRED)
  find_package(sensor_msgs REQUIRED)
  find_package(std_msgs REQUIRED)
  find_package(pcl_ros REQUIRED)
  find_package(tf2_ros REQUIRED)
- find_package(rosidl_default_generators REQUIRED)
+ find_package(builtin_interfaces REQUIRED)

  ament_target_dependencies(pointlio_mapping
    rclcpp geometry_msgs nav_msgs sensor_msgs std_msgs
    pcl_ros tf2_ros
+   builtin_interfaces
  )

  target_link_libraries(pointlio_mapping ${PCL_LIBRARIES} OpenMP::OpenMP_CXX)

- target_link_libraries(pointlio_mapping "${cpp_typesupport_target}")  # 引用未定义变量，报错

  install(TARGETS pointlio_mapping DESTINATION lib/${PROJECT_NAME})
  install(DIRECTORY config launch rviz_cfg DESTINATION share/${PROJECT_NAME})
  ament_package()
```

删 `rosidl_default_generators`（自定义消息貌似未用）

### config/*.yaml — 参数文件格式

```yaml
# ROS1                     # ROS2
common:                    /**:
  lid_topic: "..."           ros__parameters:
                               common:
                                 lid_topic: "..."
```

把原 launch 顶层 `<param>` 合并进 yaml；数值类型对齐（`satu_gyro: 35`→`35.0`，`extrinsic_R: [1,0,...]`→`[1.0,0.0,...]`）。

### launch/ — 删除旧 XML，新建 .launch.py

```python
def generate_launch_description():
    pkg_dir = get_package_share_directory('point_lio')
    return LaunchDescription([
        Node(package='point_lio', executable='pointlio_mapping',
             name='laserMapping', output='screen',
             parameters=[os.path.join(pkg_dir, 'config', 'velody16.yaml')]),
        Node(package='rviz2', executable='rviz2',
             arguments=['-d', os.path.join(pkg_dir, 'rviz_cfg', 'loam_livox.rviz')],
             condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
```

### rviz_cfg — 重写为 rviz2 格式

类名 `rviz/Displays`→`rviz_common/Displays`、`rviz/PointCloud2`→`rviz_default_plugins/PointCloud2`；`Topic` 改嵌套 `{Value: /xxx}`；Odometry 话题修正 `/Odometry`→`/aft_mapped_to_init`。

4. ROS1 → ROS2 API 对照

```cpp
// 消息
#include <sensor_msgs/Imu.h>          →  #include <sensor_msgs/msg/imu.hpp>
sensor_msgs::Imu msg                  →  sensor_msgs::msg::Imu msg

// 指针
sensor_msgs::Imu::ConstPtr            →  sensor_msgs::msg::Imu::ConstSharedPtr

// 时间戳
msg->header.stamp.toSec()             →  stamp_to_sec(msg->header.stamp)
msg->header.stamp = ros::Time().fromSec(1.5)  →  msg->header.stamp = sec_to_stamp(1.5)

// 节点
ros::init(...); ros::NodeHandle nh("~")  →  rclcpp::init(...); auto node = make_shared<rclcpp::Node>(...)
nh.subscribe(topic, q, cb)               →  node->create_subscription<T>(topic, qos, cb)
nh.advertise<T>(topic, q)                →  node->create_publisher<T>(topic, q)
ros::spin() / spinOnce()                 →  rclcpp::spin(node) / spin_some(node)

// 参数
nh.param<T>(name, var, def)           →  declare_parameter<T>(name, def); get_parameter(name, var)

// 日志
ROS_WARN("x %d", n)                   →  RCLCPP_WARN(rclcpp::get_logger("point_lio"), "x %d", n)

// TF
tf::TransformBroadcaster br;          →  tf2_ros::TransformBroadcaster br(node);
tf::StampedTransform                  →  geometry_msgs::msg::TransformStamped
```

5. 遇到的错误与解决
ROS1迁移ROS2过程问题与解决记录
 
问题1：报错  deque has not been declared 
 
报错原因：
在ROS1中，引入 ros/ros.h 会间接自带引入 deque 、 vector 等STL容器头文件，不用手动添加。但ROS2的 rclcpp 不会自动引入这些标准库，导致程序识别不到容器类型
 
解决方法：
我在 preprocess.h 头文件中，手动显式添加所需的标准库头文件 <vector> ，补齐缺失的容器定义
 
问题2：报错  glog/logging.h  找不到
 
报错原因：
项目中的ivox3d算法模块依赖glog日志库，但当前Ubuntu22.04环境没有安装对应依赖，导致头文件无法识别。且代码中所有LOG日志语句已经注释，实际不需要glog功能
 
解决方法：
这个我实在下载不来，问过ai直接注释代码中引入 glog/logging.h 的头文件语句，规避依赖缺失问题，不影响整体算法运行
 
问题3：链接报错  undefined reference to kf_input  等变量
 
报错原因：
迁移后的 Estimator.cpp 文件内容为空，缺失了ROS1原版的核心算法实现代码，编译时找不到变量和函数的具体定义，出现链接错误
 
解决方法：
对照ROS1原始源码，借助ai纯算法实现代码完整复制回 Estimator.cpp ，补齐缺失逻辑
 
问题4：RVIZ报错  class rviz/Displays does not exist 
报错原因：
ROS1的RVIZ配置文件、显示插件类名和ROS2的RVIZ2不兼容，旧的ROS1显示类无法在ROS2环境识别加载
 
解决方法：
不再使用旧的ROS1配置，手动在RVIZ2中重新添加显示组件，适配ROS2话题嵌套格式，重新配置可视化参数
 
问题5：运行提示  mapping_velody16.launch. 文件找不到 
 
报错原因：
ROS1的启动文件是 .launch 后缀的XML文件，ROS2只支持 .launch.py 后缀的Python启动文件，输入命令时遗漏后缀、残留旧XML文件都会报错
 
解决方法：
删除项目内所有ROS1旧版XML启动文件，运行命令时输入完整文件名，使用后缀为 .launch.py 的ROS2新版启动文件
 
问题6：终端提示  ignoring unknown package 'point_lio' 
 
报错原因：
执行 colcon build 编译命令时，终端当前工作目录错误，不在项目根目录，导致编译工具无法识别功能包
 
解决方法：
切换到项目总根目录（ ~/Point 目录），再执行编译指令，即可正常识别并编译point_lio功能包
6. 编译与运行

```bash
# 编译
cd ~/Point
source /opt/ros/humble/setup.bash
colcon build --packages-select point_lio

# 运行
source install/setup.bash
ros2 launch point_lio mapping_velody16.launch.py          # Velodyne，带 rviz
ros2 launch point_lio mapping_ouster64.launch.py rviz:=false   # Ouster，不带 rviz

# 验证
ros2 node list          # 应看到 /laserMapping
ros2 topic list         # 订阅 /velodyne_points、/imu/data；发布 /cloud_registered、/path、/tf 等
