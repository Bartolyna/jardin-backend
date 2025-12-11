#!/usr/bin/env python
# Script para agregar modelos adicionales a models.py

with open('/tmp/models_adicionales.py', 'r', encoding='utf-8') as f:
    content = f.read()

with open('/app/api/models.py', 'a', encoding='utf-8') as f:
    f.write('\n\n')
    f.write(content)

print("Modelos adicionales agregados exitosamente!")
