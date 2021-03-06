include '../ext/cdefs.pxi'
include '../ext/interrupt.pxi'
include 'gsl.pxi'

cdef class FastFourierTransform_base:
    pass

cdef class FastFourierTransform_complex(FastFourierTransform_base):

    cdef double * data 
    cdef size_t n
    cdef size_t stride
    cdef gsl_fft_complex_wavetable * wt
    cdef gsl_fft_complex_workspace * mem
