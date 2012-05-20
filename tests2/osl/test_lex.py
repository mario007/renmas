
import renmas2
import renmas2.osl

lex = renmas2.osl.OSLLexer()

text = """
/* komnetar  
    dupli komentar */
    1
     /* kome */
    float n
    // do kraj trenutne linije
    "text" 
    1+2-3~2.3^4=<>!%&[]{}()
    try
    while
"""
gen = lex.tokenize(text)
while True:
    try:
        t = next(gen)
        print(t)
    except:
        break

