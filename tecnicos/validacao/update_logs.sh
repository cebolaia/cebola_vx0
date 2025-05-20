#!/bin/bash
ARQUIVO=$1
HASH=$(sha256sum $ARQUIVO | cut -d' ' -f1)
echo "$(date '+%Y-%m-%d %H:%M:%S') | $ARQUIVO | Hash: $HASH" >> cebola_vx0/resumo/resumo-setup.md
