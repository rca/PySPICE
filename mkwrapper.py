#!/usr/bin/env python
#
# Generate a SPICE python wrapper
#
# Run this command by providing the location of the unpacked toolkit
# directory:
#
# mkwrapper.py /path/to/cspice/toolkit
#
# Author: Roberto Aguilar, roberto.c.aguilar@jpl.nasa.gov
#
# Released under the BSD license, see LICENSE for details
#
# $Id$

import os, sys
from cStringIO import StringIO

# This is a parameter class that is used to hold all the information about a
# parameter.  Initially there is nothing in it.  The object is populated with
# arbritrary information as the items are needed.  This is controlled using
# the setattr and getattr functions in the class
class Container(dict):
    def __getattr__(self, key):
        val = self.get(key, None)

        return val

    def __setattr__(self, key, val):
        self[key] = val


# look for these types of functions in the input stream in order to
# generate the wrappers.
function_types = ('ConstSpiceChar', 'SpiceBoolean', 'SpiceChar', 'SpiceDouble', 'SpiceInt', 'void')

RESERVED_NAMES = ('free',)

# Reasons for excluding the following functions
# appnd*, etc. - not looked into translating a SpiceCell to a python object yet.
# axisar_c - haven't written code to parse arrays
# bodvar_c - deprecated
# bschoc_c, etc. - how to support const void * array
# ckw05_c - how to support SpiceCK05Subtype
# maxd_c - variable length inputs
# spkw18_c - how to support SpiceSPK18Subtype
# dafgs_c - how to deal with an array that doesn't have the number of elements
# dasec_c - how to handle void types in parameter list
# dafgh_c - does function actually exist?  I found no C file ...
# ucase_c - not needed for python
# gfevnt_c, gffove_c, gfocce_c, gfuds_c, uddc_c, uddf_c - how to support callbacks
exclude_list = (
    'cnames',

    'appndc_c', 'appndd_c', 'appndi_c', 'zzsynccl_c',

    'bodvar_c',

    'bschoc_c', 'bsrchc_c', 'dafac_c', 'dafec_c', 'dasac_c', 'ekacec_c',
    'ekaclc_c', 'ekbseg_c', 'zzgetcml_c', 'ekifld_c', 'ekucec_c', 'esrchc_c',
    'getelm_c', 'isrchc_c', 'kxtrct_c', 'lmpool_c', 'lstlec_c', 'lstltc_c',
    'mequg_c', 'mtxmg_c', 'mtxvg_c', 'mxmg_c', 'mtmtg_c', 'mxmtg_c', 'mxvg_c',
    'orderc_c', 'pcpool_c', 'swpool_c', 'vtmvg_c', 'xposeg_c',

    'ckw05_c',

    'maxd_c', 'maxi_c', 'mind_c', 'mini_c',

    'spkw18_c',

    'dafgs_c', 'dafps_c', 'dafus_c', 'getfov_c',
    'ckw01_c', 'ckw02_c', 'ckw03_c', 'spk14a_c', 'spkw02_c', 'spkw03_c',
    'spkw05_c', 'spkw08_c', 'spkw09_c', 'spkw10_c', 'spkw12_c', 'spkw13_c',

    'dasec_c', 'ekpsel_c', 'ekrcec_c', 'gcpool_c', 'gnpool_c',

    'dafgh_c', 'prefix_c',

    'lcase_c', 'ucase_c', 'getcml_c', 'lparse_c', 'lparsm_c', 'prompt_c',
    'putcml_c', 'reordc_c', 'shellc_c', 'sumad_c', 'sumai_c',

    'gfevnt_c', 'gffove_c', 'gfocce_c', 'gfuds_c', 'uddc_c', 'uddf_c',
)

module_defs = []
cspice_src = None

DEBUG = 0 # set it on when string is the right one

INPUT_TYPE = 0
OUTPUT_TYPE = 1

def debug(string):
    if DEBUG: sys.stderr.write("%s\n" % str(string))

