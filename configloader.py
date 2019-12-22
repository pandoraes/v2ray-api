#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,yaml


def load_config():
    config_file = os.environ['CONFIGPATH']
    with open(config_file) as f:
        config = yaml.load(f.read())
    return config
