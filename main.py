#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Will Brennan'


# Built-in Modules
import os
import logging
import argparse
# Standard Modules
import cv2
import numpy
# Custom Modules
import Scripts

logger = logging.getLogger('main')


def get_args(args_string=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--video_path', dest='video_path', required=True, type=str, help='path to load video from')
    parser.add_argument('-u', '--dump_path', dest='dump_path', type=str, help='path to save output data to')
    parser.add_argument('-i', '--dump_images', dest='dump_images', action='store_true', help='save images when motion event triggered')
    parser.add_argument('-o', '--offset', dest='offset', default=3, type=float, help='number of standard deviations allowed in normal range')
    parser.add_argument('-n', '--n_samples', dest='n_samples', default=1000, type=int, help='number of frames to determine standard deviation over')
    parser.add_argument('-m', '--n_min', dest='n_min', default=150, type=int, help='number of images before checking starts')
    parser.add_argument('-d', '--display', dest='display', action='store_true', help='display visual interface')
    parser.add_argument('-e', '--debug', dest='debug', action='store_true', help='set logger to debug')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='silence the logger')
    if isinstance(args_string, str):
        args_string = [arg for arg in args_string.split(' ') if arg != ""]
        args = parser.parse_args(args_string)
    else:
        args = parser.parse_args()
    return args


def frame_diff(img_vold, img_old, new_img):
    img_diff0 = cv2.absdiff(new_img, img_old)
    img_diff1 = cv2.absdiff(img_old, img_vold)
    return cv2.bitwise_or(img_diff0, img_diff1)

if __name__ == '__main__':
    args = get_args()
    logger = Scripts.get_logger(quiet=args.quiet, debug=args.debug)
    args.video_path = os.path.abspath(args.video_path)
    logger.debug('searching for frame at {0}'.format(args.video_path))
    assert os.path.exists(args.video_path), '{0} is not a valid path'.format(args.video_path)
    logger.info('loading video from {0}'.format(args.video_path))
    cam = cv2.VideoCapture(args.video_path)
    data = numpy.array([], dtype=float)
    frames = []
    frame_id = 0
    triggered = False
    while True:
        ret, frame = cam.read()
        if ret:
            frame_id += 1
            logger.debug('processing {0} frame'.format(frame_id))
            len_frame = len(frames)
            frames = [frame] + frames[:min(2, len(frames))]
            if len(frames) == 3:
                diff = frame_diff(frames[0], frames[1], frame)
                val = numpy.mean(diff)
                data = numpy.hstack(([val], data[:min(args.n_samples, data.shape[0])]))
                data_avg = numpy.mean(data)
                data_std = numpy.std(data)
                data_var = numpy.abs(val-data_avg)/data_std
                logger.debug('data_avg: {0}, data_std: {1}, data_var: {2}, value: {3}'.format(data_avg, data_std, data_var, val))
                critical = (data_var > args.offset) and (frame_id > args.n_min)
                if args.display:
                    msg0 = "avg: {0}, std: {0}, var: {1}".format(data_avg, data_std, data_var)
                    msg1 = "critical image: {0}".format(critical)
                    cv2.imshow('input frame', Scripts.display_message(frame, msg0, msg1))
                    cv2.imshow('frame_diff', Scripts.display_message(diff, msg0, msg1))
                if critical and not triggered:
                    triggered = True
                    logger.info('Significant Motion Detected on Frame {0}!'.format(frame_id))
                    if args.dump_images:
                        img_path = '{0}_inputFrame.png'.format(frame_id)
                        dif_path = '{0}_diffFrame.png'.format(frame_id)
                        if args.dump_path:
                            img_path = os.path.join(args.dump_path, img_path)
                            dif_path = os.path.join(args.dump_path, dif_path)
                        logger.debug('saving inputFrame to {0}'.format(img_path))
                        logger.debug('saving diffFrame to {0}'.format(dif_path))
                        cv2.imwrite(img_path, frame)
                        assert os.path.exists(img_path), 'inputFrame did not save correctly'
                        cv2.imwrite(dif_path, diff)
                        assert os.path.exists(dif_path), 'diffFrame did not save correctly'
                    cv2.waitKey(0)
                elif not critical and triggered:
                    logger.info('event has stopped occurring')
                    triggered = False
                else:
                    logger.debug('nothing to report')
                if args.display:
                    cv2.waitKey(1)
        else:
            break