def determine_py_type(param_obj):
    type = param_obj.type

    param_obj.py_string = ''
    param_obj.spice_obj = None

    # functions to get a python object or spice object, respectively, for the
    # given variable
    param_obj.get_py_fn = None
    param_obj.get_spice_fn = None

    # determine the type of python variable this would be
    if type in ('SpiceChar', 'ConstSpiceChar', 'SpiceChar'):
        param_obj.py_string = 's'
    elif type in ('ConstSpiceDouble', 'SpiceDouble'):
        param_obj.py_string = 'd'
    elif type in ('ConstSpiceBoolean', 'SpiceBoolean'):
        param_obj.py_string = 'i'
    elif type in ('ConstSpiceInt', 'SpiceInt'):
        # put a long for a spice int since they are long integers
        param_obj.py_string = 'l'
    elif type == 'SpiceCell':
        param_obj.py_string = 'O'
        param_obj.spice_obj = 'Cell'
        param_obj.get_py_fn = 'get_py_cell'
        param_obj.get_spice_fn = 'get_spice_cell'
    elif type in ('ConstSpiceEllipse', 'SpiceEllipse'):
        param_obj.py_string = 'O'
        param_obj.spice_obj = 'Ellipse'
        param_obj.get_py_fn = 'get_py_ellipse'
        param_obj.get_spice_fn = 'get_spice_ellipse'
    elif type == 'SpiceEKAttDsc':
        param_obj.py_string = 'O'
        param_obj.spice_obj = 'EkAttDsc'
        param_obj.get_py_fn = 'get_py_ekattdsc'
        param_obj.get_spice_fn = 'get_spice_ekattdsc'
    elif type == 'SpiceEKSegSum':
        param_obj.py_string = 'O'
        param_obj.spice_obj = 'EkSegSum'
        param_obj.get_py_fn = 'get_py_eksegsum'
        param_obj.get_spice_fn = 'get_spice_eksegsum'
    elif type in ('ConstSpicePlane', 'SpicePlane'):
        param_obj.py_string = 'O'
        param_obj.spice_obj = 'Plane'
        param_obj.get_py_fn = 'get_py_plane'
        param_obj.get_spice_fn = 'get_spice_plane'
    elif type in ('void'):
        param_obj.py_string = ''
    else:
        sys.stderr.write('Warning: Unknown type: %s\n' % type)

def get_doc(function_name):
    doc = StringIO()

    # the sections of documentation we want
    sections = [
        '-Abstract',
        '-Brief_I/O',
        '-Detailed_Input',
        '-Detailed_Output',
    ]

    src_file = "%s/%s.c" % (cspice_src, function_name)

    if os.path.exists(src_file):
        f = open(src_file, 'r')

        # loop for going through the entire source file
        while 1:
            input = f.readline()
            input_len = len(input)

            if not input: break

            input = input.rstrip()

            # skip blank lines
            if input == "": continue

            #print "input: %s" % input

            split = input.split()

            if split[0] in sections:
                while 1:
                    if not input:
                        doc.write('\\n')
                    else:
                        doc.write('%s\\n' % input.replace('\\', '\\\\').replace('"', '\\"'))

                    input = f.readline()
                    input_len = len(input)
                    input = input.rstrip()

                    if not input:
                        continue
                    elif input[0] == '-':
                        f.seek(f.tell()-input_len)
                        break

        # t = f.readlines()
        f.close()

    return '"%s"' % doc.getvalue()

