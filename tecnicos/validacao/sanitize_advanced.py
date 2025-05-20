import re
from hashlib import sha256

class SanitizadorAvancado:
    @staticmethod
    def camada1(texto):
        return re.sub(r'!override|sudo|rm -rf', '[BLOQUEADO]', texto)
    
    @staticmethod
    def camada2(texto):
        if len(texto) < 50:
            raise ValueError("Texto muito curto para análise")
        return texto
    
    @staticmethod
    def camada3(texto):
        return sha256(texto.encode()).hexdigest()
    
    @classmethod
    def sanitizar(cls, texto):
        etapa1 = cls.camada1(texto)
        etapa2 = cls.camada2(etapa1)
        return cls.camada3(etapa2)
