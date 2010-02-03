/**
 * Python SPICE wrapper header.
 *
 * This file contains some macros useful in the auto-generated spicemodule
 *
 * Author: Roberto Aguilar, roberto.c.aguilar@jpl.nasa.gov
 *
 * Released under the BSD license, see LICENSE for details
 *
 * $Id$
 */
#include <Python.h>
#include <SpiceUsr.h>

#include <stdio.h>

#ifndef __PYSPICE_H__
#define __PYSPICE_H__ 1

#define STRING_LEN 255
#define SPICE_DETAIL_LEN 1840

#define PYSPICE_CHECK_RETURN_STATUS(status) {                           \
    if(!status) {                                                       \
      return NULL;                                                      \
    }                                                                   \
  }

#define PYSPICE_MAKE_EXCEPTION(detail) {                                \
    PyObject *exception = NULL;                                         \
    exception = PyErr_NewException("spice.SpiceException", NULL, NULL); \
    PyErr_SetString(exception, detail);                                 \
  }

/* Stuff for getting the short error message
#define SPICE_MESSAGE_LEN 25
char *spice_msg = NULL;                                                 \
spice_msg = (char *)malloc(sizeof(char) * SPICE_MESSAGE_LEN);           \
getmsg_c("short", SPICE_MESSAGE_LEN, spice_msg);                        \
free(spice_msg);                                                        \
*/

#define PYSPICE_CHECK_FAILED {                                          \
    /* variables for exception handling */                              \
    char *spice_detail = NULL;                                          \
                                                                        \
    /* check if the function call failed */                             \
    if(failed_c()) {                                                    \
      spice_detail = (char *)malloc(sizeof(char) * SPICE_DETAIL_LEN);   \
                                                                        \
      getmsg_c("long", SPICE_DETAIL_LEN, spice_detail);                 \
                                                                        \
      reset_c();                                                        \
                                                                        \
      PYSPICE_MAKE_EXCEPTION(spice_detail);                             \
                                                                        \
      free(spice_detail);                                               \
                                                                        \
      failed = 1;                                                       \
    }                                                                   \
  }

/* Functions defined in the implementation file */
PyObject * get_py_ellipse(SpiceEllipse *spice_obj);
PyObject * get_py_cell(SpiceCell *cell);
PyObject * get_py_ekattdsc(SpiceEKAttDsc *spice_obj);
PyObject * get_py_eksegsum(SpiceEKSegSum *spice_obj);
PyObject * get_py_plane(SpicePlane *spice_obj);
SpiceCell * get_spice_cell(PyObject *py_obj);
SpiceEKAttDsc * get_spice_ekattdsc(PyObject *py_obj);
SpiceEKSegSum * get_spice_eksegsum(PyObject *py_obj);
SpicePlane * get_spice_plane(PyObject *py_obj);
SpiceEllipse * get_spice_ellipse(PyObject *ellipse);

/* Some test code */
PyObject * spice_berto(PyObject *self, PyObject *args);
PyObject * spice_test(PyObject *self, PyObject *args);

#endif /* __PYSPICE_H__ */
