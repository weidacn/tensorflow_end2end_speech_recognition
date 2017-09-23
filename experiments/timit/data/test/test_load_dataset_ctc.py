#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import os
import sys
import unittest

sys.path.append(os.path.abspath('../../../../'))
from experiments.timit.data.load_dataset_ctc import Dataset
from utils.io.labels.character import idx2char
from utils.io.labels.phone import idx2phone
from utils.measure_time_func import measure_time


class TestLoadDatasetCTC(unittest.TestCase):

    def test(self):

        self.length_check = False

        # data_type
        self.check_loading(label_type='phone61', data_type='train')
        self.check_loading(label_type='phone61', data_type='dev')
        self.check_loading(label_type='phone61', data_type='test')

        # label_type
        self.check_loading(label_type='phone61')
        self.check_loading(label_type='character')
        self.check_loading(label_type='character_capital_divide')

        # sort
        self.check_loading(label_type='phone61', sort_utt=True)
        self.check_loading(label_type='phone61', sort_utt=True,
                           sort_stop_epoch=2)
        self.check_loading(label_type='phone61', shuffle=True)

        # frame stacking
        self.check_loading(label_type='phone61', frame_stacking=True)

        # splicing
        self.check_loading(label_type='phone61', splice=11)

    @measure_time
    def check_loading(self, label_type, data_type='dev',
                      shuffle=False, sort_utt=False, sort_stop_epoch=None,
                      frame_stacking=False, splice=1):

        print('========================================')
        print('  label_type: %s' % label_type)
        print('  data_type: %s' % data_type)
        print('  shuffle: %s' % str(shuffle))
        print('  sort_utt: %s' % str(sort_utt))
        print('  sort_stop_epoch: %s' % str(sort_stop_epoch))
        print('  frame_stacking: %s' % str(frame_stacking))
        print('  splice: %d' % splice)
        print('========================================')

        num_stack = 3 if frame_stacking else 1
        num_skip = 3 if frame_stacking else 1
        dataset = Dataset(
            data_type=data_type, label_type=label_type,
            batch_size=64, max_epoch=2, splice=splice,
            num_stack=num_stack, num_skip=num_skip,
            shuffle=shuffle,
            sort_utt=sort_utt, sort_stop_epoch=sort_stop_epoch,
            progressbar=True)

        print('=> Loading mini-batch...')
        map_file_path = '../../metrics/mapping_files/ctc/' + label_type + '.txt'
        if label_type in ['character', 'character_capital_divide']:
            map_fn = idx2char
        else:
            map_fn = idx2phone

        for data, is_new_epoch in dataset:
            inputs, labels, inputs_seq_len, input_names = data

            if not self.length_check:
                for i, l in zip(inputs[0], labels[0]):
                    if len(i) < len(l):
                        raise ValueError(
                            'input length must be longer than label length.')
                self.length_check = True

            str_true = map_fn(labels[0], map_file_path)
            str_true = re.sub(r'_', ' ', str_true)
            print('----- %s -----' % input_names[0])
            print(inputs[0].shape)
            print(str_true)


if __name__ == '__main__':
    unittest.main()