def gen_wrapper(prototype, buffer):
    prototype = remove_extra_spaces(prototype)
    manually_build_returnVal = False
    input_list = []
    input_name_list = []
    output_list = []
    output_name_list = []

    # keep track of whether a character string was found as an output.
    # if one was found, one of the inputs to the C function is the
    # length of the string.  since python takes care of this behind
    # the scenes, there will not be a length input from the python
    # script, so pass in the size of the locally made string (most
    # likely STRING_LEN above).
    string_output_num = 0

    # parse up the given prototype into its fundamental pieces.  this function
    # returns a container object with all the information parsed up.
    prototype_obj = parse_prototype(prototype)

    # check the exclude list before continuing
    if prototype_obj.function_name in exclude_list: return False

    # the string that is passed to PyArg_ParseTuple for getting the
    # arguments list and Py_BuildValue for returning results
    parse_tuple_string = ""
    buildvalue_string = ""

    # remove the _c suffix for the python function name
    python_function_name = prototype_obj.function_name.rsplit('_c',1)[0]

    # Add the C function prototype to the source code output.
    t = '/* %s */' % prototype
    prototype_comment_list = []
    while len(t) > 80:
        count = 79
        while t[count-1] != ',' and count > 1:
            count -= 1

        prototype_comment_list.append(t[:count])
        t = t[count:]
    if t:
        prototype_comment_list.append(t)

    prototype_comment = '\n'.join(prototype_comment_list)

    # declare the function for this wrapper
    buffer.write(
        "\n%s\nstatic PyObject * spice_%s(PyObject *self, PyObject *args)\n{" % \
        (prototype_comment, python_function_name));

    # split up the inputs from the outputs so that only inputs have to
    # be provided to the function from python and the outputs are
    # returned to python, e.g. et = utc2et("SOME DATE")
    last_item = None
    t_type = None
    for param in prototype_obj.params:
        #debug('')
        param_info = parse_param(param)
        if param_info is None:
            continue
        #debug("parsed param: %s" % param_info)

        if param_info.is_array and not param_info.is_const:
            t_type = OUTPUT_TYPE
        elif param_info.is_const or not param_info.is_pointer:
            t_type = INPUT_TYPE
        elif param_info.is_pointer:
            t_type = OUTPUT_TYPE
        else:
            raise Exception("I don't know if %s is an input or output" % param)

        # tack the parameter type onto the param_info tuple
        param_info.param_type = t_type

        # if the last param was counted as an output, but this param
        # is an input, bring the last entered item to this list
        # because it was miscategorized
        #
        # TODO: This is a HUGE hack and would be nice to find an alternate
        # way of deciding this).

        if last_item is not None and \
                t_type == INPUT_TYPE and last_item.param_type == OUTPUT_TYPE:
            output_list.remove(last_item)
            input_list.append(last_item)

        if t_type == INPUT_TYPE:
            input_list.append(param_info)
        else:
            output_list.append(param_info)

        last_item = param_info
        #debug("param after hack: %s" % param_info)

    #debug("")

    # parse the outputs
    if output_list:
        buffer.write("\n  /* variables for outputs */")

    #print 'function_name: %s' % function_name

    # the bodv* functions pass in 'maxn', which is the number of elements in
    # the output array 'values'.  detect this case and allocate memory for the
    # values array.
    #
    # the allocate_memory variable points to the last input variable, which
    # should be the variable pointing to the max number of items in the array
    if prototype_obj.function_name.startswith('bodv'):
        output_list[-1].make_pointer = True
        output_list[-1].allocate_memory = input_list[-1].name
        manually_build_returnVal = True
        pass

    for output in output_list:
        #print output

        # declare the variable
        buffer.write("\n  %s" % output.type)

        if output.make_pointer:
            buffer.write(" *")

        buffer.write(" %s" % output.name)

        # this item may be an array pointer, so only add the brackets
        # if no memory allocation was done for this variable
        if output.is_array and not output.allocate_memory:
            for count in output.num_elements:
                try:
                    buffer.write("[%d]" % count)
                except:
                    buffer.write("[]")

        if output.type == 'SpiceChar' and not output.is_array:
            string_output_num += 1
            buffer.write("[STRING_LEN]")

        buffer.write(";")

        output_name_list.append(output.name)

    # parse the inputs
    if input_list:
        buffer.write("\n  /* variables for inputs */")

    # in the loop below, the variables are being declared as type
    # 'reg_type'.  this is because python was not properly parsing the
    # arguments passed in from Python when using SPICE variable types.
    py_to_c_conversions = [];

    for input in input_list:
        input_name = input.name

        # if a character string output was detected and this variable has the
        # string 'len' in it, skip adding it to the ParseTuple string.
        if 'len' in input_name and string_output_num > 0:
            buffer.write("\n  %s %s = STRING_LEN;" % \
                         (input.reg_type, input_name)
            )
        else:
            parse_tuple_string += input.py_string

            if input.is_pointer:
                pointer_string = " * "
            else:
                pointer_string = " "

            buffer.write("\n  %s%s%s" % (
                input.reg_type, pointer_string, input_name))

            if input.is_array:
                for count in input.num_elements:
                    buffer.write("[%s]" % count)

            buffer.write(";")

            # if this input has a get_spice_fn function associated with it,
            # declare a variable for the conversion
            if input.get_spice_fn:
                input_name = "py_%s" % input_name
                buffer.write("\n  PyObject * %s = NULL;" % input_name)
                py_to_c_conversions.append("%s = %s(%s);" % (input.name, input.get_spice_fn, input_name))

            # if this is an array, put in the right amount of elements
            # into the ParseTuple parameter list (one per element).
            # Also, the list coming in can be 1D, 2D, or 3D.
            if input.is_array:
                input_name_list += get_array_sizes(
                    input.num_elements, input_name)
            else:
                input_name_list.append(input_name)

    # other variables needed below
    buffer.write('\n\n  char failed = 0;')

    if not manually_build_returnVal and output_list:
        buffer.write('\n  char buildvalue_string[STRING_LEN] = "";')

    # configure the input string list for parsing the args tuple
    input_list_string = "&" + ", &".join(input_name_list)

    # if the function type is not void, declare a variable for the
    # result.
    if prototype_obj.type != "void":
        buffer.write("\n\n  /* variable for result */")

        if prototype_obj.is_pointer:
            t_pointer = " * "
        else:
            t_pointer = " "

        buffer.write("\n  %s%sresult;" % (prototype_obj.type, t_pointer))

    buffer.write("\n")

    # generate the PyArg_ParseTuple call if there were any inputs to
    # this function
    if input_name_list:
        buffer.write(
            ('\n  PYSPICE_CHECK_RETURN_STATUS(' +
             'PyArg_ParseTuple(args, "%s", %s));') % \
            (parse_tuple_string, input_list_string))

    # if there are any Python -> C conversions that need to occur, add them here.
    if py_to_c_conversions:
        buffer.write('\n  %s\n' % '\n'.join(py_to_c_conversions))

    for output in output_list:
        # see if memory needs to be allocated for this variable
        if output.allocate_memory:
            buffer.write("\n\n  %s = malloc(sizeof(%s) * %s);" % \
                (output.name, output.type, output.allocate_memory))

    # build the input name list for calling the C function
    input_name_list = []
    for input in input_list:
        input_name_list.append(input.name)

    # combine the input name list and the output name list for the C
    # function call
    if input_list:
        input_list_string = ", ".join(input_name_list)
    else:
        input_list_string = ""

    # build the output name list for calling the C function
    t_list = []
    for output in output_list:
        if any([output.is_array,
                output.type == "SpiceChar",
                output.allocate_memory]):
            t_list.append(output.name)
        else:
            t_list.append("&" + output.name)

    if t_list:
        output_list_string = ', '.join(t_list)
    else:
        output_list_string = ''

    #debug("output list: %s" % output_list_string)

    if input_list_string and output_list_string:
        param_list_string = "%s, %s" % (input_list_string, output_list_string)
    elif input_list_string:
        param_list_string = input_list_string
    else:
        param_list_string = output_list_string

    # debug(param_list_string)

    # Call the C function
    if prototype_obj.type != "void":
        buffer.write("\n  result = %s(%s);" % (prototype_obj.function_name, param_list_string))
    else:
        buffer.write("\n  %s(%s);" % (prototype_obj.function_name, param_list_string))

    # run the macro to check to see if an exception was raised.  once the
    # check is made, see if the failed boolean was set.  this is an indication
    # that the function should free any allocated memory and return NULL.
    buffer.write("\n\n  PYSPICE_CHECK_FAILED;\n")

    buffer.write('\n  if(failed) {')

    for output in output_list:
        if output.allocate_memory:
            buffer.write('\n    free(%s);' % output.name)

    buffer.write('\n    return NULL;')
    buffer.write('\n  }\n')

    # loop through the output to build the value strings for each output if
    # the return value is not being built up manually
    if not manually_build_returnVal:
        if output_list:
            buffer.write('\n  /* put together the output buildvalue string */')

        for output in output_list:
            if output.allocate_memory:
                buffer.write(
                    ('\n  make_buildvalue_tuple(buildvalue_string, ' +
                    '"%s", %s);') % (output.py_string, output.name)
                )
            elif output.name != 'found':
                buffer.write(
                    '\n  strcat(buildvalue_string, "%s");' % output.py_string
                )

        buffer.write('\n')

    # If the called function is a void, return PyNone, or else figure out what
    # to return.
    if output_list:
        # output_list_string = ', '.join(output_list)
        #debug('output_list: '.format(output_list))
        if manually_build_returnVal:
            #debug('in manual returnVal build')
            make_manual_returnVal(buffer, output_list)
        else:
            #debug('in automatic returnVal build')
            make_automatic_returnVal(buffer, output_list)
    elif prototype_obj.type == "void":
        buffer.write("\n  Py_INCREF(Py_None);")
        buffer.write("\n  return Py_None;")
    elif prototype_obj.type == "SpiceBoolean":
        buffer.write("\n  if(result) { Py_RETURN_TRUE; } else { Py_RETURN_FALSE; }")
    elif prototype_obj.type in ("ConstSpiceChar", "SpiceDouble", "SpiceInt"):
        buffer.write('\n  return Py_BuildValue("%s", result);' % prototype_obj.py_string)
    else:
        pass # for now; TODO: figure out what to do

    buffer.write("\n}");

    # dig out the function name from the source file
    doc = get_doc(prototype_obj.function_name)

    if not doc:
        buffer.write('\nPyDoc_STRVAR(%s_doc, "");\n' % python_function_name)
    else:
        buffer.write('\nPyDoc_STRVAR(%s_doc, %s);\n' % (python_function_name, doc))

    # add this functions definition to the module_defs list
    module_defs.append('{"%s", spice_%s, METH_VARARGS, %s_doc},' % \
                       (python_function_name, python_function_name, python_function_name))

    return buffer.getvalue()

