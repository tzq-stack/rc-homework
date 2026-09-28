from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    cam_id_arg = DeclareLaunchArgument("cam_id",default_value="0",description="摄像头设备号")
    width_arg = DeclareLaunchArgument("width",default_value="1280")
    height_arg = DeclareLaunchArgument("height",default_value="720")

    ocr_node = Node(
        package="math_ocr_pkg",
        executable="ocr_publisher.py",
        name="math_ocr_publisher",
        parameters=[
            {"cam_id":LaunchConfiguration("cam_id")},
            {"width":LaunchConfiguration("width")},
            {"height":LaunchConfiguration("height")}
        ],
        output="screen"
    )
    sub_node = Node(
        package="math_ocr_pkg",
        executable="result_subscriber.py",
        name="result_subscriber",
        output="screen"
    )

    return LaunchDescription([
        cam_id_arg,
        width_arg,
        height_arg,
        ocr_node,
        sub_node
    ])

