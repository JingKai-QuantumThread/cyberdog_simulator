#!/usr/bin/env python3

# Copyright (c) 2023-2023 Beijing Xiaomi Mobile Software Co., Ltd. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shlex
import sys
import time

VISUAL_ARG_NAMES = {
    'use_sim_time',
    'hang_robot',
    'use_lidar',
    'use_realsense_camera',
    'use_stereo_camera',
    'use_ai_camera',
    'rname',
}


def _quote_cmd(script_path, extra_args):
    cmd = f'bash {script_path}'
    if extra_args:
        cmd += ' ' + ' '.join(shlex.quote(arg) for arg in extra_args)
    return cmd


def _select_visual_args(extra_args):
    visual_args = []
    for arg in extra_args:
        if ':=' not in arg:
            continue
        name, _ = arg.split(':=', 1)
        if name in VISUAL_ARG_NAMES:
            visual_args.append(arg)
    return visual_args


def launchsim(extra_args):
    gazebo_cmd = _quote_cmd('./src/cyberdog_simulator/cyberdog_gazebo/script/launchgazebo.sh', extra_args)
    visual_cmd = _quote_cmd(
        './src/cyberdog_simulator/cyberdog_gazebo/script/launchvisual.sh',
        _select_visual_args(extra_args))

    os.system(f'NO_AT_BRIDGE=1 gnome-terminal --title="cyberdog_gazebo" -- bash -c "{gazebo_cmd}"')
    time.sleep(5)
    os.system(f'NO_AT_BRIDGE=1 gnome-terminal --title="cyberdog_viusal" -- bash -c "{visual_cmd}"')
    os.system('NO_AT_BRIDGE=1 gnome-terminal --title="cyberdog_control" -- bash -c "bash ./src/cyberdog_simulator/cyberdog_gazebo/script/launchcontrol.sh"')


if __name__ == "__main__":
    launchsim(sys.argv[1:])
