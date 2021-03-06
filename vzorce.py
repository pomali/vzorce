# -*- coding: utf-8 -*-
# Author: Stanislav Parnicky
# Created: 10-11-2014
import operator
import itertools 
import math

class T:
    pass


class N:
    pass


class K(object):
    def __repr__(self):
        return str(self)
    def __add__(self, other):
        return OpAdd( (self, other) )
    def __mul__(self, other):
        return OpMul( (self, other) )
    def __lt__(self, other):
        return OpLt( (self, other) ) 
    def __gt__(self, other):
        return OpGt( (self, other) ) 
    def __and__(self, other):
        return OpDot( (self, other) )
    def __sub__(self, other):
        return OpSub( (self, other) )
    def __abs__(self):
        return OpAbs( self )
    def __pow__(self, other):
        return OpPow( self )
    def tex(self, prepend=None):
        if prepend:
            return ("\\begin{polynomial}\n"
                    "%s%s\n"
                    "\\end{polynomial}\n") % (prepend, str(self))
        else:
            return ("\\begin{polynomial}\n"
                    "%s\n"
                    "\\end{polynomial}\n") % (str(self))


class Operation(K):
    final_N = None
    def __str__(self):
        def arg_par(x):
            if isinstance(x,Operation):
                return "(%s)" % str(x)
            return str(x)
        return  self.S.join(map(arg_par,self.args))

    def __init__(self, args):
        self.args = args

    def calculate(self):
        """Vykona vsetky operacie ktore maju ako argumenty iba listy (a nahradi ich listami s vysledkom)
        """
        if all( map( lambda x: isinstance(x, N),self.args) ):
            return self.evaluate()
        else:
            return self.__class__( map(operator.methodcaller('calculate'), self.args))
            #return self.__class__( (self.args[0].calculate(), self.args[1].calculate()) )

    def duri(self, prepend = None):
        """Vrati TeX source vypoctu stromu operacii
        """
        buf = []
        X = self
        while True:
            buf.append(X.tex(prepend))
            X = X.calculate()
            if not isinstance(X, Operation):
                break
        self.final_N = X.value
        buf.append(X.tex(prepend))
        out_str = "\n".join(buf)
        return out_str


class SingleArgOperation(Operation):
    pass


class CmpOperation(Operation):
    def __str__(self):
        return  self.S.join(map(str,self.args))


class AssociativeOperation(Operation):
    def __str__(self):
        def arg_par(x):
            """Vsetky rovnake operacie neozatvorkuje inak ozatvorkuje
            """
            if (isinstance(x,Operation) 
                and not isinstance(x, self.__class__) 
                and not isinstance(x,SingleArgOperation)):
                return "(%s)" % str(x)
            return str(x)
        return  self.S.join(map(arg_par,self.args))


class OpMul(AssociativeOperation):
    S = " * "
    def calculate(self):
        x = self.args[0]
        y = self.args[1]
        if x.evaluate() == 0 or y.evaluate() == 0 :
            return N(0)
        return super(OpMul, self).calculate()

    def evaluate(self):
        x = self.args[0]
        y = self.args[1]
        if x.is_scalar:
            if y.is_scalar:
                return N( x.evaluate() * y.evaluate())
            else:
                return N( map( lambda i: i*x.evaluate(), y.evaluate()))
        else:
            return N( map( lambda i: i*y.evaluate(), x.evaluate()))


class OpAdd(AssociativeOperation):
    S = " + "
    def evaluate(self):
        return N( self.args[0].evaluate() + self.args[1].evaluate())


class OpSub(Operation):
    S = " - "
    def evaluate(self):
        x = self.args[0]
        y = self.args[1]
        if x.is_scalar:
            if y.is_scalar:
                return N( x.value - y.value)
            return N( list(map( lambda i: x.value-i, y.value)))
        else:
            if y.is_scalar:
                return N( list(map( lambda i: i-y.value, x.value)))
            else:
                return N( list(itertools.starmap(operator.sub, zip(x.value, y.value) ) ) )


class OpLt(CmpOperation):
    S = " < "
    def evaluate(self):
        return N(self.args[0].value < self.args[1].value)


class OpGt(CmpOperation):
    S = " > "
    def evaluate(self):
        return N(self.args[0].value > self.args[1].value)


class OpDot(Operation):
    S = " \\cdot "
    def evaluate(self):
        x = self.args[0].evaluate()
        y = self.args[1].evaluate()
        return (N(x[0]) * N(y[0])) + (N(x[1]) * N(y[1])) + (N(x[2]) * N(y[2]))


class OpPow(Operation):
    S = "^"
    def evaluate(self):
        x = self.args[0].evaluate()
        y = self.args[1].evaluate()
        return N(x)**N(y)


class OpAbs(SingleArgOperation):
    def __str__(self):
        return "|%s|" % str(self.args)

    def evaluate(self):
       return N(abs(self.args.value)) 

    def calculate(self):
       if isinstance(self.args, N):
           return self.evaluate()
       else:
           return OpAbs(self.args.calculate())


class N(K): #number/value
    """Class zachytavajuci konkretne cislo, hodnotu, maticu a podobne
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if isinstance(self.value, bool):
            return "\\text{Platí}" if  self.value else "\\text{Neplatí}"
        if (isinstance(self.value, int) or isinstance(self.value, float)) and self.value<0:
            return "(%s)" % str(self.value)
        return str(self.value)

    def calculate(self):
        return N(self.value)

    def evaluate(self):
        return self.value

    def __getitem__(self, key):
        return N(self.value[key])

    @property
    def is_scalar(self):
        return not isinstance(self.value, list)


class T(K): #Term
    """Class zachytavajuci hodnotu s menom, 
        ktora sa da pouzit pri vypoctoch a po vypisani vzorcu bude dosadena
    """
    def __init__(self, value, name=None):
        self.value = value
        self.name = name

    def __str__(self):
        if self.name:
            return self.name
        return str(self.value)

    def calculate(self):
        return N(self.value) 

    def evaluate(self):
        return self.value

    def __getitem__(self, key):
        keyname = ['x','y','z'][key]
        return T(self.value[key], "{%s}_{%s}" % (self.name,keyname))

    @property
    def is_scalar(self):
        return not isinstance(self.value, list)

    def eq_tex(self):
        return ("\\begin{polynomial}\n"
                "%s = %s\n"
                "\\end{polynomial}\n") % (self.name, str(self.value))





