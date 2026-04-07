#!/usr/bin/env python3

# Copyright (c) 2023-2023 Beijing Xiaomi Mobile Software Co., Ltd.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import shlex
import subprocess
import sys
import time


def run_terminal(title: str, command: str, workspace: str) -> None:
    terminal_cmd = [
        'gnome-terminal',
        '--title',
        title,
        '--',
        'bash',
        '-lc',
        f'cd {shlex.quote(workspace)} && {command}; exec bash',
    ]
    subprocess.Popen(terminal_cmd)


def build_launch_args(enable_lidar: bool, enable_realsense: bool, enable_stereo: bool, enable_ai: bool) -> str:
    args = []
    if enable_lidar:
        args.append('use_lidar:=true')
    if enable_realsense:
        args.append('use_realsense_camera:=true')
    if enable_stereo:
        args.append('use_stereo_camera:=true')
    if enable_ai:
        args.append('use_ai_camera:=true')
    return ' '.join(args)


def build_sensor_command(expect_lidar: bool, echo_timeout: float, topic_timeout: float) -> str:
    cmd = [
        'source /opt/ros/galactic/setup.bash',
        'source install/setup.bash',
        'python3 src/cyberdog_simulator/cyberdog_gazebo/script/check_sensors.py',
    ]

    if expect_lidar:
        cmd[-1] += ' --expect-lidar'
    if echo_timeout != 8.0:
        cmd[-1] += f' --echo-timeout {echo_timeout}'
    if topic_timeout != 5.0:
        cmd[-1] += f' --topic-timeout {topic_timeout}'
    return '; '.join(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Launch Gazebo, RViz, and sensor self-check in separate terminals.'
    )
    parser.add_argument(
        '--workspace',
        default='/home/cyberdog_sim',
        help='CyberDog simulator workspace root.',
    )
    parser.add_argument(
        '--gazebo-delay',
        type=float,
        default=5.0,
        help='Seconds to wait after Gazebo launch before starting RViz.',
    )
    parser.add_argument(
        '--sensor-delay',
        type=float,
        default=8.0,
        help='Seconds to wait after Gazebo launch before running sensor self-check.',
    )
    parser.add_argument(
        '--disable-lidar',
        action='store_true',
        help='Do not enable lidar topics during launch.',
    )
    parser.add_argument(
        '--disable-realsense',
        action='store_true',
        help='Do not enable RealSense topics during launch.',
    )
    parser.add_argument(
        '--disable-stereo',
        action='store_true',
        help='Do not enable stereo topics during launch.',
    )
    parser.add_argument(
        '--disable-ai-camera',
        action='store_true',
        help='Do not enable AI camera topics during launch.',
    )
    parser.add_argument(
        '--echo-timeout',
        type=float,
        default=8.0,
        help='Forwarded to check_sensors.py.',
    )
    parser.add_argument(
        '--topic-timeout',
        type=float,
        default=5.0,
        help='Forwarded to check_sensors.py.',
    )
    args = parser.parse_args()

    workspace = os.path.abspath(args.workspace)
    if not os.path.isdir(workspace):
        print(f'workspace not found: {workspace}')
        return 2

    enable_lidar = not args.disable_lidar
    enable_realsense = not args.disable_realsense
    enable_stereo = not args.disable_stereo
    enable_ai = not args.disable_ai_camera
    launch_args = build_launch_args(
        enable_lidar,
        enable_realsense,
        enable_stereo,
        enable_ai,
    )

    gazebo_script = os.path.join(
        workspace,
        'src/cyberdog_simulator/cyberdog_gazebo/script/launchgazebo.sh',
    )
    visual_script = os.path.join(
        workspace,
        'src/cyberdog_simulator/cyberdog_gazebo/script/launchvisual.sh',
    )
    sensor_script = os.path.join(
        workspace,
        'src/cyberdog_simulator/cyberdog_gazebo/script/check_sensors.py',
    )

    for path in (gazebo_script, visual_script, sensor_script):
        if not os.path.exists(path):
            print(f'required file not found: {path}')
            return 2

    run_terminal(
        'cyberdog_gazebo',
        f'bash ./src/cyberdog_simulator/cyberdog_gazebo/script/launchgazebo.sh {launch_args}'.strip(),
        workspace,
    )

    time.sleep(args.gazebo_delay)

    run_terminal(
        'cyberdog_visual',
        f'bash ./src/cyberdog_simulator/cyberdog_gazebo/script/launchvisual.sh {launch_args}'.strip(),
        workspace,
    )

    remaining_delay = max(0.0, args.sensor_delay - args.gazebo_delay)
    if remaining_delay > 0.0:
        time.sleep(remaining_delay)

    run_terminal(
        'cyberdog_control',
        'bash ./src/cyberdog_simulator/cyberdog_gazebo/script/launchcontrol.sh',
        workspace,
    )
    time.sleep(5)

    run_terminal(
        'cyberdog_sensors',
        build_sensor_command(
            enable_lidar,
            args.echo_timeout,
            args.topic_timeout,
        ),
        workspace,
    )

    

    return 0


if __name__ == '__main__':
    sys.exit(main())
