import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('point_lio')
    config_file = os.path.join(pkg_dir, 'config', 'velody16.yaml')
    rviz_cfg = os.path.join(pkg_dir, 'rviz_cfg', 'loam_livox.rviz')

    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='true', description='Launch RViz2'
    )

    mapping_node = Node(
        package='point_lio',
        executable='pointlio_mapping',
        name='laserMapping',
        output='screen',
        parameters=[config_file],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_cfg],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        rviz_arg,
        mapping_node,
        rviz_node,
    ])
