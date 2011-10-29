
from tdasm import Tdasm, Runtime
from .call import MacroCall
from .arithmetic import arithmetic32, arithmetic128
from .broadcast import broadcast
from .macro_if import macro_if
from .macro_dotproduct import dot_product
from .normalization import normalization

assembler = Tdasm()
macro_call = MacroCall()
assembler.register_macro('call', macro_call.macro_call)
assembler.register_macro('eq128', arithmetic128)
assembler.register_macro('eq32', arithmetic32)
assembler.register_macro('broadcast', broadcast)
assembler.register_macro('if', macro_if)
assembler.register_macro('dot', dot_product)
assembler.register_macro('normalization', normalization)