def get_array_sizes(list, name):
    """
    Expand the elements of an array for 1, 2, and 3D arrays
    """
    t_list = []

    if len(list) == 1:
        for t in range(0, list[0]):
            t_list.append(name + "[%s]" % t)
    elif len(list) == 2:
        for t1 in range(0, list[0]):
            for t2 in range(0, list[1]):
                    t_list.append(name + "[%s][%s]" % (t1, t2))
    elif len(list) == 3:
        for t1 in range(0, list[0]):
            for t2 in range(0, list[1]):
                for t3 in range(0, list[2]):
                    t_list.append(name + "[%s][%s][%s]" % (t1, t2, t3))

    return t_list

def make_automatic_returnVal(buffer, output_list):
    """
    The outputs parameters and their dimensions are defined so this function
    can be used.
    """

    # put together the outputs
    t_list = []
    buildvalue_string = ''

    # Check_found is used to indicate whether a found variable was
    # passed along with other output variables.  check_found is set to
    # True if the found variable indicating that the additional
    # outputs are valid.  This way, if nothing was found, the function
    # returns None instead of the output variables requested.
    check_found = False

    for output in output_list:
        # if the length of the output list is only 1 and it's found,
        # return true or false, otherwise, if found is false return None.
        if output.name == "found":
            if len(output_list) == 1:
                buffer.write(
                    '\n  if(found) { Py_RETURN_TRUE; } ' +
                    'else { Py_RETURN_FALSE; }'
                )
            else:
                check_found = True
            continue

        # If the output is an array, expand out all the elements in order
        # to build a python tuple out of them (This seems sub-optimal, I
        # have to read some more python C documentation).
        if output.is_array:
            t_list += get_array_sizes(output.num_elements, output.name)
        elif(output.get_py_fn):
            t_list.append('%s(&%s)' % (output.get_py_fn, output.name))
        else:
            t_list.append(output.name)

        buildvalue_string += output.py_string

    output_list_string = ", ".join(t_list)

    if output_list_string:
        if check_found:
            buffer.write(
                '\n  if(!found) {\n    return Py_None;\n  } else {\n    ')
        else:
            buffer.write('\n  ')

        buffer.write(
            'PyObject *returnVal = Py_BuildValue(buildvalue_string, %s);' % \
            (output_list_string))

        for output in output_list:
            if output.allocate_memory:
                buffer.write('\n  free(%s);' % output.name)

        buffer.write('\n  return returnVal;');

        if check_found:
            buffer.write('\n  }\n')

