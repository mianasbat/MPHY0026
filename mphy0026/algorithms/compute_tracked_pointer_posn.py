# -*- coding: utf-8 -*-

import numpy as np


def _get_aruco_item_index(handles, value):
    """
    From an array of handles, returns the index that matches the given value.
    :param handles: handles of tracked items returned from ArUco tracker.
    :param value: value to search for, essentially, a tag number
    :return: None or array index.
    """
    if handles is None or not handles:
        return None

    index_of_item = np.where(handles == value)

    if index_of_item is None or not index_of_item:
        return None

    return index_of_item[0]


def compute_tracked_pointer_posn(tracker_frame,
                                 tracker_type,
                                 pointer,
                                 reference,
                                 offset):
    """
    Computes the pointer position, or returns None if not enough items tracked.
    :param tracker_frame: tracker frame
    :param tracker_type: tracker type must be [vega|aurora|aruco]
    :param pointer: config information for pointer
    :param reference: optional config information for reference
    :param offset: 4x1 tip offset in pointer coordinate system
    :return: 1x3 ndarray of pointer tip
    """
    if tracker_frame is None:
        raise ValueError("Failed to get data from tracker.")
    if not tracker_frame[4]: # ArUco returns empty list
        return None

    pointer_posn = None
    pointer_index = 0
    reference_index = 1
    tracking_pointer = False
    tracking_reference = False

    if tracker_type == 'aruco':
        pointer_index = _get_aruco_item_index(tracker_frame[0], pointer)
        reference_index = _get_aruco_item_index(tracker_frame[0], reference)

    if not np.isnan(tracker_frame[4][pointer_index]):
        tracking_pointer = True

    if reference is not None \
            and not np.isnan(tracker_frame[4][pointer_index]) \
            and not np.isnan(tracker_frame[4][reference_index]):
        tracking_reference = True

    if tracking_pointer:
        pointer_to_world = tracker_frame[3][pointer_index]
        world_point = np.matmul(pointer_to_world, offset)
        world_point_transposed = (np.transpose(world_point))[0, 0:3]
        pointer_posn = world_point_transposed
    elif tracking_reference:
        pointer_to_world = tracker_frame[3][pointer_index]
        reference_to_world = tracker_frame[3][reference_index]
        world_to_reference = np.linalg.inv(reference_to_world)
        pointer_in_world = np.matmul(pointer_to_world,
                                     offset)
        pointer_in_ref = np.matmul(world_to_reference,
                                   pointer_in_world)
        pointer_in_ref_transposed = \
            (np.transpose(pointer_in_ref))[0, 0:3]
        pointer_posn = pointer_in_ref_transposed

    return pointer_posn
