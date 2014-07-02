

Included files: 
    README.txt   : This file.
    keith.py     : Main Python code.
    cuda_code.py : Holds the C (CUDA) code that gets executed on GPU. 
    known_keiths_table.py : List of 2-34 digit Keith numbers to be used for testing.
    

PyCUDA/CUDA code for finding Keith numbers.
--------------------------

This work is based on the following code and aims to port it to GPU, using PyCUDA:

    def this_function(number_to_test):
        n = map(int, str(number_to_test))
        while number_to_test > n[0]:
            n=n[1:]+[sum(n)]
        if (number_to_test == n[0]) ):
            return True 


The PyCuda implementation is included in keith.py

There are two versions of the code.
 
The primary version is find_keith().
It tries to find Keith numbers by consecutively enumeration N digit numbers, where N is given as an argument (len_digit).
It sends only a single offset value (actually two 64bit values to represent a 128bit value) to the GPU, but each GPU thread tests a different integer (offset_value + thread_id).

 print find_keith.__doc__
    Search for Keith numbers in the [start_value, end_value) range.
    If not given, start_value and end_value are calculated based on len_digits.
    iteration_limit is used to limit the kernel invocations.
    iteration_limit=0 (or None) will surprass this limit.
    
There is also an extra assertion at line 72, which stops you from starting long executions.
The reason is, if you are running on a GPU that the computer screen is connected, my program hijacks the GPU so you may have a hard time killing the process if you happen to start a long execution unintentionally.
You should eventually delete that assertion.
See the while loop at line 87, and you will notice iteration_limit is used for stopping execution early.


The second version is is_keith_values().
Instead of a single offset, it accepts an array of values, each of which gets used by different GPU threads.
This is slower than the first version, but it allows to check non-consecutive values.


Both functions accept block_size and grid_size integer values that represent the 1D grid/block size of the CUDA kernel that will be launched.
The best block and grid size is dependent on the exact GPU model you have, and it is better to be found empirically.


You should probably use the aforomentioned functions directly.
But for a quick performance test simply run:

    python keith.py --perf 10

You can see what it is doing at the bottom of the file.
Run keith.py without arguments for a short help message.
Enjoy!


