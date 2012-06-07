
from tdasm import Runtime
import renmas2
import renmas2.osl

lex = renmas2.osl.OSLLexer()

text = """
shader gamma (float x, output float k, output vector p, vector t)
{
    float pa; 
    k = x;
    p = t;

}
"""
tokens = lex.tokenize(text)

parser = renmas2.osl.OSLParser()

shader = parser.parse(tokens)
print(shader)

ren = renmas2.Renderer()
runtime = Runtime()
shader.prepare("test", [runtime], ren.assembler)

print(shader.props.k)

shader.props.x = 44
shader.props.t = (4,5,6)
shader.execute()
print(shader.props.k)
print(shader.props.p)
#shader.param.k = vector
#shader.param.k = (4,5,6)