def make_manual_returnVal(buffer, output_list):
    """
    This returnVal function is used when the output dimensions are dynamic.
    For instance, a double * and an integer specifying the number of elements
    in that array are passed in.  In order to properly build the return tuple,
    this function can be used.
    """

    buffer.write('\n  int i = 0;')
    buffer.write('\n  PyObject *t = NULL;')
    buffer.write(
        '\n  PyObject *returnVal = PyTuple_New(%d);' % len(output_list))

    count = 0;
    for count in range(len(output_list)):
        output = output_list[count]

        if output.allocate_memory:
            buffer.write('\n  t = PyTuple_New(%s);' % output_list[0].name)
            buffer.write(
                '\n  for(i = 0; i < %s; ++ i) {' % output_list[0].name
            )
            buffer.write(
                '\n    PyTuple_SET_ITEM(t, i, Py_BuildValue("%s", %s[i]));' % \
                (output.py_string, output.name)
            )
            buffer.write('\n  }')
            buffer.write('\n  PyTuple_SET_ITEM(returnVal, %d, t);' % count)
        else:
            buffer.write(
                '\n  PyTuple_SET_ITEM(returnVal, %d, Py_BuildValue("%s", %s));' % \
                (count, output.py_string, output.name)
            )

    buffer.write('\n  return returnVal;');

