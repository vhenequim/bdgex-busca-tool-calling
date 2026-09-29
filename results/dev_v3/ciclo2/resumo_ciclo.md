# Ciclo 2 — desenvolvimento da v3 (160 consultas do lote 1)

| Configuração | n | Acurácia | Domínio | Falsa recusa | Recusa F | F1 | Chamadas/consulta | Com pergunta | Chamada em texto | Latência mediana (s) | FP mais comuns | FN mais comuns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tc1 (T4) | 160 | 58.1% | 50.4% | 31.9% | 100.0% | 0.762 | 1.00 | 0 | 0 | 0.8 | {'keyword': 6, 'publicationPeriod': 6, 'productType': 5, 'sortField': 2, 'city': 1, 'creationPeriod': 1} | {'productType': 13, 'scale': 13, 'city': 11, 'publicationPeriod': 11, 'state': 8, 'supplyArea': 7} |
| se1 (T4) | 160 | 69.4% | 75.6% | 0.0% | 0.0% | 0.908 | 1.00 | 0 | 0 | 0.8 | {'keyword': 16, 'publicationPeriod': 9, 'productType': 2, 'limit': 2, 'state': 2, 'creationPeriod': 1} | {'city': 6, 'creationPeriod': 4, 'state': 2, 'sortField': 2, 'sortDirection': 2, 'scale': 1} |
| tc2 (T4) | 160 | 58.1% | 51.9% | 2.2% | 100.0% | 0.841 | 1.00 | 0 | 0 | 0.9 | {'keyword': 20, 'productType': 20, 'state': 14, 'limit': 12, 'publicationPeriod': 3, 'creationPeriod': 3} | {'productType': 4, 'city': 3, 'scale': 3, 'state': 2, 'publicationPeriod': 2, 'creationPeriod': 1} |
| se2 (T4) | 160 | 72.5% | 67.4% | 14.1% | 100.0% | 0.883 | 1.00 | 0 | 0 | 0.7 | {'keyword': 11, 'state': 6, 'publicationPeriod': 4, 'limit': 2, 'productType': 1, 'creationPeriod': 1} | {'city': 11, 'productType': 7, 'scale': 6, 'state': 5, 'creationPeriod': 2, 'project': 1} |
| hib: tc2 decide, se1 extrai (T4) | 160 | 78.1% | 74.8% | 2.2% | 100.0% | 0.911 | 1.00 | 0 | 0 | 1.5 | {'keyword': 11, 'publicationPeriod': 8, 'productType': 2, 'limit': 2, 'state': 2, 'creationPeriod': 1} | {'city': 6, 'creationPeriod': 4, 'state': 2, 'publicationPeriod': 2, 'sortField': 2, 'sortDirection': 2} |
| tool_calling_v3f | 160 | 96.9% | 96.3% | 0.7% | 100.0% | 0.990 | 2.11 | 18 | 24 | 6.4 | {'limit': 1, 'scale': 1, 'city': 1} | {'creationPeriod': 1, 'productType': 1, 'scale': 1} |
| tool_calling_v3 | 160 | 96.9% | 97.0% | 0.0% | 100.0% | 0.992 | 2.19 | 11 | 23 | 7.6 | {'city': 2, 'keyword': 1, 'publicationPeriod': 1, 'limit': 1} | {} |
| saida_estruturada_v3 | 160 | 93.1% | 91.9% | 2.2% | 100.0% | 0.979 | 1.00 | 0 | 0 | 5.1 | {'keyword': 4, 'city': 2, 'publicationPeriod': 2} | {'productType': 2, 'keyword': 1, 'creationPeriod': 1} |
| hib: tc3 decide, se3 extrai | 160 | 93.1% | 91.9% | 2.2% | 100.0% | 0.979 | 1.00 | 0 | 0 | 13.1 | {'keyword': 4, 'city': 2, 'publicationPeriod': 2} | {'productType': 2, 'keyword': 1, 'creationPeriod': 1} |
