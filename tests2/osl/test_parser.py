
import renmas2
import renmas2.osl

lex = renmas2.osl.OSLLexer()

text = """
    shader shader_name ()
    {
    }

"""
tokens = lex.tokenize(text)

parser = renmas2.osl.OSLParser()

parser.parse(tokens)

