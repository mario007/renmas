from .shader import Shader

class OSLParser:
    def __init__(self):
        self._data_types = ['int', 'float', 'point', 'vector', 'normal', 'color', 'matrix', 'string', 'void']

    def parse(self, tokens):

        shader_type = self._shader_type(tokens)
        print("Shader type", shader_type)
        metadata = self._metadata(tokens)
        shader_name = self._shader_name(tokens)
        print("Shader name", shader_name)
        parameters = self._parameters(tokens)
        print("Shader parameters", parameters)

        # TODO metadata
        
    def _shader_type(self, tokens):
        while True:
            token = next(tokens)
            tk_typ, tk_value, line = token
            if tk_typ == "new_line" or tk_typ == "space":
                continue
            elif tk_typ == "iden":
                if tk_value in ('surface', 'displacement', 'light', 'volume', 'shader'):
                    return tk_value
                else:
                    raise ValueError("Wrong shader type!", token)
            else:
                raise ValueError("Cannot determied shader type!", token)

    def _metadata(self, tokens):
        pass

    def _shader_name(self, tokens):
        while True:
            token = next(tokens)
            tk_typ, tk_value, line = token
            if tk_typ == "iden":
                return tk_value
            elif tk_typ == "new_line" or tk_typ == "space":
                continue
            else:
                raise ValueError("Shader name error! Wrong token!", token)

    def _parameters(self, tokens):
        params = []
        inside = False
        while True:
            token = next(tokens)
            tk_typ, tk_value, line = token
            if tk_typ == "special":
                if tk_value == '(':
                    if inside == True:
                        raise ValueError("Allready inside!", token)
                    inside = True
                elif tk_value == ')':
                    if inside == False:
                        raise ValueError("Missing parenthesis!", token)
                    return params
                else:
                    raise ValueError("Syntax error in parameters! Wrong token!", token)
            elif tk_typ == "osl_keyword":
                if tk_value in self._data_types:
                    params.append(self._param(tokens))
                else:
                    raise ValueError("Wrong data type in parameter", token)
            elif tk_typ == "space" or tk_typ == "new_line":
                continue
            else:
                raise ValueError("Could not parse parameters!", token)

    def _param(self, tokens):
        pass

