import sys
import time
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import numpy as np

import cuda_code
reload(cuda_code)


def get_pycuda_function(len_digits, func_arg_types='P', get_v2=False):
    """Returns a callable PyCUDA function, with prepared invocation based on
     func_arg_types.
    Call the GPU via 
        func.prepared_call(<grid_dim>, <block_dim>, gpu_variables...)
    """

    # Below is needed on MacOS if using the clang compiler (CUDA 6.0).
    if sys.platform == 'darwin':
        nvcc_options = ['-ccbin=/usr/bin/clang']
    else:
        nvcc_options = None

    if not get_v2:
        source_code = cuda_code.source_code_with_printf
        #source_code = cuda_code.source_code_noprint
        #source_code = cuda_code.source_code_nounroll
        #source_code = cuda_code.source_code_nounroll_strict
    else:
        # v2 expects you to send multiple values, instead of single offset.
        source_code = cuda_code.source_code_with_printf_v2

    source_code = source_code.replace('LEN_DIGITS', str(len_digits))
    mod = SourceModule(source=source_code, options=nvcc_options)
    is_keith = mod.get_function("is_keith")
    is_keith.prepare(func_arg_types)
    return is_keith


def find_keith(len_digits=None, start_value=None, end_value=None,
               block_size=None, grid_size=None,
               verbose=True, iteration_limit=1):
    """Search for Keith numbers in the [start_value, end_value) range.
    If not given, start_value and end_value are calculated based on len_digits.
    iteration_limit is used to limit the kernel invocations.
    iteration_limit=0 (or None) will surprass this limit.
    """
    if not len_digits:
       len_digits = len(str(start_value))
       print "Setting len_digits to:", len_digits

    if not start_value:
        start_value = 10 ** (len_digits - 1)
    if not end_value:
        end_value = 10 ** len_digits
    if not block_size:
        block_size = 1024
    if not grid_size:
        grid_size = 2147483648 / block_size / 64

    total_data_size = block_size * grid_size

    assert 10 ** (len_digits - 1) <= start_value < 10 ** len_digits, (
           "start_value doesn't have len_digits many digits.")
    assert start_value < end_value <= 10 ** len_digits, (
           "end_value isn't acceptable.")

    if not iteration_limit:
        # Set a limit higher than needed.
        iteration_limit = int(end_value - start_value) / total_data_size + 10
        if verbose:
            print 'iteration_limit set to, iteration_limit'

    #assert iteration_limit < 50, ('This is a superfluous assertion to avoid '
    #   'long executions during delevopment and testing stage. Remove it at a '
    #    'late stage, after performance tuning, etc.')

    is_keith = get_pycuda_function(len_digits)
    value_pair = np.array([start_value / 2**64, start_value % 2**64], dtype=np.uint64)
    value_pair_gpu = cuda.mem_alloc(value_pair.nbytes)

    # Main loop, except the last small sized block.
    if verbose:
        print 'start'

    target_offset = start_value
    t_i = 0
    t0 = time.time()
    while (target_offset <= end_value - total_data_size):
        if t_i >= iteration_limit:
            break
        t_i += 1
        value_pair = np.array([target_offset / 2**64, target_offset % 2**64],
                              dtype=np.uint64)
        cuda.memcpy_htod(value_pair_gpu, value_pair)
        is_keith.prepared_call((grid_size,1), (block_size,1,1), value_pair_gpu)
        target_offset += total_data_size

    t_tot = time.time() - t0
    if verbose:
        print 'Total {:.2f} seconds'.format(t_tot)
    if verbose and t_i:
        avg_time = t_tot / t_i
        print 'Avg.  {:.2f} seconds'.format(avg_time)
        print 'Speed {:.2e} exec/minute'.format(60. / avg_time * total_data_size)
        print 'iterations:', t_i

    # Execute the last block unless loop was stopped because of iteration_limit.
    last_data_size = end_value - target_offset
    if last_data_size > 0 and last_data_size < total_data_size:
        value_pair = np.array([target_offset / 2**64, target_offset % 2**64],
                               dtype=np.uint64)
        cuda.memcpy_htod(value_pair_gpu, value_pair)
        is_keith.prepared_call((last_data_size,1), (1,1,1), value_pair_gpu)

    if verbose:
        print 'done.'


