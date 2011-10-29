
from ctypes import windll 
from ctypes import byref, c_uint32, c_uint64, c_void_p, c_size_t, create_string_buffer, cast, POINTER
from ctypes import c_bool, c_int32, sizeof, c_ulong, c_ulonglong, c_char, c_char_p, pointer
import struct
import array

OPENCL_PATH = "OpenCL.dll"

opencl = windll.LoadLibrary(OPENCL_PATH)

clGetPlatformIDs = opencl.clGetPlatformIDs
clGetPlatformInfo = opencl.clGetPlatformInfo
clGetDeviceIDs = opencl.clGetDeviceIDs
clGetDeviceInfo = opencl.clGetDeviceInfo
clCreateContext = opencl.clCreateContext
clCreateContextFromType = opencl.clCreateContextFromType
clGetContextInfo = opencl.clGetContextInfo
clCreateProgramWithSource = opencl.clCreateProgramWithSource
clBuildProgram = opencl.clBuildProgram
clCreateCommandQueue = opencl.clCreateCommandQueue
clGetProgramBuildInfo = opencl.clGetProgramBuildInfo
clCreateKernel = opencl.clCreateKernel
clCreateBuffer = opencl.clCreateBuffer
clEnqueueWriteBuffer = opencl.clEnqueueWriteBuffer
clEnqueueReadBuffer = opencl.clEnqueueReadBuffer

def GetPlatform(idx):
    num_platforms = c_uint32()
    rez = clGetPlatformIDs(0, None, byref(num_platforms))
    if rez != CL_SUCCESS: return None
    n = num_platforms.value
    if n == 0 or idx >= n: return None

    platform_array = (c_void_p * n)()
    rez = clGetPlatformIDs(n, platform_array, None)
    t = tuple(x for x in platform_array)
    return t[idx]

CL_SUCCESS =                                  0
CL_DEVICE_NOT_FOUND =                         -1
CL_DEVICE_NOT_AVAILABLE =                     -2
CL_COMPILER_NOT_AVAILABLE =                   -3
CL_MEM_OBJECT_ALLOCATION_FAILURE =            -4
CL_OUT_OF_RESOURCES =                         -5
CL_OUT_OF_HOST_MEMORY =                       -6
CL_PROFILING_INFO_NOT_AVAILABLE =             -7
CL_MEM_COPY_OVERLAP =                         -8
CL_IMAGE_FORMAT_MISMATCH =                    -9
CL_IMAGE_FORMAT_NOT_SUPPORTED =               -10
CL_BUILD_PROGRAM_FAILURE =                    -11
CL_MAP_FAILURE =                              -12
CL_MISALIGNED_SUB_BUFFER_OFFSET =             -13
CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST = -14
CL_INVALID_VALUE =                            -30
CL_INVALID_DEVICE_TYPE =                      -31
CL_INVALID_PLATFORM =                         -32
CL_INVALID_DEVICE =                           -33
CL_INVALID_CONTEXT =                          -34
CL_INVALID_QUEUE_PROPERTIES =                 -35
CL_INVALID_COMMAND_QUEUE =                    -36
CL_INVALID_HOST_PTR =                         -37
CL_INVALID_MEM_OBJECT =                       -38
CL_INVALID_IMAGE_FORMAT_DESCRIPTOR =          -39
CL_INVALID_IMAGE_SIZE =                       -40
CL_INVALID_SAMPLER =                          -41
CL_INVALID_BINARY =                           -42
CL_INVALID_BUILD_OPTIONS =                    -43
CL_INVALID_PROGRAM =                          -44
CL_INVALID_PROGRAM_EXECUTABLE =               -45
CL_INVALID_KERNEL_NAME =                      -46
CL_INVALID_KERNEL_DEFINITION =                -47
CL_INVALID_KERNEL =                           -48
CL_INVALID_ARG_INDEX =                        -49
CL_INVALID_ARG_VALUE =                        -50
CL_INVALID_ARG_SIZE =                         -51
CL_INVALID_KERNEL_ARGS =                      -52
CL_INVALID_WORK_DIMENSION =                   -53
CL_INVALID_WORK_GROUP_SIZE =                  -54
CL_INVALID_WORK_ITEM_SIZE =                   -55
CL_INVALID_GLOBAL_OFFSET =                    -56
CL_INVALID_EVENT_WAIT_LIST =                  -57
CL_INVALID_EVENT =                            -58
CL_INVALID_OPERATION =                        -59
CL_INVALID_GL_OBJECT =                        -60
CL_INVALID_BUFFER_SIZE =                      -61
CL_INVALID_MIP_LEVEL =                        -62
CL_INVALID_GLOBAL_WORK_SIZE =                 -63
CL_INVALID_PROPERTY =                         -64

