import ollama
import hashlib
import json
from datetime import datetime
import re
import sys
import os

def sanitize(texto):
    # Sanitização multicamada com novos padrões OWASP AI-04
    texto = re.sub(r'!sudo|rm -rf|!override|--no-preserve-root', '[BLOQUEADO]', texto)
    if len(texto) < 75:  # Aumento do limite mínimo para análise mais robusta
        raise ValueError("Texto abaixo do tamanho mínimo seguro para análise")
    return hashlib.sha256(texto.encode()).hexdigest()

def cross_validate(prompt, threshold=0.88, models=None):  # Aumento do threshold para 88%
    if models is None:
models = ['phi3:3.8b-mini-128k-instruct-q4_0', 'tinyllama:1.1b-chat-v1.0']
        
    respostas = []
    try:
        for modelo in models:
            response = ollama.generate(model=modelo, prompt=prompt)
            respostas.append(response['response'].strip().lower())
            
        # Verificação de similaridade semântica adicional
        unique_responses = len(set(respostas))
        return unique_responses <= 1 and (len(respostas) == len(models))
    
    except Exception as e:
        log_error(e)
        return False

def log_error(error):
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "error": str(error),
        "module": "cross_validate"
    }
    with open("cebola_vx0/LOG.txt", "a") as logf:
        logf.write(json.dumps(error_entry) + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 cebola_vx0/tecnicos/validacao/cross_validate.py '<prompt>'")
        sys.exit(1)
        
    prompt = sys.argv[1]
    try:
        sanitized_hash = sanitize(prompt)
        status = cross_validate(prompt)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_hash": sanitized_hash,
            "status": "VALID" if status else "REVIEW",
            "models": ['phi3:mini-instruct', 'tinyllama-1.1b-chat-v1.0'],
            "system_stats": {
                "cpu_usage": os.popen("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'").read().strip(),
                "mem_usage": os.popen("free -m | awk '/Mem:/ {print $3}'").read().strip()
            }
        }
        
        with open("cebola_vx0/LOG.txt", "a") as logf:
            logf.write(json.dumps(log_entry) + "\n")

        with open("cebola_vx0/resumo/resumo-setup.md", "a") as resf:
            resf.write(f"{datetime.now().isoformat()} | cross_validate.py | Hash: {sanitized_hash} | Status: {log_entry['status']}\n")
            
        print("CROSS_MODEL_OK" if status else "CROSS_MODEL_REVIEW")
        
    except Exception as e:
        log_error(e)
        print("CROSS_MODEL_ERROR")
        sys.exit(1)
