import re
from hashlib import sha256

def sanitizar(texto):
    # Camada 1: Regex (OWASP AI-04 básico)
    texto = re.sub(r'!override|sudo|rm -rf', '[BLOQUEADO]', texto)
    
    # Camada 2: Validação estrutural
    if len(texto.split()) < 3:
        raise ValueError("Texto muito curto para análise")
    
    # Camada 3: Hash de integridade
    return sha256(texto.encode()).hexdigest()

if __name__ == "__main__":
    import sys
    print(sanitizar(sys.argv[1]))