CL_PLATFORM_PROFILE =                         0x0900
CL_PLATFORM_VERSION =                         0x0901
CL_PLATFORM_NAME =                            0x0902
CL_PLATFORM_VENDOR =                          0x0903
CL_PLATFORM_EXTENSIONS =                      0x0904

CL_DEVICE_TYPE_DEFAULT =                      (1 << 0)
CL_DEVICE_TYPE_CPU =                          (1 << 1)
CL_DEVICE_TYPE_GPU =                          (1 << 2)
CL_DEVICE_TYPE_ACCELERATOR =                  (1 << 3)
CL_DEVICE_TYPE_ALL =                          0xFFFFFFFF

CL_DEVICE_TYPE =                              0x1000
CL_DEVICE_VENDOR_ID =                         0x1001
CL_DEVICE_MAX_COMPUTE_UNITS =                 0x1002
CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS =          0x1003
CL_DEVICE_MAX_WORK_GROUP_SIZE =               0x1004
CL_DEVICE_MAX_WORK_ITEM_SIZES =               0x1005
CL_DEVICE_PREFERRED_VECTOR_WIDTH_CHAR =       0x1006
CL_DEVICE_PREFERRED_VECTOR_WIDTH_SHORT =      0x1007
CL_DEVICE_PREFERRED_VECTOR_WIDTH_INT =        0x1008
CL_DEVICE_PREFERRED_VECTOR_WIDTH_LONG =       0x1009
CL_DEVICE_PREFERRED_VECTOR_WIDTH_FLOAT =      0x100A
CL_DEVICE_PREFERRED_VECTOR_WIDTH_DOUBLE =     0x100B
CL_DEVICE_MAX_CLOCK_FREQUENCY =               0x100C
CL_DEVICE_ADDRESS_BITS =                      0x100D
CL_DEVICE_MAX_READ_IMAGE_ARGS =               0x100E
CL_DEVICE_MAX_WRITE_IMAGE_ARGS =              0x100F
CL_DEVICE_MAX_MEM_ALLOC_SIZE =                0x1010
CL_DEVICE_IMAGE2D_MAX_WIDTH =                 0x1011
CL_DEVICE_IMAGE2D_MAX_HEIGHT =                0x1012
CL_DEVICE_IMAGE3D_MAX_WIDTH =                 0x1013
CL_DEVICE_IMAGE3D_MAX_HEIGHT =                0x1014
CL_DEVICE_IMAGE3D_MAX_DEPTH =                 0x1015
CL_DEVICE_IMAGE_SUPPORT =                     0x1016
CL_DEVICE_MAX_PARAMETER_SIZE =                0x1017
CL_DEVICE_MAX_SAMPLERS =                      0x1018
CL_DEVICE_MEM_BASE_ADDR_ALIGN =               0x1019
CL_DEVICE_MIN_DATA_TYPE_ALIGN_SIZE =          0x101A
CL_DEVICE_SINGLE_FP_CONFIG =                  0x101B
CL_DEVICE_GLOBAL_MEM_CACHE_TYPE =             0x101C
CL_DEVICE_GLOBAL_MEM_CACHELINE_SIZE =         0x101D
CL_DEVICE_GLOBAL_MEM_CACHE_SIZE =             0x101E
CL_DEVICE_GLOBAL_MEM_SIZE =                   0x101F
CL_DEVICE_MAX_CONSTANT_BUFFER_SIZE =          0x1020
CL_DEVICE_MAX_CONSTANT_ARGS =                 0x1021
CL_DEVICE_LOCAL_MEM_TYPE =                    0x1022
CL_DEVICE_LOCAL_MEM_SIZE =                    0x1023
CL_DEVICE_ERROR_CORRECTION_SUPPORT =          0x1024
CL_DEVICE_PROFILING_TIMER_RESOLUTION =        0x1025
CL_DEVICE_ENDIAN_LITTLE =                     0x1026
CL_DEVICE_AVAILABLE =                         0x1027
CL_DEVICE_COMPILER_AVAILABLE =                0x1028
CL_DEVICE_EXECUTION_CAPABILITIES =            0x1029
CL_DEVICE_QUEUE_PROPERTIES =                  0x102A
CL_DEVICE_NAME =                              0x102B
CL_DEVICE_VENDOR =                            0x102C
CL_DRIVER_VERSION =                           0x102D
CL_DEVICE_PROFILE =                           0x102E
CL_DEVICE_VERSION =                           0x102F
CL_DEVICE_EXTENSIONS =                        0x1030
CL_DEVICE_PLATFORM =                          0x1031
CL_DEVICE_DOUBLE_FP_CONFIG =                  0x1032
CL_DEVICE_HALF_FP_CONFIG =                    0x1033
CL_DEVICE_PREFERRED_VECTOR_WIDTH_HALF =       0x1034
CL_DEVICE_HOST_UNIFIED_MEMORY =               0x1035
CL_DEVICE_NATIVE_VECTOR_WIDTH_CHAR =          0x1036
CL_DEVICE_NATIVE_VECTOR_WIDTH_SHORT =         0x1037
CL_DEVICE_NATIVE_VECTOR_WIDTH_INT =           0x1038
CL_DEVICE_NATIVE_VECTOR_WIDTH_LONG =          0x1039
CL_DEVICE_NATIVE_VECTOR_WIDTH_FLOAT =         0x103A
CL_DEVICE_NATIVE_VECTOR_WIDTH_DOUBLE =        0x103B
CL_DEVICE_NATIVE_VECTOR_WIDTH_HALF =          0x103C
CL_DEVICE_OPENCL_C_VERSION =                  0x103D

