#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/validators.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/validators.py,v 1.30 2003/12/10 14:40:13 rgbecker Exp $
__version__=''' $Id$ '''
"""
This module contains some standard verifying functions which can be
used in an attribute map.
"""

import string, sys
from types import *
_SequenceTypes = (ListType,TupleType)
_NumberTypes = (FloatType,IntType)
from reportlab.lib import colors
if sys.hexversion<0x2030000:
    True = 1
    False = 0

class Validator:
    "base validator class"
    def __call__(self,x):
        return self.test(x)

    def __str__(self):
        return getattr(self,'_str',self.__class__.__name__)

    def normalize(self,x):
        return x

    def normalizeTest(self,x):
        try:
            self.normalize(x)
            return True
        except:
            return False

class _isAnything(Validator):
    def test(self,x):
        return True

class _isNothing(Validator):
    def test(self,x):
        return False

class _isBoolean(Validator):
    if sys.hexversion>=0x2030000:
        def test(self,x):
            if type(x) in (IntType,BooleanType): return x in (0,1)
            return self.normalizeTest(x)
    else:
        def test(self,x):
            if type(x) is IntType: return x in (0,1)
            return self.normalizeTest(x)

    def normalize(self,x):
        if x in (0,1): return x
        try:
            S = string.upper(x)
        except:
            raise ValueError, 'Must be boolean'
        if S in ('YES','TRUE'): return True
        if S in ('NO','FALSE',None): return False
        raise ValueError, 'Must be boolean'

class _isString(Validator):
    def test(self,x):
        return type(x) in (StringType, UnicodeType)

class _isNumber(Validator):
    def test(self,x):
        if type(x) in _NumberTypes: return True
        return self.normalizeTest(x)

    def normalize(self,x):
        try:
            return float(x)
        except:
            return int(x)

class _isInt(Validator):
    def test(self,x):
        if type(x) not in (IntType,StringType): return False
        return self.normalizeTest(x)

    def normalize(self,x):
        return int(x)

class _isNumberOrNone(_isNumber):
    def test(self,x):
        return x is None or isNumber(x)

    def normalize(self,x):
        if x is None: return x
        return _isNumber.normalize(x)

class _isListOfNumbersOrNone(Validator):
    "ListOfNumbersOrNone validator class."
    def test(self, x):
        if x is None: return True
        return isListOfNumbers(x)

class _isListOfShapes(Validator):
    "ListOfShapes validator class."
    def test(self, x):
        from reportlab.graphics.shapes import Shape
        if type(x) in _SequenceTypes:
            answer = 1
            for element in x:
                if not isinstance(x, Shape):
                    answer = 0
            return answer
        else:
            return False

class _isListOfStringsOrNone(Validator):
    "ListOfStringsOrNone validator class."

    def test(self, x):
        if x is None: return True
        return isListOfStrings(x)

class _isTransform(Validator):
    "Transform validator class."
    def test(self, x):
        if type(x) in _SequenceTypes:
            if len(x) == 6:
                for element in x:
                    if not isNumber(element):
                        return False
                return True
            else:
                return False
        else:
            return False

class _isColor(Validator):
    "Color validator class."
    def test(self, x):
        return isinstance(x, colors.Color)

class _isColorOrNone(Validator):
    "ColorOrNone validator class."
    def test(self, x):
        if x is None: return True
        return isColor(x)

class _isValidChild(Validator):
    "ValidChild validator class."
    def test(self, x):
        """Is this child allowed in a drawing or group?
        I.e. does it descend from Shape or UserNode?
        """

        from reportlab.graphics.shapes import UserNode, Shape
        return isinstance(x, UserNode) or isinstance(x, Shape)

class _isValidChildOrNone(_isValidChild):
    def test(self,x):
        return _isValidChild.test(self,x) or x is None

class _isCallable(Validator):
    def test(self, x):
        return callable(x)

class OneOf(Validator):
    """Make validator functions for list of choices.

    Usage:
    f = reportlab.lib.validators.OneOf('happy','sad')
    or
    f = reportlab.lib.validators.OneOf(('happy','sad'))
    f('sad'),f('happy'), f('grumpy')
    (1,1,0)
    """
    def __init__(self, enum,*args):
        if type(enum) in [ListType,TupleType]:
            if args!=():
                raise ValueError, "Either all singleton args or a single sequence argument"
            self._enum = tuple(enum)+args
        else:
            self._enum = (enum,)+args

    def test(self, x):
        return x in self._enum

class SequenceOf(Validator):
    def __init__(self,elemTest,name=None,emptyOK=1, NoneOK=0, lo=0,hi=0x7fffffff):
        self._elemTest = elemTest
        self._emptyOK = emptyOK
        self._NoneOK = NoneOK
        self._lo, self._hi = lo, hi
        if name: self._str = name

    def test(self, x):
        if type(x) not in _SequenceTypes:
            if x is None: return self._NoneOK
            return False
        if x==[] or x==():
            return self._emptyOK
        elif not self._lo<=len(x)<=self._hi: return False
        for e in x:
            if not self._elemTest(e): return False
        return True

class EitherOr(Validator):
    def __init__(self,tests,name=None):
        if type(tests) not in _SequenceTypes: tests = (tests,)
        self._tests = tests
        if name: self._str = name

    def test(self, x):
        for t in self._tests:
            if t(x): return True
        return False

class NoneOr(Validator):
    def __init__(self,elemTest,name=None):
        self._elemTest = elemTest
        if name: self._str = name

    def test(self, x):
        if x is None: return True
        return self._elemTest(x)

class isInstanceOf(Validator):
    def __init__(self,klass=None):
        self._klass = klass
    def test(self,x):
        return isinstance(x,self._klass)

isBoolean = _isBoolean()
isString = _isString()
isNumber = _isNumber()
isInt = _isInt()
isNoneOrInt = NoneOr(isInt,'isNoneOrInt')
isNumberOrNone = _isNumberOrNone()
isTextAnchor = OneOf('start','middle','end','boxauto')
isListOfNumbers = SequenceOf(isNumber,'isListOfNumbers')
isListOfNumbersOrNone = _isListOfNumbersOrNone()
isListOfShapes = _isListOfShapes()
isListOfStrings = SequenceOf(isString,'isListOfStrings')
isListOfStringsOrNone = _isListOfStringsOrNone()
isTransform = _isTransform()
isColor = _isColor()
isListOfColors = SequenceOf(isColor,'isListOfColors')
isColorOrNone = _isColorOrNone()
isShape = isValidChild = _isValidChild()
isNoneOrShape = isValidChildOrNone = _isValidChildOrNone()
isAnything = _isAnything()
isNothing = _isNothing()
isXYCoord = SequenceOf(isNumber,lo=2,hi=2,emptyOK=0)
isBoxAnchor = OneOf('nw','n','ne','w','c','e','sw','s','se', 'autox', 'autoy')
isNoneOrString = NoneOr(isString,'NoneOrString')
isNoneOrListOfNoneOrStrings=SequenceOf(isNoneOrString,'isNoneOrListOfNoneOrStrings',NoneOK=1)
isListOfNoneOrString=SequenceOf(isNoneOrString,'isListOfNoneOrString',NoneOK=0)
isNoneOrListOfNoneOrNumbers=SequenceOf(isNumberOrNone,'isNoneOrListOfNoneOrNumbers',NoneOK=1)
isCallable = _isCallable()
isStringOrCallable=EitherOr((isString,isCallable),'isStringOrCallable')
isStringOrCallableOrNone=NoneOr(isStringOrCallable,'isStringOrCallableNone')
isStringOrNone=NoneOr(isString,'isStringOrNone')
