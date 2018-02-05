import unittest
import copy
from panoptes_aggregation.extractors import filter_annotations

annotation = [
    {
        'task': 'T0',
        'task_label': 'Please mark the galaxy centre(s) and any foreground stars you see.',
        'value': [
            {
                'details': [],
                'frame': 0,
                'tool': 0,
                'tool_label': 'Galaxy center',
                'x': 261,
                'y': 266
            }, {
                'details': [
                    {'value': 1},
                    {'value': [0, 1]}
                ],
                'frame': 0,
                'tool': 2,
                'tool_label': 'Foreground Star',
                'x': 270,
                'y': 341
            }, {
                'details': [],
                'frame': 0,
                'tool': 1,
                'tool_label': 'A line',
                'x1': 714.84,
                'y1': 184.78,
                'x2': 446.35,
                'y2': 278.33
            }
        ]
    }, {
        'task': 'T1',
        'task_label': 'A single question',
        'value': 'Yes'
    }, {
        'task': 'T2',
        'task_label': 'A multi question',
        'value': ['Blue', 'Green']
    }, {
        'task': 'T3',
        'task_label': 'Transcribe',
        'value': [
            {
                'type': 'graphic',
                'tag': '<graphic>word</graphic>'
            },
            {
                'type': 'text',
                'text': 'All the words'
            }
        ]
    }
]

config = {
    'T0': {
        'line_extractor': {
            'tool': [1],
            'details': {}
        },
        'point_extractor': {
            'tool': [
                0,
                2
            ],
            'details': {
                'T0_tool2': [
                    'question_extractor',
                    'question_extractor'
                ]
            }
        }
    },
    'T1': 'question_extractor',
    'T2': 'question_extractor',
    'T3': ['sw_extractor', 'sw_graphic_extractor']
}


class TestFilterAnnotations(unittest.TestCase):
    def setUp(self):
        self.annotation = copy.deepcopy(annotation)
        self.maxDiff = None

    def test_filter(self):
        '''Test annotation filter: Test with no task labels'''
        expected_result = {
            'line_extractor': {
                'annotations': [{
                    'task': 'T0',
                    'value': [{
                        'details': [],
                        'frame': 0,
                        'tool': 1,
                        'x1': 714.84,
                        'y1': 184.78,
                        'x2': 446.35,
                        'y2': 278.33
                    }]
                }],
                'config': {}
            },
            'point_extractor': {
                'annotations': [{
                    'task': 'T0',
                    'value': [{
                        'details': [],
                        'frame': 0,
                        'tool': 0,
                        'x': 261,
                        'y': 266
                    }, {
                        'details': [
                            {'value': 1},
                            {'value': [0, 1]}
                        ],
                        'frame': 0,
                        'tool': 2,
                        'x': 270,
                        'y': 341
                    }]
                }],
                'config': {
                    'details': {
                        'T0_tool2': [
                            'question_extractor',
                            'question_extractor'
                        ]
                    }
                }
            },
            'question_extractor': {
                'annotations': [{
                    'task': 'T1',
                    'value': 'Yes'
                }, {
                    'task': 'T2',
                    'value': ['Blue', 'Green']
                }]
            },
            'sw_extractor': {
                'annotations': [{
                    'task': 'T3',
                    'value': [
                        {
                            'type': 'graphic',
                            'tag': '<graphic>word</graphic>'
                        },
                        {
                            'type': 'text',
                            'text': 'All the words'
                        }
                    ]
                }]
            },
            'sw_graphic_extractor': {
                'annotations': [{
                    'task': 'T3',
                    'value': [
                        {
                            'type': 'graphic',
                            'tag': '<graphic>word</graphic>'
                        },
                        {
                            'type': 'text',
                            'text': 'All the words'
                        }
                    ]
                }]
            }
        }
        result = filter_annotations(self.annotation, config)
        self.assertDictEqual(result, expected_result)

    def test_filter_human(self):
        '''Test annotation filter: Test with task labels'''
        expected_result = {
            'line_extractor': {
                'annotations': [{
                    'task': 'T0',
                    'task_label': 'Please mark the galaxy centre(s) and any foreground stars you see.',
                    'value': [{
                        'details': [],
                        'frame': 0,
                        'tool': 1,
                        'tool_label': 'A line',
                        'x1': 714.84,
                        'y1': 184.78,
                        'x2': 446.35,
                        'y2': 278.33
                    }]
                }],
                'config': {}
            },
            'point_extractor': {
                'annotations': [{
                    'task': 'T0',
                    'task_label': 'Please mark the galaxy centre(s) and any foreground stars you see.',
                    'value': [{
                        'details': [],
                        'frame': 0,
                        'tool': 0,
                        'tool_label': 'Galaxy center',
                        'x': 261,
                        'y': 266
                    }, {
                        'details': [
                            {'value': 1},
                            {'value': [0, 1]}
                        ],
                        'frame': 0,
                        'tool': 2,
                        'tool_label': 'Foreground Star',
                        'x': 270,
                        'y': 341
                    }]
                }],
                'config': {
                    'details': {
                        'T0_tool2': [
                            'question_extractor',
                            'question_extractor'
                        ]
                    }
                }
            },
            'question_extractor': {
                'annotations': [{
                    'task': 'T1',
                    'task_label': 'A single question',
                    'value': 'Yes'
                }, {
                    'task': 'T2',
                    'task_label': 'A multi question',
                    'value': ['Blue', 'Green']
                }]
            },
            'sw_extractor': {
                'annotations': [{
                    'task': 'T3',
                    'task_label': 'Transcribe',
                    'value': [
                        {
                            'type': 'graphic',
                            'tag': '<graphic>word</graphic>'
                        },
                        {
                            'type': 'text',
                            'text': 'All the words'
                        }
                    ]
                }]
            },
            'sw_graphic_extractor': {
                'annotations': [{
                    'task': 'T3',
                    'task_label': 'Transcribe',
                    'value': [
                        {
                            'type': 'graphic',
                            'tag': '<graphic>word</graphic>'
                        },
                        {
                            'type': 'text',
                            'text': 'All the words'
                        }
                    ]
                }]
            }
        }
        result = filter_annotations(self.annotation, config, human=True)
        self.assertDictEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