CL_FP_DENORM =                                (1 << 0)
CL_FP_INF_NAN =                               (1 << 1)
CL_FP_ROUND_TO_NEAREST =                      (1 << 2)
CL_FP_ROUND_TO_ZERO =                         (1 << 3)
CL_FP_ROUND_TO_INF =                          (1 << 4)
CL_FP_FMA =                                   (1 << 5)
CL_FP_SOFT_FLOAT =                            (1 << 6)

CL_NONE =                                     0x0
CL_READ_ONLY_CACHE =                          0x1
CL_READ_WRITE_CACHE =                         0x2

CL_LOCAL =                                    0x1
CL_GLOBAL =                                   0x2

CL_EXEC_KERNEL =                              (1 << 0)
CL_EXEC_NATIVE_KERNEL =                       (1 << 1)

CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE =      (1 << 0)
CL_QUEUE_PROFILING_ENABLE =                   (1 << 1)

CL_CONTEXT_REFERENCE_COUNT =                  0x1080
CL_CONTEXT_DEVICES =                          0x1081
CL_CONTEXT_PROPERTIES =                       0x1082
CL_CONTEXT_NUM_DEVICES =                      0x1083
CL_CONTEXT_PLATFORM =                         0x1084

CL_PROGRAM_BUILD_STATUS =                     0x1181
CL_PROGRAM_BUILD_OPTIONS =                    0x1182
CL_PROGRAM_BUILD_LOG =                        0x1183

CL_MEM_READ_WRITE =                           (1 << 0)
CL_MEM_WRITE_ONLY =                           (1 << 1)
CL_MEM_READ_ONLY =                            (1 << 2)
CL_MEM_USE_HOST_PTR =                         (1 << 3)
CL_MEM_ALLOC_HOST_PTR =                       (1 << 4)
CL_MEM_COPY_HOST_PTR =                        (1 << 5)

