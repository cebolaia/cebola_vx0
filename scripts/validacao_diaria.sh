#!/bin/bash

# Validação de hashes
find /cebola_vx0 -type f -exec sha256sum {} \; | grep -v "resumo-setup.md" > /tmp/hashes_atual.txt
diff --strip-trailing-cr /cebola_vx0/resumo/resumo-setup.md /tmp/hashes_atual.txt || exit 1

# Validação cross-model
MODELS=("phi3:3.8b-mini-128k-instruct-q4_0" "tinyllama:1.1b")
THRESHOLD=0.85

for model in "${MODELS[@]}"; do
    concordancia=$(cebola validate --model $model --quiet)
    if (( $(echo "$concordancia < $THRESHOLD" | bc -l) )); then
        echo "Falha na validação: $model - $concordancia" >&2
        exit 2
    fi
done

# Atualização do resumo
echo "Validação $(date '+%Y-%m-%d %H:%M:%S') - SUCESSO" >> /cebola_vx0/resumo/resumo-setup.md