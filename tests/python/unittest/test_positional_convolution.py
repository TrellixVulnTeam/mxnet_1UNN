# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# pylint: skip-file
from __future__ import print_function
import numpy as np
import mxnet as mx
from mxnet.test_utils import *
import unittest
import itertools


def test_positional_convolution_forward(ctx):
    """
    Test positional convolution forward.
    """
    # num_batch * channel * height * width input
    # i.e. (2, 2, 6, 6)
    in_data = \
    mx.nd.array(
    [
    [[[1, 2, -1, 0, 1, 1],
     [3, 6, -5, 4, 2, -2],
     [9, 6, -1, 3, 1, 3],
     [4, 2, 5, 7, 3, 1],
     [0, 1, 1, 2, 2, 1],
     [3, 1, 2, 4, 3, 3]],

     [[3, 1, 2, 4, 3, 3],
     [0, 1, 1, 2, 2, 1],
     [4, 2, 5, 7, 3, 1],
     [9, 6, -1, 3, 1, 3],
     [3, 6, -5, 4, 2, -2],
     [1, 2, -1, 0, 1, 1]]],
    [[[1, 2, 3, 4, 5, 6],
      [6, 5, 4, 3, 2, 1],
      [0, 0, 1, 1, 2, 2],
      [3, 3, 0, -1, -1, -2],
      [3, 1, 0, 3, 3, 2],
      [5, 6, 7, -1, -2, 0]],

      [[5, 6, 7, -1, -2, 0],
      [3, 1, 0, 3, 3, 2],
      [3, 3, 0, -1, -1, -2],
      [0, 0, 1, 1, 2, 2],
      [6, 5, 4, 3, 2, 1],
      [1, 2, 3, 4, 5, 6]]]
    ], ctx=ctx)

    # num_filter * channel * K * K weight
    # i.e. (2, 2, 3, 3)
    weight = \
    mx.nd.array(
    [
    [[[1, 0, 1],
     [0, 2, -1],
     [2, 3, 1]],

    [[1, 1, 0],
     [2, -1, 2],
     [3, -2, 4]]],

    [[[0, 1, 2],
      [-1, 2, 3],
      [4, 1, -5]],

     [[3, 0, -1],
      [-1, 2, 1],
      [5, 6, 2]]]
    ], ctx=ctx)

    # num_batch * channel * out_height * out_width scale
    # i.e. (2, 2, 6, 6)
    scale = \
    mx.nd.array(
    [
    [[[1, 1, 1, 1, 1, 1],
     [1, -1, 1, -1, 1, -1],
     [-1, 1, -1, 1, -1, 1],
     [-1, -1, -1, -1, -1, -1],
     [2, 1, 2, 2, 1, 1],
     [1, 2, 1, 2, 1, 2]],

     [[1, 1, 1, 1, 1, 1],
      [1, -1, -1, 1, 1, 1],
      [-1, 1, -1, 1, -1, 1],
      [1, -1, -1, -1, -1, 1],
      [2, -1, 2, -2, 1, 1],
      [1, 2, 1, 2, 1, 2]]],

    [[[6, 5, 4, 3, 2, 1],
      [1, 2, 3, 4, 5, 6],
      [1, -1, 2, -2, 3, -3],
      [4, -4, 5, -5, 6, -6],
      [1, 1, 1, 1, 1, 1],
      [-1, -1, -1, -1, -1, -1]],

     [[-1, -1, -1, -1, -1, -1],
      [1, 1, 1, 1, 1, 1],
      [4, -4, 5, -5, 6, -6],
      [1, -1, 2, -2, 3, -3],
      [1, 2, 3, 4, 5, 6],
      [6, 5, 4, 3, 2, 1]]],
    ], ctx=ctx)

    # num_filter bias
    # i.e. (2, )
    bias = \
    mx.nd.array(
        [1, 2], ctx=ctx)

    in_data_var = mx.symbol.Variable(name="in_data")
    weight_var = mx.symbol.Variable(name="weight")
    scale_var = mx.symbol.Variable(name="scale")
    bias_var = mx.symbol.Variable(name="bias")

    op = mx.symbol.contrib.PositionalConvolution(name='test_positional_convolution',
                                                 data=in_data_var,
                                                 scale=scale_var,
                                                 weight=weight_var,
                                                 bias=bias_var,
                                                 num_filter=2,
                                                 pad=(1, 1), kernel=(3, 3), stride=(1, 1))
    be = op.bind(ctx=ctx, args={'in_data': in_data,
                                'scale': scale,
                                'weight': weight,
                                'bias': bias})
    be.forward(True)
    out_o = be.outputs[0].asnumpy()
    print(out_o)


def test_positional_convolution_backward():
    """
    Test positional convolution backward.
    """
    for num_batch in [1, 2, 4]:
        for num_channel_data in [4, 8, 12]:
            for input_height, input_width in itertools.product([5, 6, 9], [5, 6, 9]):
                for dilate in [(1, 1), (2, 2)]:
                    for num_group in [1, 2, 4]:
                        for grad_nodes in [['im_data'], ['scale_data'], ['weight'], ['bias']]:
                            output_height = input_height
                            output_width = input_width
                            im_data = np.random.rand(num_batch, num_channel_data, input_height, input_width)
                            scale_data = \
                                np.random.rand(num_batch, num_channel_data, output_height, output_width)\
                                * 0.8 + 0.1

                            weight = np.random.normal(0, 0.001, (num_channel_data, num_channel_data, 3, 3))
                            bias = np.random.rand(num_channel_data)

                            im_data_var = mx.symbol.Variable(name="im_data")
                            scale_data_var = mx.symbol.Variable(name="scale_data")
                            weight_var = mx.symbol.Variable(name="weight")
                            bias_var = mx.symbol.Variable(name="bias")
                            op = mx.sym.contrib.PositionalConvolution(name='test_op', data=im_data_var,
                                                                      scale=scale_data_var,
                                                                      weight=weight_var, bias=bias_var,
                                                                      num_filter=num_channel_data, pad=dilate,
                                                                      kernel=(3, 3), stride=(1, 1), dilate=dilate,
                                                                      num_group=num_group)
                            rtol, atol = 1e-5, 1e-8
                            # By now we only have gpu implementation
                            if mx.Context.default_ctx.device_type == 'gpu':
                                check_numeric_gradient(op, [im_data, scale_data, weight, bias], rtol=rtol, atol=atol,
                                                       grad_nodes=grad_nodes, ctx=mx.gpu(0))


if __name__ == '__main__':
    test_positional_convolution_forward(mx.gpu(0))
    test_positional_convolution_backward()
    print("numeric gradient is correct.")