def PlatformInfo(platform, param_name):
    if platform is None: return None
    sz = c_size_t()
    ret = clGetPlatformInfo(platform, param_name, 0, None, byref(sz))
    if ret != CL_SUCCESS: return None
    param_value = create_string_buffer(sz.value)
    clGetPlatformInfo(platform, param_name, sz.value, param_value, None)
    value = str(param_value.value, 'utf-8')
    return value

class Platform:
    def __init__(self, platform):
        self.platform = platform
        self.version = PlatformInfo(platform, CL_PLATFORM_VERSION)
        self.profile = PlatformInfo(platform, CL_PLATFORM_PROFILE)
        self.name = PlatformInfo(platform, CL_PLATFORM_NAME)
        self.vendor = PlatformInfo(platform, CL_PLATFORM_VENDOR)
        self.extensions = PlatformInfo(platform, CL_PLATFORM_EXTENSIONS)


def GetDevice(idx, device_type, platform):
    num_devices = c_uint32()
    dev_type = c_uint64(device_type) #64-bit DEVICE_TYPE investigate TODO
    ret = clGetDeviceIDs(platform, dev_type, 0, None, byref(num_devices)) 
    if ret != CL_SUCCESS: return None
    n = num_devices.value
    if idx >= n: return None 

    device_array = (c_void_p * n)()

    clGetDeviceIDs(platform, dev_type, num_devices, device_array, None)
    t = tuple(x for x in device_array)
    return t[idx]

def DeviceInfo(device, param_name, ptr_type):
    if device is None: return None
    sz = c_size_t()
    ret = clGetDeviceInfo(device, param_name, 0, None, byref(sz))
    if ret != CL_SUCCESS: return None

    if ptr_type == c_bool:
        item_size = 4
    else:
        item_size = sizeof(ptr_type)
    n = int(sz.value / item_size)
    arr = (ptr_type * n)()
    clGetDeviceInfo(device, param_name, sz.value, arr, None)
    if n == 1:
        return arr[0]
    else:
        return tuple(arr)


    ### Erase later TODO
    param_value = create_string_buffer(sz.value)
    clGetDeviceInfo(device, param_name, sz.value, param_value, None)

    if param_name == CL_DEVICE_MAX_WORK_GROUP_SIZE:
        print(sizeof(ptr_type))
        arr = (ptr_type * 1)()
        clGetDeviceInfo(device, param_name, sz.value, arr, None)
        print(arr[0])
        print(sz.value)
        for n in param_value:
            print(n)

    if param_name == CL_DEVICE_MAX_WORK_ITEM_SIZES: #TODO calculate harcoded number 3
        arr = (ptr_type * 3)()
        clGetDeviceInfo(device, param_name, sz.value, arr, None)
        return tuple(arr)
    else:
        value = param_value.value
        np = cast(value, POINTER(ptr_type))
        return np.contents.value 

def convert_chars(chars):
    if chars is None: return None
    text = ""
    for char in chars:
        text += str(char, 'utf-8')
    return text