def is_keith_values(values_to_test, block_size=None, grid_size=None,
                    verbose=True):
    """Alternative function.
    Checks if any of the values given is a Keith number.
    """

    if not block_size:
        block_size = 1024
    if not grid_size:
        grid_size = 2147483648 / block_size / 64 / 16

    total_data_size = block_size * grid_size

    len_digits = len(str(values_to_test[0]))
    assert len(str(min(values_to_test))) == len(str(max(values_to_test))) 

    is_keith = get_pycuda_function(len_digits, get_v2=True)
    value_pairs_gpu = cuda.mem_alloc(total_data_size * 2 * 8)

    start_i = 0
    t0 = time.time()
    while start_i <= len(values_to_test) - total_data_size:
        value_pairs = np.array([(x / 2**64, x % 2**64) for x in
                               values_to_test[start_i: start_i + total_data_size]],
                               dtype=np.uint64).flatten()
        cuda.memcpy_htod(value_pairs_gpu, value_pairs)
        is_keith.prepared_call((grid_size,1), (block_size,1,1), value_pairs_gpu)
        start_i += total_data_size

    t_i = start_i / total_data_size
    t_tot = time.time() - t0
    if verbose:
        print 'Total {:.2f} seconds'.format(t_tot)
    if verbose and t_i:
        avg_time = t_tot / t_i
        print 'Avg.  {:.2f} seconds'.format(avg_time)
        print 'Speed {:.2e} exec/minute'.format(60. / avg_time * total_data_size)
        print 'iterations:', t_i


    # Execute the last block of values.
    last_data_size = len(values_to_test) - start_i
    if last_data_size > 0:
        value_pairs = np.array([(x / 2**64, x % 2**64) for x in
                               values_to_test[start_i:]],
                               dtype=np.uint64).flatten()
        cuda.memcpy_htod(value_pairs_gpu, value_pairs)
        is_keith.prepared_call((last_data_size,1), (1,1,1), value_pairs_gpu)

    if verbose:
        print 'done.'


def test_for_correctness(len_digits):
    import known_keiths_table

    keiths_list = known_keiths_table.known_keiths[len_digits]
    print 'len_digits:', len_digits
    print 'keiths_list:', keiths_list

    for known_keith in keiths_list:
        print '-' * 30
        print 'Expected stdout : {} * 2**64 + {}'.format(known_keith / 2**64,
                                                         known_keith % 2**64)
        find_keith(len_digits, start_value=known_keith, verbose=False,
                   iteration_limit=1)
        print '-' * 30


def check_performance(len_digits, iteration, randomized_start=True):
    import random
    start_value = 10 ** (len_digits - 1)
    if randomized_start:
       start_value = random.randrange(start_value, start_value * 5)
    find_keith(len_digits, start_value=start_value, verbose=True,
               iteration_limit=iteration)


def check_v2(iteration):
    block_size = 1024
    grid_size = 1024
    data_len = block_size * grid_size * iteration
    start_value = 10**34 * 3
    values = np.arange(start_value, start_value + data_len)
    is_keith_values(values, block_size=block_size, grid_size=grid_size)


if __name__ == '__main__':

	'''	
    if '--test' in sys.argv:
        test_for_correctness(int(sys.argv[-1]))
    elif '--perf' in sys.argv:
        check_performance(len_digits=35, iteration=int(sys.argv[-1]))
    elif '--perfv2' in sys.argv:
        check_v2(iteration=int(sys.argv[-1]))

    else:
        print '\n  Please see the Readme file.\n'
        print '  You may run:'
        print '     ', sys.argv[0], '--test N'
        print ('  in order to execute test code that tries to find known'
               ' Keith numbers with N digits.')
        print '  Also a performance test can be run with:'
        print '     ', sys.argv[0], '--perf iter'
        print ('  which will call the GPU kernel iter many times and calculate'
               ' average execution times.\n')
	'''
	
	s_value = long(sys.argv[1])
	e_value = long(sys.argv[2])
	xx = int(sys.argv[3])
	find_keith(start_value=s_value, end_value=e_value, iteration_limit=xx)
	#test_for_correctness(xx)


