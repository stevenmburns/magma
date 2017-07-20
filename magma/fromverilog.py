from __future__ import absolute_import
from __future__ import print_function
from collections import namedtuple

from mako.template import Template
from pyverilog.vparser.parser import VerilogParser, Node, Input, Output, ModuleDef
from pyverilog.dataflow.visit import NodeVisitor

from .t import In, Out
from .bit import Bit
from .array import Array
from .circuit import DeclareCircuit, DefineCircuit

__all__  = ['DeclareFromVerilog']
__all__ += ['DeclareFromVerilogFile']
__all__ += ['DeclareFromTemplatedVerilog']
__all__ += ['DeclareFromTemplatedVerilogFile']
__all__ += ['DefineFromVerilog']
__all__ += ['DefineFromVerilogFile']
__all__ += ['DefineFromTemplatedVerilog']
__all__ += ['DefineFromTemplatedVerilogFile']


class ModuleVisitor(NodeVisitor):
    def __init__(self):
        self.nodes = []

    def visit_ModuleDef(self, node):
        self.nodes.append(node)
        return node

def ParseVerilogModule(node):
    args = []
    for port in node.portlist.ports:
        io = port.first
        args.append(io.name)
        msb = int(io.width.msb.value)
        lsb = int(io.width.lsb.value)
        if   isinstance(io, Input):  dir = 'In'
        elif isinstance(io, Output): dir = 'Out'
        else: continue
        if msb == 0 and lsb == 0:
            t = Bit
        else:
            t = Array(msb-lsb+1, Bit)
        args.append( In(t) if dir == 'In' else Out(t) )

    return node.name, args

def FromVerilog(source, func):
    parser = VerilogParser()

    ast = parser.parse(source)
    #ast.show()

    v = ModuleVisitor()
    v.visit(ast)

    modules = []
    for node in v.nodes:
         name, args = ParseVerilogModule(node)
         modules.append(func(name, *args))
    return modules

def FromVerilogFile(file, func):
    if file is None:
        return None
    verilog = open(file).read()
    return FromVerilog(verilog, func)

def FromTemplatedVerilog(templatedverilog, func, **kwargs):
    verilog = Template(templatedverilog).render(**kwargs)
    return FromVerilog(verilog, func)

def FromTemplatedVerilogFile(file, func, **kwargs):
    if file is None:
        return None
    templatedverilog = open(file).read()
    return FromTemplatedVerilog(templatedverilog, func)


def DeclareFromVerilog(source):
    return FromVerilog(source, DeclareCircuit)

def DeclareFromVerilogFile(file):
    return FromVerilogFile(file, DeclareCircuit)

def DeclareFromTemplatedVerilog(source, **kwargs):
    return FromTemplatedVerilog(source, DeclareCircuit, **kwargs)

def DeclareFromTemplatedVerilogFile(file, **kwargs):
    return FromTemplatedVerilogFile(file, DeclareCircuit, **kwargs)


def DefineFromVerilog(source):
    return FromVerilog(source, DefineCircuit)

def DefineFromVerilogFile(file):
    return FromVerilogFile(source, DefineCircuit)

def DefineFromTemplatedVerilog(source, **kwargs):
    return FromTemplatedVerilog(source, DefineCircuit, **kwargs)

def DefineFromTemplatedVerilogFile(file, **kwargs):
    return FromTemplatedVerilogFile(file, DefineCircuit, **kwargs)