class Device:
    def __init__(self, device):
        self.device = device
        self.dev_type = DeviceInfo(device, CL_DEVICE_TYPE, c_uint64)
        self.dev_type = self.dev_type & 0xFF
        self.vendor_id = DeviceInfo(device, CL_DEVICE_VENDOR_ID, c_uint32)
        self.max_compute_units = DeviceInfo(device, CL_DEVICE_MAX_COMPUTE_UNITS, c_uint32)
        self.max_work_item_dimensions = DeviceInfo(device, CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS, c_uint32)
        self.max_work_item_sizes = DeviceInfo(device, CL_DEVICE_MAX_WORK_ITEM_SIZES, c_size_t)
        self.max_work_group_size = DeviceInfo(device, CL_DEVICE_MAX_WORK_GROUP_SIZE, c_size_t)

        self.preferred_vector_width_char = DeviceInfo(device, CL_DEVICE_PREFERRED_VECTOR_WIDTH_CHAR, c_uint32)
        self.preferred_vector_width_short = DeviceInfo(device, CL_DEVICE_PREFERRED_VECTOR_WIDTH_SHORT, c_uint32)
        self.preferred_vector_width_int = DeviceInfo(device, CL_DEVICE_PREFERRED_VECTOR_WIDTH_INT, c_uint32)
        self.preferred_vector_width_long = DeviceInfo(device, CL_DEVICE_PREFERRED_VECTOR_WIDTH_LONG, c_uint32)
        self.preferred_vector_width_float = DeviceInfo(device, CL_DEVICE_PREFERRED_VECTOR_WIDTH_FLOAT, c_uint32)
        self.preferred_vector_width_double = DeviceInfo(device, CL_DEVICE_PREFERRED_VECTOR_WIDTH_DOUBLE, c_uint32)
        self.preferred_vector_width_half = DeviceInfo(device, CL_DEVICE_PREFERRED_VECTOR_WIDTH_HALF, c_uint32)

        self.native_vector_width_char = DeviceInfo(device, CL_DEVICE_NATIVE_VECTOR_WIDTH_CHAR, c_uint32)
        self.native_vector_width_short = DeviceInfo(device, CL_DEVICE_NATIVE_VECTOR_WIDTH_SHORT, c_uint32)
        self.native_vector_width_int = DeviceInfo(device, CL_DEVICE_NATIVE_VECTOR_WIDTH_INT, c_uint32)
        self.native_vector_width_long = DeviceInfo(device, CL_DEVICE_NATIVE_VECTOR_WIDTH_LONG, c_uint32)
        self.native_vector_width_float = DeviceInfo(device, CL_DEVICE_NATIVE_VECTOR_WIDTH_FLOAT, c_uint32)
        self.native_vector_width_double = DeviceInfo(device, CL_DEVICE_NATIVE_VECTOR_WIDTH_DOUBLE, c_uint32)
        self.native_vector_width_half = DeviceInfo(device, CL_DEVICE_NATIVE_VECTOR_WIDTH_HALF, c_uint32)

        self.max_clock_frequency = DeviceInfo(device, CL_DEVICE_MAX_CLOCK_FREQUENCY, c_uint32)
        self.address_bits = DeviceInfo(device, CL_DEVICE_ADDRESS_BITS, c_uint32)
        self.max_mem_alloc_size = DeviceInfo(device, CL_DEVICE_MAX_MEM_ALLOC_SIZE, c_ulonglong)
        self.image_support = DeviceInfo(device, CL_DEVICE_IMAGE_SUPPORT, c_bool)
        self.max_read_image_args = DeviceInfo(device, CL_DEVICE_MAX_READ_IMAGE_ARGS, c_uint32)
        self.max_write_image_args = DeviceInfo(device, CL_DEVICE_MAX_WRITE_IMAGE_ARGS, c_uint32)

        self.image2d_max_width = DeviceInfo(device, CL_DEVICE_IMAGE2D_MAX_WIDTH, c_size_t)
        self.image2d_max_height = DeviceInfo(device, CL_DEVICE_IMAGE2D_MAX_HEIGHT, c_size_t)
        self.image3d_max_width = DeviceInfo(device, CL_DEVICE_IMAGE3D_MAX_WIDTH, c_size_t)
        self.image3d_max_height = DeviceInfo(device, CL_DEVICE_IMAGE3D_MAX_HEIGHT, c_size_t)
        self.image3d_max_depth = DeviceInfo(device, CL_DEVICE_IMAGE3D_MAX_DEPTH, c_size_t)

        self.max_samplers = DeviceInfo(device, CL_DEVICE_MAX_SAMPLERS, c_uint32)
        self.max_parameter_size = DeviceInfo(device, CL_DEVICE_MAX_PARAMETER_SIZE, c_size_t)
        self.mem_base_addr_align = DeviceInfo(device, CL_DEVICE_MEM_BASE_ADDR_ALIGN, c_uint32)
        self.min_data_type_align_size = DeviceInfo(device, CL_DEVICE_MIN_DATA_TYPE_ALIGN_SIZE, c_uint32)
        
        double_fp_config = DeviceInfo(device, CL_DEVICE_DOUBLE_FP_CONFIG, c_char)
        if double_fp_config is not None: 
            temp = str(double_fp_config[0], 'utf-8')
            self.double_fp_config = int(ord(temp))
        
        cache_type = DeviceInfo(device, CL_DEVICE_GLOBAL_MEM_CACHE_TYPE, c_char)
        if cache_type is not None:
            temp = str(cache_type[0], 'utf-8')
            self.global_mem_cache_type = int(ord(temp))

        self.global_mem_cacheline_size = DeviceInfo(device, CL_DEVICE_GLOBAL_MEM_CACHELINE_SIZE, c_uint32)
        self.global_mem_cache_size = DeviceInfo(device, CL_DEVICE_GLOBAL_MEM_CACHE_SIZE, c_ulonglong)
        self.global_mem_size = DeviceInfo(device, CL_DEVICE_GLOBAL_MEM_SIZE, c_ulonglong)
        self.max_constant_buffer_size = DeviceInfo(device, CL_DEVICE_MAX_CONSTANT_BUFFER_SIZE, c_ulonglong)
        self.max_constant_args = DeviceInfo(device, CL_DEVICE_MAX_CONSTANT_ARGS, c_uint32)
        
        mem_type = DeviceInfo(device, CL_DEVICE_LOCAL_MEM_TYPE, c_char)
        if mem_type is not None:
            temp = str(mem_type[0], 'utf-8')
            self.local_mem_type = int(ord(temp))

        self.local_mem_size = DeviceInfo(device, CL_DEVICE_LOCAL_MEM_SIZE, c_ulonglong)
        self.error_correction_support = DeviceInfo(device, CL_DEVICE_ERROR_CORRECTION_SUPPORT, c_bool)
        self.host_unified_memory = DeviceInfo(device, CL_DEVICE_HOST_UNIFIED_MEMORY, c_bool)
        self.profiling_timer_resolution = DeviceInfo(device, CL_DEVICE_PROFILING_TIMER_RESOLUTION, c_size_t)
        self.endian_little = DeviceInfo(device, CL_DEVICE_ENDIAN_LITTLE, c_bool)
        self.available = DeviceInfo(device, CL_DEVICE_AVAILABLE, c_bool)
        self.compiler_available = DeviceInfo(device, CL_DEVICE_COMPILER_AVAILABLE, c_bool)

        exec_capabilities = DeviceInfo(device, CL_DEVICE_EXECUTION_CAPABILITIES, c_char)
        if exec_capabilities is not None:
            temp = str(exec_capabilities[0], 'utf-8')
            self.execution_capabilities = int(ord(temp))

        queue_prop = DeviceInfo(device, CL_DEVICE_QUEUE_PROPERTIES, c_char)
        if queue_prop is not None:
            temp = str(queue_prop[0], 'utf-8')
            self.queue_properties = int(ord(temp))

        name = DeviceInfo(device, CL_DEVICE_NAME, c_char)
        self.name = convert_chars(name)
        vendor = DeviceInfo(device, CL_DEVICE_VENDOR, c_char)
        self.vendor = convert_chars(vendor)
        driver = DeviceInfo(device, CL_DRIVER_VERSION, c_char)
        self.driver_version = convert_chars(driver)
        profile1 = DeviceInfo(device, CL_DEVICE_PROFILE, c_char)
        self.profile1 = convert_chars(profile1)
        version = DeviceInfo(device, CL_DEVICE_VERSION, c_char)
        self.version = convert_chars(version)
        extensions = DeviceInfo(device, CL_DEVICE_EXTENSIONS, c_char)
        self.extensions = convert_chars(extensions)