def get_type(type):
    reg_type = type

    # determine the type of python variable this would be
    if type in ('SpiceChar', 'ConstSpiceChar', 'SpiceChar'):
        reg_type = 'char'
    elif type in ('ConstSpiceDouble', 'SpiceDouble'):
        reg_type = 'double'
    elif type in ('ConstSpiceBoolean', 'SpiceBoolean'):
        reg_type = 'char'
    elif type in ('ConstSpiceInt', 'SpiceInt'):
        # put a long for a spice int since they are long integers
        reg_type = 'long'

    return reg_type

def get_tuple_py_string(param_obj, curr_depth=0):
    """
    Put together the tuple string based on the number of elements in
    the given elements list.  if this was a one demensional array, the
    list would simply be, for example [3], where 3 is the number of
    elements in the array.  A 3x3 2D array would be [3, 3] a 3x3x3 3D
    array is: [3, 3, 3].  The output for these examples would be:

    (xxx)
    ((xxx)(xxx)(xxx))
    (((xxx)(xxx)(xxx))((xxx)(xxx)(xxx))((xxx)(xxx)(xxx)))
    """

    list = param_obj.num_elements
    char = param_obj.py_string

    t = "("

    for i in range(0, list[curr_depth]):
        if curr_depth < (len(list) - 1):
            t += get_tuple_py_string(param_obj, (curr_depth+1))
        else:
            t += char

    t += ")"

    return t

def fixNameCollision(name):
    if name in RESERVED_NAMES:
        return name + '_'
    else:
        return name

