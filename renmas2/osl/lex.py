
import re
import timeit
import string

# TODO - nested comments
class OSLLexer: 
    def __init__(self):
        osl_keywords = ['break', 'closure', 'color', 'continue', 'do', 'else', 'emit', 'float', 'for', 'if',
                'illuminance', 'illuminate', 'int', 'matrix', 'normal', 'output', 'point', 'public', 'return',
                'string', 'struct', 'vector', 'void', 'while'] 

        reserved_words = ['bool', 'caes', 'catch', 'char', 'class', 'const', 'delete', 'default', 'double',
                'enum', 'extern', 'false', 'friend', 'goto', 'inline', 'long', 'new', 'operator', 'private',
                'protected', 'short', 'signed', 'sizeof', 'static', 'switch', 'template', 'this', 'throw',
                'true', 'try', 'typedef', 'uniform', 'union', 'unsigned', 'varying', 'virtual', 'volatile']


        self.definitions = [
        ('multi_comment', r'/\*(.|\r\n|\n)*?\*/'),
        ('new_line', r'\r\n|\n'),
        ('string', r'"[\s\w]*"'),
        ('operators', r'\+|-|~|\^|=|<|>|!|&|%'),
        ('comment', r'//.*$'),
        ('special', r'\[|]|{|}|\(|\)|;'),
        ('comma', r','),
        ('keyword', r'\b(%s)\b' % '|'.join(osl_keywords)),
        ('reserved_word', r'\b(%s)\b' % '|'.join(reserved_words)),
        ('decimal', r'[0-9]+\.[0-9]*'),
        ('hex_num', r'0x[0-9A-Fa-f]+'),
        ('bin_num', r'[01]+[bB]'),
        ('number', r'[0-9]+'),
        ('iden', r'[_A-Za-z][_A-Za-z0-9]*'),
        ('space', r'( |\t)+'),
       ]

        parts = []
        for name, part in self.definitions:
            parts.append('(?P<%s>%s)' %(name, part))
        self.regexpString = "|".join(parts)
        self.regexp = re.compile(self.regexpString, re.MULTILINE)

    def tokenize(self, text):
        len_text = len(text)
        line_number = 0
        position = 0
        while True:
            match = self.regexp.match(text, position)
            if match is not None:
                position = match.end()
                for name, rexp in self.definitions:
                    m = match.group(name)
                    if m is not None:
                        if name == 'hex_num':
                            name = "number"
                            m = str(int(m, 16))
                        elif name == 'bin_num':
                            name = "number"
                            m = str(int(m[:len(m)-1], 2))
                        elif name == 'string':
                            m = str(m[1:len(m)-1])
                        if m == '\n' or m =="\r\n":
                            line_number += 1
                        yield (name, m, line_number)
            else:
                if position != len_text:
                    raise ValueError("Unexpected token ", line_number, position, text[position])
                break
                    