#device = GetDevice(0, CL_DEVICE_TYPE_GPU, platform)
#device = GetDevice(0, CL_DEVICE_TYPE_CPU, platform)
#device = GetDevice(0, CL_DEVICE_TYPE_ACCELERATOR, platform)
#device = GetDevice(0, CL_DEVICE_TYPE_DEFAULT, platform)
#device = GetDevice(0, CL_DEVICE_TYPE_ALL, platform)

def display_inf(dev):
    print("Device Type: ", dev.dev_type)
    print("Vendor ID: ", dev.vendor_id)
    print("Max compute units: ", dev.max_compute_units)
    print("Max work item dimensions: ", dev.max_work_item_dimensions)
    print("Max work item sizes: ", dev.max_work_item_sizes)
    print("Max work group size: ", dev.max_work_group_size)
    print("Preferred vector with char: ", dev.preferred_vector_width_char)
    print("Preferred vector with short: ", dev.preferred_vector_width_short)
    print("Preferred vector with int: ", dev.preferred_vector_width_int)
    print("Preferred vector with long: ", dev.preferred_vector_width_long)
    print("Preferred vector with float: ", dev.preferred_vector_width_float)
    print("Preferred vector with double: ", dev.preferred_vector_width_double)
    print("Preferred vector with half: ", dev.preferred_vector_width_half)

    print("Native vector with char: ", dev.native_vector_width_char)
    print("Native vector with short: ", dev.native_vector_width_short)
    print("Native vector with int: ", dev.native_vector_width_int)
    print("Native vector with long: ", dev.native_vector_width_long)
    print("Native vector with float: ", dev.native_vector_width_float)
    print("Native vector with double: ", dev.native_vector_width_double)
    print("Native vector with half: ", dev.native_vector_width_half)
    print("Max clock frequency: ", dev.max_clock_frequency)
    print("Address bits: ", dev.address_bits)
    print("Max mem alloc size: ", dev.max_mem_alloc_size)
    print("Image support: ", dev.image_support)
    print("Max read image args: ", dev.max_read_image_args)
    print("Max write image args: ", dev.max_write_image_args)

    print("Image2d max width: ", dev.image2d_max_width)
    print("Image2d max height: ", dev.image2d_max_height)
    print("Image3d max width: ", dev.image3d_max_width)
    print("Image3d max height: ", dev.image3d_max_height)
    print("Image3d max depth: ", dev.image3d_max_depth)

    print("Max samplers: ", dev.max_samplers)
    print("Max parameter size: ", dev.max_parameter_size)
    print("Mem base addr align: ", dev.mem_base_addr_align)
    print("Min data type align size: ", dev.min_data_type_align_size)

    print("Double FP config: ", hex(dev.double_fp_config))
    print("Global mem cache type: ", hex(dev.global_mem_cache_type))
    print("Global mem cacheline size: ", dev.global_mem_cacheline_size)
    print("Global mem cache size: ", dev.global_mem_cache_size)
    print("Global mem size: ", dev.global_mem_size)
    print("Max constant buffer size: ", dev.max_constant_buffer_size)
    print("Max constant args: ", dev.max_constant_args)
    print("Local mem type: ", hex(dev.local_mem_type))
    print("Local mem size: ", dev.local_mem_size)
    print("Error correction support: ", dev.error_correction_support)
    print("Host unified memory: ", dev.host_unified_memory)
    print("Profiling timer resolution: ", dev.profiling_timer_resolution)
    print("Endian little: ", dev.endian_little)
    print("Device available: ", dev.available)
    print("Compiler available: ", dev.compiler_available)
    print("Execution capabilities: ", dev.execution_capabilities)
    print("Device Queue properties: ", dev.queue_properties)


    print("Device name: ", dev.name)
    print("Device vendor: ", dev.vendor)
    print("Driver version: ", dev.driver_version)
    print("Device profile1: ", dev.profile1)
    print("Device version: ", dev.version)
    print("Device extensions: ", dev.extensions)

