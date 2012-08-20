from tdasm import Tdasm

from .mov import mov
from .lea import lea
from .arithmetic import arithmetic32, arithmetic128
from .broadcast import broadcast
from .macro_if import macro_if
from .macro_dotproduct import dot_product
from .normalization import normalization
from .cross_product import cross_product

def create_assembler():
    assembler = Tdasm()
    assembler.register_macro('mov', mov)
    assembler.register_macro('lea', lea)
    assembler.register_macro('eq128', arithmetic128)
    assembler.register_macro('eq32', arithmetic32)
    assembler.register_macro('broadcast', broadcast)
    assembler.register_macro('if', macro_if)
    assembler.register_macro('dot', dot_product)
    assembler.register_macro('normalization', normalization)
    assembler.register_macro('cross', cross_product)
    return assembler

