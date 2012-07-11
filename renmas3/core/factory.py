
from tdasm import Tdasm
from renmas3.macros import mov, arithmetic32, arithmetic128,\
                            broadcast, macro_if, dot_product, normalization, cross_product

class Factory:
    def __init__(self):
        pass

    def create_assembler(self):
        assembler = Tdasm()
        assembler.register_macro('mov', mov)
        assembler.register_macro('eq128', arithmetic128)
        assembler.register_macro('eq32', arithmetic32)
        assembler.register_macro('broadcast', broadcast)
        assembler.register_macro('if', macro_if)
        assembler.register_macro('dot', dot_product)
        assembler.register_macro('normalization', normalization)
        assembler.register_macro('cross', cross_product)
        return assembler

