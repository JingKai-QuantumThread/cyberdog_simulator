# CyberDog simulator

该仿真平台使用gazebo plugin的形式，消除ros通信不同步对控制的影响。同时，提供了基于Rviz2的可视化工具，将机器人状态的lcm数据转发到ROS。
该仿真平台需和cyberdog_locomotion仓通信进行使用，建议通过cyberdog_sim仓进行安装

详细信息可参照[**仿真平台文档**](https://miroboticslab.github.io/blogs/#/cn/cyberdog_gazebo_cn)

推荐安装环境： Ubuntu 20.04 + ROS2 Galactic

## 依赖安装
运行仿真平台需要安装如下的依赖  
**ros2_Galactic** 
```
$ sudo apt update && sudo apt install curl gnupg lsb-release
$ sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
$ sudo apt update
$ sudo apt install ros-galactic-desktop
```
**Gazebo**
```
$ curl -sSL http://get.gazebosim.org | sh
$ sudo apt install ros-galactic-gazebo-ros
$ sudo apt install ros-galactic-gazebo-msgs
```
**LCM**
```
$ git clone https://github.com/lcm-proj/lcm.git
$ cd lcm
$ mkdir build
$ cd build
$ cmake -DLCM_ENABLE_JAVA=ON ..
$ make
$ sudo make install
```
**Eigen**
```
$ git clone https://github.com/eigenteam/eigen-git-mirror
$ cd eigen-git-mirror
$ mkdir build
$ cd build
$ cmake ..
$ sudo make install
```
**xacro**
```
$ sudo apt install ros-galactic-xacro
```

**vcstool**
```
$ sudo apt install python3-vcstool
```

**colcon**
```
$ sudo apt install python3-colcon-common-extensions
```

注意：若环境中安装有其他版本的yaml-cpp，可能会与ros galactic 自带的yaml-cpp发生冲突，建议编译时环境中无其他版本yaml-cpp

## 下载
```
$ git clone https://github.com/MiRoboticsLab/cyberdog_sim.git
$ cd cyberdog_sim
$ vcs import < cyberdog_sim.repos
```
## 编译
需要将src/cyberdog locomotion/CMakeLists.txt中的BUILD_ROS置为ON
然后需要在cyberdog_sim文件夹下进行编译
```
$ source /opt/ros/galactic/setup.bash 
$ colcon build --merge-install --symlink-install --packages-up-to cyberdog_locomotion cyberdog_simulator
```

## 使用
需要在cyberdog_sim文件夹下运行
```
$ python3 src/cyberdog_simulator/cyberdog_gazebo/script/launchsim.py
```

如果希望一键启动 Gazebo、RViz 和传感器自检，可使用：
```
$ python3 src/cyberdog_simulator/cyberdog_gazebo/script/launchall.py
```

如果当前仿真包含雷达，建议使用：
```
$ python3 src/cyberdog_simulator/cyberdog_gazebo/script/launchall.py --expect-lidar
```

可选参数示例：
```
$ python3 src/cyberdog_simulator/cyberdog_gazebo/script/launchall.py --gazebo-delay 6 --sensor-delay 12 --echo-timeout 12
```

### 也可以通过以下命令分别运行各程序：

首先启动gazebo程序，于cyberdog_sim文件夹下进行如下操作：
```
$ source /opt/ros/galactic/setup.bash
$ source install/setup.bash
$ ros2 launch cyberdog_gazebo gazebo.launch.py
```
也可通过如下命令打开激光雷达
```
$ source /opt/ros/galactic/setup.bash
$ source install/setup.bash
$ ros2 launch cyberdog_gazebo gazebo.launch.py use_lidar:=true
```

### 传感器对照表

当前机器人描述中的传感器与对应 ROS2 topic 如下：

| link | 传感器类型 | 插件 | 主要 topic |
| --- | --- | --- | --- |
| `imu_link` | IMU | `libgazebo_ros_imu_sensor.so` | `/imu` |
| `RGB_camera_link` | 单目 RGB 相机 | `libgazebo_ros_camera.so` | `/rgb_camera/image_raw` `/rgb_camera/camera_info` |
| `D435_camera_link` | 深度相机 | `libgazebo_ros_camera.so` | `/d435_camera/depth/image_raw` `/d435_camera/depth/depth_image_raw` `/d435_camera/depth/camera_info` `/d435_camera/depth/depth_camera_info` `/d435_camera/depth/points` |
| `AI_camera_link` | 双目相机 | `libgazebo_ros_camera.so` | `/ai_camera/left/image_raw` `/ai_camera/right/image_raw` `/ai_camera/left/camera_info` `/ai_camera/right/camera_info` |
| `lidar_link` | CPU 激光雷达 | `libgazebo_ros_ray_sensor.so` | `/lidar/scan` |
| `lidar_link` | GPU 激光雷达 | `libgazebo_ros_ray_sensor.so` | `/lidar_gpu/scan` |
| `FR_knee` | 足端接触 | `libfoot_contact_plugin.so` + `libgazebo_ros_bumper.so` | `/foot_contact/fr` |
| `FL_knee` | 足端接触 | `libfoot_contact_plugin.so` + `libgazebo_ros_bumper.so` | `/foot_contact/fl` |
| `RR_knee` | 足端接触 | `libfoot_contact_plugin.so` + `libgazebo_ros_bumper.so` | `/foot_contact/rr` |
| `RL_knee` | 足端接触 | `libfoot_contact_plugin.so` + `libgazebo_ros_bumper.so` | `/foot_contact/rl` |

说明：
- `use_lidar:=false` 时不会生成 `lidar_link` 上的两个雷达 topic。
- 足端接触除了上表 ROS topic 外，原有自定义 `libfoot_contact_plugin.so` 输出仍然保留。

### 如何调用传感器

在启动仿真后，可先查看所有传感器 topic：
```
$ source /opt/ros/galactic/setup.bash
$ source install/setup.bash
$ ros2 topic list | egrep 'imu|rgb_camera|d435_camera|ai_camera|lidar|foot_contact'
```

常用查看命令示例：
```
$ ros2 topic echo /imu
$ ros2 topic echo /lidar/scan
$ ros2 topic echo /lidar_gpu/scan
$ ros2 topic echo /foot_contact/fr
$ ros2 topic hz /rgb_camera/image_raw
$ ros2 topic hz /d435_camera/depth/image_raw
$ ros2 topic hz /ai_camera/left/image_raw
```

图像类 topic 可直接用如下方式查看：
```
$ ros2 run rqt_image_view rqt_image_view
```

在 `rqt_image_view` 中选择以下任一 topic：
```
/rgb_camera/image_raw
/d435_camera/depth/image_raw
/ai_camera/left/image_raw
/ai_camera/right/image_raw
```

点云可用如下命令确认是否在发布：
```
$ ros2 topic echo /d435_camera/depth/points --once
```

也可以直接运行传感器自检脚本：
```
$ source /opt/ros/galactic/setup.bash
$ source install/setup.bash
$ python3 src/cyberdog_simulator/cyberdog_gazebo/script/check_sensors.py
```

如果当前是以 `use_lidar:=true` 启动仿真，建议使用：
```
$ python3 src/cyberdog_simulator/cyberdog_gazebo/script/check_sensors.py --expect-lidar
```

自检脚本会检查：
- topic 是否存在
- topic 类型是否正确
- IMU、图像、点云、激光、足端接触等关键 topic 能否收到一条消息

可选参数：
```
$ python3 src/cyberdog_simulator/cyberdog_gazebo/script/check_sensors.py --echo-timeout 12 --topic-timeout 8
```

然后启动cyberdog_locomotion仓的控制程序。在cyberdog_sim文件夹下运行：
```
$ source /opt/ros/galactic/setup.bash
$ source install/setup.bash
$ ros2 launch cyberdog_gazebo cyberdog_control_launch.py
```

最后打开可视化界面，在cyberdog_sim文件夹下运行：
```
$ source /opt/ros/galactic/setup.bash
$ source install/setup.bash
$ ros2 launch cyberdog_visual cyberdog_visual.launch.py
```

### 播放实机lcm log数据
该平台能够通过rviz2将实机的运动控制lcm数据进行播放和可视化。  
操作方法如下：
运行lcm数据可视化界面，于cyberdog_sim文件夹下进行如下操作：
```
$ source /opt/ros/galactic/setup.bash
$ source install/setup.bash
$ ros2 launch cyberdog_visual cyberdog_lcm_repaly.launch.py
```
打开可视化界面后，通过运行cyberdog_locomotion仓的script目录下的脚本播放lcm log数据。  
于cyberdog_sim文件夹下进行如下操作：
```
$ cd src/cyberdog_locomotion/scripts
$ ./make_types.sh #初次使用时需要运行
$ ./launch_lcm_logplayer.sh
```
运行后选择需要播放的lcm log文件，即可进行log数据的播放，此时通过rviz可视化界面能复现机器人的姿态。