def CreateContext(platform, device):
    props = (c_void_p * 3)()
    props[0] = CL_CONTEXT_PLATFORM
    props[1] = platform
    props[2] = 0

    dev_arr = (c_void_p * 1)()
    dev_arr[0] = device

    err_code = c_int32()
    ret = clCreateContext(props, 1, dev_arr, None, None, byref(err_code))
    if err_code.value != CL_SUCCESS: return None

    return ret

def ContextInfo(context, param_name, ptr_type):
    if context is None: return None
    sz = c_size_t()
    ret = clGetContextInfo(context, param_name, 0, None, byref(sz))
    if ret != CL_SUCCESS: return None

    if ptr_type == c_bool:
        item_size = 4
    else:
        item_size = sizeof(ptr_type)
    n = int(sz.value / item_size)
    arr = (ptr_type * n)()
    clGetContextInfo(context, param_name, sz.value, arr, None)
    if n == 1:
        return arr[0]
    else:
        return tuple(arr)

class Context:
    def __init__(self, platform, device):
        self.platform = platform
        self.device = device
        self.context = CreateContext(platform, device)
        self.reference_count = ContextInfo(self.context, CL_CONTEXT_REFERENCE_COUNT, c_uint32)
        self.num_devices = ContextInfo(self.context, CL_CONTEXT_NUM_DEVICES, c_uint32)

        self.dev_arr = (c_void_p * 1)()
        self.dev_arr[0] = device
        self.buffers = {}


    def build_program(self, kernel_name, source):
        c_source = c_char_p(bytes(source, 'ascii'))
        p = pointer(c_source)
        err_code = c_int32()
        program = clCreateProgramWithSource(self.context, 1, p, None, byref(err_code))
        ret = clBuildProgram(program, 1, self.dev_arr, None, None, None)
        if ret != CL_SUCCESS: 
            self.log = self._get_log(program)
            return False

        c_name = create_string_buffer(bytes(kernel_name, 'ascii'))
        #inofrmation about error TODO
        self.kernel = clCreateKernel(program, byref(c_name), byref(err_code))
        if err_code.value != CL_SUCCESS: return False
        return True

    def _get_log(self, program):
        sz = c_size_t()
        clGetProgramBuildInfo(program, self.device, CL_PROGRAM_BUILD_LOG, 0, None, byref(sz))
        param_value = create_string_buffer(sz.value)
        clGetProgramBuildInfo(program, self.device, CL_PROGRAM_BUILD_LOG, sz, param_value, None)
        return str(param_value.value, 'utf-8')

    def create_command_queue(self):

        err_code = c_int32()
        properties = c_ulonglong()
        properties.value = 0
        ret = clCreateCommandQueue(self.context, self.device, properties, byref(err_code))
        if err_code.value != CL_SUCCESS: return False
        self.command_queue = ret
        return True

    
    def create_buffer(self, name, size):

        err_code = c_int32()
        mem_flags = c_ulonglong()
        mem_flags.value = CL_MEM_READ_WRITE
        buff = clCreateBuffer(self.context, mem_flags, size, None, byref(err_code))
        if err_code.value != CL_SUCCESS: return False
        self.buffers[name] = buff
        return True

    def host_to_device(self, buff_name, host_addr, size):
        buff = self.buffers[buff_name]
        ret = clEnqueueWriteBuffer(self.command_queue, buff, True, 0, size, host_addr, 0, None, None)
        if ret != CL_SUCCESS: return False
        return True

    def device_to_host(self, buff_name, host_addr, size):
        buff = self.buffers[buff_name]
        ret = clEnqueueReadBuffer(self.command_queue, buff, True, 0, size, host_addr, 0, None, None)
        if ret != CL_SUCCESS: return False
        return True


KERNEL1 = """
    __kernel void add_vector(__global const float *a,
                            __global const float *b,
                            __global float *result)
    {
        int gid = get_global_id(0);
        result[gid] = a[gid] + b[gid];
    }
"""

platform = GetPlatform(0)
pl = Platform(platform)

device = GetDevice(0, CL_DEVICE_TYPE_GPU, platform)

con = Context(platform, device)

ret = con.build_program('add_vector', KERNEL1)
print(ret)

ret = con.create_command_queue()
print(ret)
ret = con.create_buffer("buf1", 1024)
print(ret)

arr = array.array('f')
arr.append(2.2)
arr.append(2.4)
arr.append(2.6)
arr.append(2.8)
print(arr.buffer_info())
adr = arr.buffer_info()[0]

print(arr)
arr2 = array.array('f', [0]*4)
print(arr2)

ret = con.host_to_device("buf1", adr, 16)
print(ret)

adr2 = arr2.buffer_info()[0]

ret = con.device_to_host("buf1", adr2, 16)
print(ret)

print(arr2)

