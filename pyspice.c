/**
 * PySPICE implementation file
 *
 * This file contains some helper functions for going between C and Python
 *
 * Author: Roberto Aguilar, roberto.c.aguilar@jpl.nasa.gov
 *
 * Released under the BSD license, see LICENSE for details
 *
 * $Id$
 */
#include "pyspice.h"

void make_buildvalue_tuple(char *buf, const char *type, const int count)
{
    int i = 0;

    strcat(buf, "(");

    for(i = 0; i < count; ++ i) {
        strcat(buf, type);
    }

    strcat(buf, ")");
}

static PyObject * get_double_list(double *array, const int count)
{
    int i = 0;
    /* set the center */
    PyObject *list = PyList_New(count);

    if(list) {
        for(i = 0; i < count; ++ i) {
            PyObject *d = PyFloat_FromDouble(array[i]);
            PyList_SET_ITEM(list, i, d);
        }
    }

    return list;
}

/**
 * Create a Python Ellipse object from a SpiceEllipse object
 */
PyObject * get_py_ellipse(SpiceEllipse *spice_obj)
{
    PyObject *py_obj = NULL;
    PyObject *module = PyImport_ImportModule("spice");

    if(module) {
        PyObject *py_cls = PyObject_GetAttrString(module, "Ellipse");

        if(py_cls) {
            py_obj = PyObject_CallObject(py_cls, NULL);

            if(py_obj) {
                PyObject_SetAttrString(py_obj, "center", get_double_list(spice_obj->center, 3));
                PyObject_SetAttrString(py_obj, "semi_major", get_double_list(spice_obj->semiMajor, 3));
                PyObject_SetAttrString(py_obj, "semi_minor", get_double_list(spice_obj->semiMinor, 3));
            }
        }
    }

    return py_obj;
}

PyObject * get_py_cell(SpiceCell *cell)
{
    PyObject *py_obj = NULL;
    return py_obj;
}

PyObject * get_py_ekattdsc(SpiceEKAttDsc *spice_obj)
{
    PyObject *py_obj = NULL;
    return py_obj;
}

PyObject * get_py_eksegsum(SpiceEKSegSum *spice_obj)
{
    PyObject *py_obj = NULL;
    return py_obj;
}

PyObject * get_py_plane(SpicePlane *spice_obj)
{
    PyObject *py_obj = NULL;
    PyObject *module = PyImport_ImportModule("spice");

    if(module) {
        PyObject *py_cls = PyObject_GetAttrString(module, "Plane");

        if(py_cls) {
            py_obj = PyObject_CallObject(py_cls, NULL);

            if(py_obj) {
                PyObject_SetAttrString(py_obj, "constant", PyFloat_FromDouble(spice_obj->constant));
                PyObject_SetAttrString(py_obj, "normal", get_double_list(spice_obj->normal, 3));
            }
        }
    }

    return py_obj;
}


SpiceCell * get_spice_cell(PyObject *py_obj)
{
    SpiceCell *spice_obj = NULL;
    return spice_obj;
}

SpiceEKAttDsc * get_spice_ekattdsc(PyObject *py_obj)
{
    SpiceEKAttDsc *spice_obj = NULL;
    return spice_obj;
}

SpiceEKSegSum * get_spice_eksegsum(PyObject *py_obj)
{
    SpiceEKSegSum *spice_obj = NULL;
    return spice_obj;
}

SpicePlane * get_spice_plane(PyObject *py_obj)
{
    SpicePlane *spice_obj = malloc(sizeof(SpicePlane));

    PyObject *l = NULL, *f = NULL;

    /* set the constant variable in the spice_obj */
    f = PyObject_GetAttrString(py_obj, "constant");
    spice_obj->constant = PyFloat_AsDouble(f);

    /* now set each element in the normal array */
    l = PyObject_GetAttrString(py_obj, "normal");

    f = PyList_GetItem(l, 0);
    spice_obj->normal[0] = PyFloat_AsDouble(f);

    f = PyList_GetItem(l, 1);
    spice_obj->normal[1] = PyFloat_AsDouble(f);

    f = PyList_GetItem(l, 2);
    spice_obj->normal[2] = PyFloat_AsDouble(f);

    return spice_obj;
}

SpiceEllipse * get_spice_ellipse(PyObject *ellipse)
{
    char failed = 0, *sections[3] = {"center", "semi_major", "semi_minor"};
    int i, j;

    SpiceEllipse *spice_ellipse = malloc(sizeof(SpiceEllipse));

    double *ellipse_sections[3] = {spice_ellipse->center, spice_ellipse->semiMajor, spice_ellipse->semiMinor};

    for(i = 0; i < 3; ++ i) {
        PyObject *section = PyObject_GetAttrString(ellipse, sections[i]);

        if(section) {
            for(j = 0; j < 3; ++ j) {
                ellipse_sections[i][j] = PyFloat_AS_DOUBLE(PyList_GET_ITEM(section, j));
            }
        } else {
            failed = 1;
            break;
        }
    }

    if(failed) {
        free(spice_ellipse);
        spice_ellipse = NULL;
    }

    return spice_ellipse;
}

PyObject * spice_berto(PyObject *self, PyObject *args)
{
    PyObject *py_ellipse = NULL;

    PYSPICE_CHECK_RETURN_STATUS(PyArg_ParseTuple(args, "O", &py_ellipse));

    SpiceEllipse *spice_ellipse = get_spice_ellipse(py_ellipse);

    char *sections[3] = {"center", "semi_major", "semi_minor"};
    double *ellipse_sections[3] = {spice_ellipse->center, spice_ellipse->semiMajor, spice_ellipse->semiMinor};
    int i = 0, j = 0;

    for(i = 0; i < 3; ++ i) {
        for(j = 0; j < 3; ++ j) {
            printf ("%s[%d] = %f\n", sections[i], j, ellipse_sections[i][j]);
        }
    }

    spice_ellipse->center[0] = 1;
    spice_ellipse->center[1] = 2;
    spice_ellipse->center[2] = 3;
    spice_ellipse->semiMajor[0] = 4;
    spice_ellipse->semiMajor[1] = 5;
    spice_ellipse->semiMajor[2] = 6;
    spice_ellipse->semiMinor[0] = 7;
    spice_ellipse->semiMinor[1] = 8;
    spice_ellipse->semiMinor[2] = 9;

    py_ellipse = get_py_ellipse(spice_ellipse);

    free(spice_ellipse);

    return py_ellipse;
}

PyObject * spice_test(PyObject *self, PyObject *args)
{
    PyObject *py_obj = NULL;
    SpicePlane *plane = NULL;

    PYSPICE_CHECK_RETURN_STATUS(PyArg_ParseTuple(args, "O", &py_obj));

    plane = get_spice_plane(py_obj);

    PyObject *py_obj2 = get_py_plane(plane);
    free(plane);

    return py_obj2;
}
