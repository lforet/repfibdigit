

_printf_header = "#include <stdio.h>\n\n"

_helper_function = """
struct Int128 {
  unsigned long long int high;
  unsigned long long int low;
};

// Implements: new_sum = 2 * sum - value
// Assumption: sum >= value
__device__ Int128
double_sum_minus_value(Int128 sum, Int128 value)
{
  Int128 new_sum;
  int over_under_correction;

  // First let's double the sum.
  new_sum.high = sum.high << 1;
  new_sum.low = sum.low << 1;

  /* Check if there was an overflow. */
  if (new_sum.low < sum.low)
    over_under_correction = 1;
  else
    over_under_correction = 0;
      
  // Let's substract value
  /* Check if there will be an underflow */
  if (new_sum.low < value.low)
    over_under_correction--;

  new_sum.high = new_sum.high - value.high;
  new_sum.low = new_sum.low - value.low;

  /* Apply overflow/underflow correction (-1, 0, +1) */
  new_sum.high += over_under_correction;

  return new_sum;
}\n
"""

_main_v1_body = """
__global__ void
is_keith(unsigned long long int *target_offset_highlow)
{
  int i = 0;
  
  Int128 sum = {.high = 0, .low = 0};
  Int128 new_sum;
  const int idx = blockIdx.x * blockDim.x + threadIdx.x;
  Int128 number_to_test = {.high = target_offset_highlow[0],
                           .low = target_offset_highlow[1] + idx};
  Int128 values[LEN_DIGITS];

  if (number_to_test.low < target_offset_highlow[1])
    number_to_test.high++;
    
  /* Used for splitting the target number into digits. */
  unsigned long long int dissect_mid32 = number_to_test.low >> 32;
  unsigned long long int dissect_low32 = number_to_test.low & 0x00000000FFFFFFFF;
  unsigned long long int dissect_high = number_to_test.high;
  unsigned long long int R_high, R_mid, R_low;

  #pragma unroll
  for (i = 0; i < LEN_DIGITS; i++)
  {
    R_high = dissect_high % 10;
    dissect_high = dissect_high / 10;

    R_mid = ((R_high << 32) + dissect_mid32) % 10;
    dissect_mid32 = ((R_high << 32) + dissect_mid32) / 10;

    R_low = ((R_mid << 32) + dissect_low32) % 10;
    dissect_low32 = ((R_mid << 32) + dissect_low32) / 10;
    
    values[LEN_DIGITS - 1 - i].low = R_low;
    values[LEN_DIGITS - 1 - i].high = 0;
    sum.low += R_low;
  }
    
  i = 0;
  // number_to_test > sum
  while(number_to_test.high > sum.high ||
        (number_to_test.high == sum.high && number_to_test.low > sum.low))
  {
    // sum = 2 * sum - values[i]
    new_sum = double_sum_minus_value(sum, values[i]);
    
    values[i].high = sum.high;
    values[i].low = sum.low;
    sum.high = new_sum.high;
    sum.low = new_sum.low;
    
    i = (i + 1) % LEN_DIGITS;
  }
    
  if (number_to_test.high == sum.high && number_to_test.low == sum.low)
  {
    printf("!!! Found number: %llu * 2**64 + %llu\\n", number_to_test.high, number_to_test.low);
  }
}
"""


_main_v2_body = """
__global__ void
is_keith(unsigned long long int *target_offsets_highlow)
{
  int i = 0;
  
  Int128 sum = {.high = 0, .low = 0};
  Int128 new_sum;
  const int idx = blockIdx.x * blockDim.x + threadIdx.x;
  Int128 number_to_test = {.high = target_offsets_highlow[2 * idx],
                           .low = target_offsets_highlow[2 * idx + 1]};
  Int128 values[LEN_DIGITS];

"""
_main_v2_body += _main_v1_body[_main_v1_body.index('  /* Used for splitting'):]


source_code_with_printf = _printf_header + _helper_function + _main_v1_body
source_code_noprint = (source_code_with_printf[20: source_code_with_printf.index('printf')]
                       + ";\n  }\n}\n") 
source_code_nounroll = source_code_with_printf.replace('#pragma unroll', '')
source_code_nounroll_strict = source_code_with_printf.replace('#pragma unroll',
                                                              '#pragma unroll 1')

source_code_with_printf_v2 = _printf_header + _helper_function + _main_v2_body



def print_all():
    print 'Below are the available CUDA kernel source code versions:'
    for code_name in ['source_code_with_printf', 'source_code_noprint', 
                      'source_code_nounroll', 'source_code_unroll0']:
        print '-' * 30, '\n', code_name, '\n', '-' * 30
        print eval(code_name)
        print '-' * 30, '\nENDOF:', code_name, '\n', '-' * 30
        print 


if __name__ == '__main__':
    pass
    #print source_code_with_printf_v2
    #print_all()