def parse_param(param):
    """
    Take the given parameter and break it up into the type of
    variable, the variable name and whether it's a pointer.
    """

    param_obj = Container()

    param = remove_extra_spaces(param)
    param_split = param.split(" ")

    param_obj.original = param

    #debug('param: %s' % param)
    #debug('param_split: %s' % str(param_split))

    index = 0

    type = param_split[index]
    index += 1

    if type == 'const':
        param_obj.is_const = True
        type = param_split[index]
        index += 1
    else:
        param_obj.is_const = False

    param_obj.type = type
    param_obj.reg_type = get_type(type)

    try:
        name = param_split[index]
        index += 1

        # check to see if the second element in the split list is a
        # pointer, if so, set the is_pointer var to True and set the name
        # to the next element in the list
        if name == "*":
            param_obj.is_pointer = True
            name = param_split[index]
            index += 1
        else:
            param_obj.is_pointer = False

        # now check to see if the pointer is stuck on the variable
        if name[0] == "*":
            param_obj.is_pointer = True
            name = name[1:]

        # check for const in the type name
        if type.startswith('Const'):
            param_obj.is_const = True

        # look for brackets in the param string.  this can be a 1D
        # array, e.g. int x[3] or a multidimensional array, e.g. int
        # x[4][4]
        start_find = 0
        param_obj.num_elements = []

        while 1:
            open_bracket_pos = param.find('[', start_find)
            start_find = open_bracket_pos + 1

            #debug('open_bracket_pos: %s' % open_bracket_pos)

            # if no open bracket was found, break out of the loop
            if open_bracket_pos == -1:
                break
            close_bracket_pos = param.find(']', start_find)

            #debug('close_bracket_pos: %s' % close_bracket_pos)

            # try to convert the number of the elements into an
            # integer.  this may fail if the brackets are empty.  If
            # they are empty, don't fail, or else raise the exception.
            t = param[open_bracket_pos+1:close_bracket_pos]

            #debug('t: %s' % t)

            try:
                param_obj.num_elements.append(int(t))
            except Exception, msg:
                if t:
                    raise msg
                param_obj.num_elements.append('')

            #debug('num_elements: %s' % str(param_obj.num_elements))

        #debug('num_elements (out of loop): %s' % param_obj.num_elements)

        # check if the bracket was stuck on the variable and
        # remove it
        name_bracket_pos = name.find('[')
        if name_bracket_pos > -1:
            name = name[0:name_bracket_pos]

        param_obj.name = fixNameCollision(name)
        param_obj.is_array = len(param_obj.num_elements)
        determine_py_type(param_obj)

        #debug('type: %s' % param_obj.type)
        #debug('is_const: %s' % param_obj.is_const)
        #debug('name: %s' % param_obj.name)
        #debug('is_pointer: %s' % param_obj.is_pointer)
        #debug('is_array: %s' % str(param_obj.is_array))
        #debug('py_string: %s' % param_obj.py_string)

        if param_obj.is_array:
            param_obj.py_string = get_tuple_py_string(param_obj)

        return param_obj
    except Exception, msg:
        if type == 'void':
            return None
        else:
            raise msg

def parse_prototype(prototype):
    """
    Take the given function prototype and break it up into the type of
    function, the function name, whether it is a pointer and the
    parameters it takes.
    """

    prototype = prototype.strip()
    prototype_split = prototype.split(" ")
    type = prototype_split[0]
    prototype_obj = Container()

    if prototype_split[1] == "*":
        is_pointer = True
        function_name = prototype_split[2]
        params = " ".join(prototype_split[3:])
    else:
        is_pointer = False
        function_name = prototype_split[1]
        params = " ".join(prototype_split[2:])

    # if the function's open paren is stuck to the function name, remove it
    if function_name.endswith("("):
        function_name = function_name.rstrip('(')
        params = "(" + params

    # if the pointer was stuck to the function name, remove it
    if function_name.startswith('*'):
        is_pointer = True
        function_name = function_name.lstrip('*')

    try:
        params = params[params.index("(")+1:params.index(")")].strip().split(",")

        #debug("type: %s, function: %s, is_pointer: %s, params: %s" % \
            # (type, function_name, is_pointer, params))
    except:
        #debug("unable to parse params for function %s" % function_name)
        debug(function_name[-1])

    prototype_obj.type = type
    prototype_obj.is_pointer = is_pointer
    prototype_obj.function_name = function_name
    prototype_obj.params = params
    determine_py_type(prototype_obj)

    #debug('function_name: %s, type: %s, py_string: %s\n' % \
        # (prototype_obj.function_name,
        #  prototype_obj.type,
        #  prototype_obj.py_string))

    return prototype_obj

def remove_extra_spaces(string):
    """
    strip out extra spaces in the given string
    """

    string = string.strip()

    last_char = ""

    i = 0
    while i < len(string):
        s = string[i]

        if s == " " and last_char == " ":
            string = string[0:i] + string[i+1:]
        else:
            i += 1

        last_char = s

    return string

def run_command(command, writer):
    """
    run_command(command, writer)

    Run the given command and write the output to the given writer object

    command - a string representing the command to run
    writer  - any object that has a write(string) function.

    The function returns the given command's exit status.

    Here's a typical usage scenario:

    # import everything from this module
    from command import *

    # create a StringIO object
    s = StringIO()

    # run the desired command
    status = run_command('ls', s)

    # print the result
    print s.getvalue()

    # print the command's exit status
    print 'exit status: %d' % (status,)
    """

    command_handle = os.popen(command, 'r')

    output = command_handle.read()
    writer.write(output)

    return command_handle.close()

