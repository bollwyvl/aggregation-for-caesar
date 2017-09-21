'''
Polygon As Line Tool for Text Extractor
---------------------------------------
This module provides a fuction of eaxtract panoptes annotations
from porjects using a polygon tool to mark word in a transcribed
document and provide the transcribed text as a sub-task.
'''
from collections import OrderedDict
import copy
import numpy as np
from .extractor_wrapper import extractor_wrapper


@extractor_wrapper
def poly_line_text_extractor(classification):
    '''Extract annotations from a polygon tool with a text sub-task

    Parameters
    ----------
    classification : dict
        A dictionary containing an `annotations` key that is a list of
        panoptes annotations

    Returns
    -------
    extraction : dict
        A dictionary with one key for each `frame`. The value for each frame
        is a dict with `text`, a list-of-lists of transcribe words, `points`, a
        dict with the list-of-lists of `x` and `y` postions of each word, and
        `slope`, a list of the slopes (in deg) of each line drawn.
        For `points` and `text` there is one inner list for each annotaiton made
        on the frame.

    Examples
    --------
    >>> classification = {'annotations': [
        'value': [
            {
                'frame': 0,
                'points': [
                    {'x': 756, 'y': 197}
                ],
                'details': [
                    {'value': '[unclear]Cipher[/unclear]'}
                ],
            },
            {
                'frame': 0,
                'points': [
                    {'x': 756, 'y': 97},
                    {'x': 856, 'y': 97}
                ],
                'details': [
                    {'value': 'A word'}
                ],
            }
    ]}
    >>> poly_line_text_extractor(classification)
    {'frame0': {
        'points': {'x': [[756], [756, 856]], 'y': [[197], [97, 97]]},
        'text': [['[unclear]Cipher[/unclear]'], ['A', 'word']]
        'slope': [0, 0]
    }}
    '''
    blank_frame = OrderedDict([
        ('points', OrderedDict([('x', []), ('y', [])])),
        ('text', []),
        ('slope', [])
    ])
    extract = OrderedDict()
    annotation = classification['annotations'][0]
    for value in annotation['value']:
        frame = 'frame{0}'.format(value['frame'])
        extract.setdefault(frame, copy.deepcopy(blank_frame))
        text = value['details'][0]['value']
        words = text.split(' ')
        x = [point['x'] for point in value['points']]
        y = [point['y'] for point in value['points']]
        if len(x) > 1:
            fit = np.polyfit(x, y, 1)
            y_fit = np.polyval(fit, [x[0], x[-1]])
            dx = x[-1] - x[0]
            dy = y_fit[-1] - y_fit[0]
            slope = np.rad2deg(np.arctan2(dy, dx))
        else:
            # default the slope to 0 if only one point was drawn
            slope = 0
        # NOTE: if `words` and `points` are differnt lengths
        # the extract is not used
        if len(words) == len(x):
            extract[frame]['text'].append(words)
            extract[frame]['points']['x'].append(x)
            extract[frame]['points']['y'].append(y)
            extract[frame]['slope'].append(slope)
    return extract