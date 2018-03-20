# _*_ coding: utf-8 _*_
import os
import json
from types import SimpleNamespace

import yaml


class Setting(object):
    app_setting = os.path.dirname(os.path.abspath(__file__)) + "/setting.yaml"


def config(path, is_yaml=True):
        with open(path, "r") as fp:
            if is_yaml:
                res = json.loads(
                    json.dumps(
                    yaml.safe_load(fp)),
                    object_hook=lambda d: SimpleNamespace(**d))
            else:
                res = json.loads(
                    fp.read(),
                    object_hook=lambda d:SimpleNamespace(**d))
        return res
