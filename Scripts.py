#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Will Brennan'


# Built-in Modules
import logging
import argparse
import platform
import subprocess
# Standard Modules
import cv2
import numpy
# Custom Modules


logger = logging.getLogger('main')


def get_resolution():
    os_name = platform.system()
    res = [1280, 720]
    try:
        if os_name == 'Windows':
            command = "wmic desktopmonitor get screenheight, screenwidth"
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            data = proc.stdout.readlines()
            data = filter(lambda i: i != '', data[1].split(' '))
            res = [float(data[1]), float(data[0])]
        elif os_name == 'Linux':
            command = "xdpyinfo  | grep dimensions"
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            data = proc.stdout.readlines()
            data = filter(lambda i: i != '', data[0].split(' '))
            res = [float(i) for i in data[1].split('x')]
    except Exception as e:
        logger.warning("Failed to determine screen size")
        logger.warning("Error: {0}".format(e))
    return res


def get_logger(level=logging.INFO, quiet=False, debug=False, to_file=''):
    """
    This function initialises a logger to stdout.
    :return: logger
    """
    assert level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.CRITICAL]
    logger = logging.getLogger('main')
    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    if debug:
        level = logging.DEBUG
    logger.setLevel(level=level)
    if not quiet:
        if to_file:
            fh = logging.FileHandler(to_file)
            fh.setLevel(level=level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        else:
            ch = logging.StreamHandler()
            ch.setLevel(level=level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
    return logger


def resize(frame, max_size=2000000, full_screen=False):
    if full_screen:
        logger.debug('determining screen size')
        w, h = get_resolution()
        logger.debug("Screen Size - {0}px x {1}px".format(w, h))
        ratio_w = w/frame.shape[1]
        ratio_h = h/frame.shape[0]
        print ratio_h, ratio_w
        logger.debug("Frame Size: {0}".format(frame.shape[:2]))
        logger.debug("Resize Ratios - {0} and {1}".format(ratio_w, ratio_h))
        scale = min(0.8*ratio_w, 0.8*ratio_h, 1)
        logger.debug("Scale Ratio: {0}".format(scale))
    else:
        scale = numpy.sqrt(min(1.0, float(max_size)/(frame.shape[0]*frame.shape[1])))
    shape = (int(scale*frame.shape[1]), int(scale*frame.shape[0]))
    return cv2.resize(frame, shape)


def display_message(frame, msg0, msg1, max_size=2000000):
    assert isinstance(frame, numpy.ndarray), 'frame must be a nump.ndarray not {0}'.format(type(frame))
    frame = resize(frame, max_size=max_size)
    if frame.ndim == 3:
        frame[-30:, :, :] *= 0.5
        for i, line in enumerate(reversed([msg0, msg1])):
            cv2.putText(frame, line, (10, frame.shape[0]-(5+13*i)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 250), 1, 8)
        return frame
    else:
        frame[-30:, :] = 255
        for i, line in enumerate(reversed([msg0, msg1])):
            cv2.putText(frame, line, (10, frame.shape[0]-(5+13*i)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 20, 1, 8)
        return frame
