#!/usr/bin/env python2.7

# Copyright 2014 California Institute of Technology.  ALL RIGHTS RESERVED.
# U.S. Government Sponsorship acknowledged.


import base64
import binascii
import datetime
import struct

import nose
import nose.tools

from bliss.core import dtype


def testArrayType():
    array  = dtype.ArrayType('MSB_U16', 3)
    bin123 = '\x00\x01\x00\x02\x00\x03'
    bin456 = '\x00\x04\x00\x05\x00\x06'

    assert array.name   == 'MSB_U16[3]'
    assert array.nbits  == 3 * 16
    assert array.nbytes == 3 *  2
    assert array.nelems == 3
    assert array.type   == dtype.PrimitiveType('MSB_U16')

    assert array.encode(1, 2, 3)   == bin123
    assert array.decode(bin456)    == [4, 5, 6]
    assert array.decode(bin456, 0) == 4
    assert array.decode(bin456, 1) == 5
    assert array.decode(bin456, 2) == 6
    assert array.decode(bin456, slice(1, 3)) == [5, 6]

    with nose.tools.assert_raises(ValueError):
        array.encode(1, 2)

    with nose.tools.assert_raises(IndexError):
        array.decode(bin456[1:5])

    with nose.tools.assert_raises(IndexError):
        array.decode(bin456, 3)

    with nose.tools.assert_raises(TypeError):
        array.decode(bin456, 'foo')

    with nose.tools.assert_raises(TypeError):
        dtype.ArrayType('U8', '4')





def testEVR16():
    """Test EVR16 complex data type"""
    dt   = dtype.EVRType()
    code = 0x0001
    name = "NO_ERROR"

    rawdata = bytearray(struct.pack('>H', code))

    assert dt.decode(rawdata).name == name
    assert dt.encode(name) == rawdata


def testTIME8():
    """Test TIME8 complex data type"""
    dt      = dtype.Time8Type()
    fine    = 17
    rawdata = bytearray(struct.pack('B', fine))

    expected = fine/256.0

    assert dt.decode(rawdata)  == expected
    assert dt.encode(expected) == rawdata


def testTIME32():
    """Test TIME32 complex data type"""
    dt  = dtype.Time32Type()
    sec = 1113733097

    rawdata = bytearray(struct.pack('>I', sec))
    date    = datetime.datetime(2015, 4, 22, 10, 18, 17)

    assert dt.decode(rawdata) == date
    assert dt.encode(date)    == rawdata


def testTIME40():
    """Test TIME40 complex data type"""
    dt   = dtype.Time40Type()
    sec  = 1113733097
    fine = 8

    # get raw data ready
    rawdata = bytearray(struct.pack('>I', sec))
    rawdata.extend(struct.pack('B', fine))

    # get the expected date
    date = datetime.datetime(2015, 4, 22, 10, 18, 17)

    # get expected fine string
    fine_exp = fine / 256.0
    fine_str = ('%f' % fine_exp).lstrip('0')

    # concatenate the expcted datetime value
    expected = ('%s%s' % (date, fine_str))

    assert dt.decode(rawdata)  == expected
    assert dt.encode(expected) == rawdata


def testTIME64():
    """Test TIME64 complex data type"""
    dt     = dtype.Time64Type()
    sec    = 1113733097
    subsec = 10
    
    rawdata = bytearray(struct.pack('>I', sec))
    rawdata.extend(struct.pack('>I', subsec))

    date = datetime.datetime(2015, 4, 22, 10, 18, 17)
    date = '%s.%010d' % (date, subsec)

    assert dt.decode(rawdata) == date
    assert dt.encode(date)    == rawdata


def testgetdtype():
    dt = dtype.get("TIME32")
    assert isinstance(dt, dtype.Time32Type)
    assert dt.name == "TIME32"
    assert dt.pdt  == "MSB_U32"
    assert dt.max  == 4294967295


def testget():
    assert isinstance( dtype.get("U8")    , dtype.PrimitiveType )
    assert isinstance( dtype.get("S40")   , dtype.PrimitiveType )
    assert isinstance( dtype.get("TIME32"), dtype.Time32Type    )

    assert dtype.get('LSB_U32[10]') == dtype.ArrayType('LSB_U32', 10)

    with nose.tools.assert_raises(ValueError):
        dtype.get('U8["foo"]')

    with nose.tools.assert_raises(ValueError):
        dtype.get('U8[-42]')


if __name__ == '__main__':
    nose.main()