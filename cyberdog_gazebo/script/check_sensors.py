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
import shutil
import subprocess
import sys
import time
from typing import Dict, List, Tuple


TOPIC_SPECS = [
    {
        'name': '/imu',
        'type': 'sensor_msgs/msg/Imu',
        'required': True,
        'sample': True,
        'desc': 'IMU',
    },
    {
        'name': '/rgb_camera/image_raw',
        'type': 'sensor_msgs/msg/Image',
        'required': True,
        'sample': True,
        'desc': 'RGB image',
    },
    {
        'name': '/rgb_camera/camera_info',
        'type': 'sensor_msgs/msg/CameraInfo',
        'required': True,
        'sample': False,
        'desc': 'RGB camera info',
    },
    {
        'name': '/d435_camera/depth/image_raw',
        'type': 'sensor_msgs/msg/Image',
        'required': True,
        'sample': True,
        'desc': 'Depth camera color image',
    },
    {
        'name': '/d435_camera/depth/depth_image_raw',
        'type': 'sensor_msgs/msg/Image',
        'required': True,
        'sample': True,
        'desc': 'Depth image',
    },
    {
        'name': '/d435_camera/depth/camera_info',
        'type': 'sensor_msgs/msg/CameraInfo',
        'required': True,
        'sample': False,
        'desc': 'Depth camera info',
    },
    {
        'name': '/d435_camera/depth/depth_camera_info',
        'type': 'sensor_msgs/msg/CameraInfo',
        'required': True,
        'sample': False,
        'desc': 'Depth camera depth info',
    },
    {
        'name': '/d435_camera/depth/points',
        'type': 'sensor_msgs/msg/PointCloud2',
        'required': True,
        'sample': True,
        'desc': 'Depth point cloud',
    },
    {
        'name': '/ai_camera/left/image_raw',
        'type': 'sensor_msgs/msg/Image',
        'required': True,
        'sample': True,
        'desc': 'Stereo left image',
    },
    {
        'name': '/ai_camera/right/image_raw',
        'type': 'sensor_msgs/msg/Image',
        'required': True,
        'sample': True,
        'desc': 'Stereo right image',
    },
    {
        'name': '/ai_camera/left/camera_info',
        'type': 'sensor_msgs/msg/CameraInfo',
        'required': True,
        'sample': False,
        'desc': 'Stereo left camera info',
    },
    {
        'name': '/ai_camera/right/camera_info',
        'type': 'sensor_msgs/msg/CameraInfo',
        'required': True,
        'sample': False,
        'desc': 'Stereo right camera info',
    },
    {
        'name': '/lidar/scan',
        'type': 'sensor_msgs/msg/LaserScan',
        'required': False,
        'sample': True,
        'desc': 'CPU lidar scan',
    },
    {
        'name': '/lidar_gpu/scan',
        'type': 'sensor_msgs/msg/LaserScan',
        'required': False,
        'sample': True,
        'desc': 'GPU lidar scan',
    },
    {
        'name': '/foot_contact/fr',
        'type': 'gazebo_msgs/msg/ContactsState',
        'required': True,
        'sample': True,
        'desc': 'Front-right foot contact',
    },
    {
        'name': '/foot_contact/fl',
        'type': 'gazebo_msgs/msg/ContactsState',
        'required': True,
        'sample': True,
        'desc': 'Front-left foot contact',
    },
    {
        'name': '/foot_contact/rr',
        'type': 'gazebo_msgs/msg/ContactsState',
        'required': True,
        'sample': True,
        'desc': 'Rear-right foot contact',
    },
    {
        'name': '/foot_contact/rl',
        'type': 'gazebo_msgs/msg/ContactsState',
        'required': True,
        'sample': True,
        'desc': 'Rear-left foot contact',
    },
]


def run_command(cmd: List[str], timeout: float) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )


def check_ros2_cli() -> None:
    if shutil.which('ros2') is None:
        print('ros2 command not found. Please source ROS 2 and your workspace first.')
        sys.exit(2)


def get_topic_types(timeout: float) -> Dict[str, str]:
    result = run_command(['ros2', 'topic', 'list', '-t'], timeout)
    if result.returncode != 0:
        print('Failed to query topic list:')
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(2)

    topic_types: Dict[str, str] = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if '[' not in line or ']' not in line:
            continue
        topic_name, raw_type = line.split('[', 1)
        topic_types[topic_name.strip()] = raw_type.rstrip('] ').strip()
    return topic_types


def echo_once(topic_name: str, timeout: float) -> Tuple[bool, str]:
    process = subprocess.Popen(
        ['ros2', 'topic', 'echo', topic_name, '--spin-time', str(timeout)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            line = process.stdout.readline()
            if line:
                process.terminate()
                try:
                    process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                return True, 'message received'

            if process.poll() is not None:
                break

            time.sleep(0.1)

        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=1.0)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()

        detail = (stderr or stdout).strip()
        return False, detail or 'no message received before timeout'
    finally:
        if process.poll() is None:
            process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Check whether CyberDog simulator sensor topics are available.'
    )
    parser.add_argument(
        '--expect-lidar',
        action='store_true',
        help='Treat lidar topics as required.',
    )
    parser.add_argument(
        '--topic-timeout',
        type=float,
        default=5.0,
        help='Timeout in seconds for ros2 topic list commands.',
    )
    parser.add_argument(
        '--echo-timeout',
        type=float,
        default=8.0,
        help='Timeout in seconds when waiting for one message on sampled topics.',
    )
    args = parser.parse_args()

    check_ros2_cli()
    topic_types = get_topic_types(args.topic_timeout)

    failures = 0
    warnings = 0

    print('CyberDog sensor self-check')
    print('-' * 72)

    for spec in TOPIC_SPECS:
        required = spec['required'] or (
            args.expect_lidar and spec['name'] in ('/lidar/scan', '/lidar_gpu/scan')
        )

        topic_name = spec['name']
        expected_type = spec['type']
        actual_type = topic_types.get(topic_name)

        if actual_type is None:
            level = 'FAIL' if required else 'WARN'
            print(f'[{level}] {topic_name} ({spec["desc"]}) not found')
            if required:
                failures += 1
            else:
                warnings += 1
            continue

        if actual_type != expected_type:
            print(
                f'[FAIL] {topic_name} type mismatch: '
                f'expected {expected_type}, got {actual_type}'
            )
            failures += 1
            continue

        print(f'[OK]   {topic_name} type={actual_type}')

        if spec['sample']:
            ok, detail = echo_once(topic_name, args.echo_timeout)
            if ok:
                print(f'       sample check: {detail}')
            else:
                print(f'       sample check: FAIL ({detail})')
                failures += 1

    print('-' * 72)
    print(
        f'Summary: {len(TOPIC_SPECS) - warnings - failures} ok, '
        f'{warnings} warning, {failures} failure'
    )

    if failures:
        print('Self-check failed. Make sure Gazebo is running and the robot is spawned.')
        return 1

    if warnings:
        print('Self-check passed with warnings.')
        return 0

    print('Self-check passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