def main(cspice_toolkit):
    global cspice_src

    parsing_prototype = False
    curr_prototype = ''
    module_methods = StringIO()
    buffer = StringIO()

    cspice_header = os.path.join(cspice_toolkit, 'include', 'SpiceUsr.h')
    cspice_src = os.path.join(cspice_toolkit, 'src', 'cspice')

    if not os.path.exists(cspice_header):
        sys.exit('Error: Unable to find %s' % cspice_header)

    if not os.path.exists(cspice_src):
        sys.exit('Error: Unable to find %s' % cspice_header)

    # preprocess the header file
    output = StringIO()
    run_command('gcc -E %s' % cspice_header, output)
    output.reset()

    used_prototypes = 0
    total_prototypes = 0;
    line_no = 0
    while 1:
        input = output.readline()
        line_no +=1
        # #debug('line: {1}, input: {0}'.format(input,line_no))
        if input == "":
            break
        input = input.strip()

        if input == "":
            continue
        # if parsing still false and line does not have opening bracket
        elif not parsing_prototype and "(" not in input:
            continue
        if parsing_prototype:
            # #debug("parse_adding: %s" % input)

            curr_prototype += input

            # #debug("curr_prototype now: %s" % curr_prototype)

            # if the last character is a semi-colon, the prototype is
            # complete, pass it along to the wrapper generator and clear
            # out the curr_prototype variable
            if input.endswith(";"):
                parsing_prototype = False

                # gen_wrapper can return False, then don't count it as used
                #debug('')
                #debug('%s\n' % curr_prototype)
                if gen_wrapper(curr_prototype, buffer):
                    used_prototypes += 1
                total_prototypes += 1

                curr_prototype = ""
            pass
        else:
            first_word = input[0:input.index(" ")]
            # #debug('first_word: {0}'.format(first_word))
            if first_word in function_types:
                # #debug("adding %s" % input)

                curr_prototype += input

                # #debug("curr_prototype now: %s" % curr_prototype)
            else:
                continue
            if input.endswith(";"):
                # #debug("prototype to be wrapped: {0}".format(curr_prototype))
                gen_wrapper(curr_prototype, buffer)
                curr_prototype = ""
            else:
                parsing_prototype = True

    sys.stderr.write("prototypes used: %d, total: %d\n" % (used_prototypes, total_prototypes))
    # put together the methods array
    for module_def in module_defs:
        module_methods.write("\n  %s" % module_def)

    # print out necessary boilerplate stuff
    return """\
/*
THIS IS AUTOMATICALLY GENERATED CODE.  IF THERE IS AN ERROR, PLEASE
MAKE ANY NECESSARY CHANGES IN THE PYTHON SCRIPT NAMED mkwrapper.py.

THIS CODE HAS NOT BEEN THOROUGHLY TESTED, USE AT YOUR OWN RISK, THE
AUTHOR(S) IS/ARE NOT RESPONSIBLE IF YOUR CRAFT GOES DOWN, BLAH BLAH
BLAH.  SEE FILE "LICENSE" FOR MORE INFO.
*/

#include "pyspice.h"

PyObject *SpiceException;

%s
PyMethodDef methods[] = {
%s
  {NULL, NULL},
};

void init_spice(PyObject *self)
{
  PyObject *m = NULL;

  m = Py_InitModule("_spice", methods);

  /* Don't allow an exception to stop execution */
  erract_c("SET", 0, "RETURN");
  errdev_c("SET", 0, "NULL");

  SpiceException = \
    PyErr_NewException("_spice.SpiceException", PyExc_Exception, NULL);
  Py_INCREF(SpiceException);

  PyModule_AddObject(m, "SpiceException", SpiceException);
}""" % (buffer.getvalue(), module_methods.getvalue())

if __name__ == '__main__':
    if sys.argv:
        cspice_toolkit = sys.argv[1]
    else:
        sys.exit('Please provide the path to the unpacked cspice toolkit directory')

    print main(cspice_toolkit)
