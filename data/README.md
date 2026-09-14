# Base de conhecimento

`knowledge.json` é gerado pelo script `src/prepare_knowledge.py` a partir dos PDFs fornecidos para a atividade.

Fonte utilizada nesta execução:

```text
C:\caminho\dos\pdfs
```

Para atualizar a base depois de adicionar ou substituir PDFs:

```bash
python src/prepare_knowledge.py --source-dir "C:\caminho\dos\pdfs"
```

O JSON contém metadados dos documentos e trechos com nome do arquivo e número da página, permitindo que o agente mostre a origem do contexto usado. Os PDFs originais não são versionados nesta pasta.

