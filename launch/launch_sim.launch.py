import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    # Package name
    package_name = 'articubot_one'  # Make sure this is your correct package name
    
    # Path to the parameter file for SLAM
    slam_params = os.path.join(
        get_package_share_directory(package_name), 
        'config', 
        'mapper_params_online_async.yaml'  # Ensure this file exists in the specified path
    )

    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                #launch_arguments={'world': os.path.join(get_package_share_directory(package_name), 'worlds', 'NewWorld.world')}.items()  # Update to use your world file
    )

    # Run the spawner node from the gazebo_ros package
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'box_bot'],#<--- เปลี่ยนชื่อหุ่นยนต์ตรงนี้
                        output='screen')

    # Launch SLAM tool with parameters from the provided YAML file
    slam = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('slam_toolbox'),'launch','online_async_launch.py'
                )]), 
                launch_arguments={'use_sim_time': 'true', 'params_file': slam_params}.items()
    )
    

    # Node for twist_mux
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        output='screen',
        parameters=[
            os.path.join(
                get_package_share_directory(package_name), 
                'config', 
                'twist_mux.yaml'  # Ensure this file exists in the specified path
            )
        ],
        remappings=[
            ('cmd_vel_out', 'diff_cont/cmd_vel_unstamped')  # Remap output topic
        ]
    )
    
    
    controller_manager = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "gripper_controller",
        ],
    )
    
    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        #slam,
        twist_mux,
        #controller_manager,
    ])