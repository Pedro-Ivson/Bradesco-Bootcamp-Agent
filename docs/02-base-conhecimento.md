# 2. Base de conhecimento

## Fontes utilizadas

| Arquivo | Conteúdo principal | Uso no agente |
|---|---|---|
| `01_Fundamentos_de_Nutricao_e_Alimentacao_Saudavel.pdf` | Princípios de alimentação saudável, grupos de alimentos, processamento e segurança alimentar | Explicar equilíbrio, diversidade, moderação e escolhas cotidianas |
| `02_Macronutrientes_Fibras_Agua_e_Metabolismo.pdf` | Carboidratos, proteínas, gorduras, fibras, água e metabolismo | Responder dúvidas sobre funções dos macronutrientes e hidratação |
| `03_Micronutrientes_Deficiencias_e_Suplementacao.pdf` | Vitaminas, minerais, biodisponibilidade, deficiências e suplementos | Explicar conceitos sem prescrever suplemento ou dose |
| `04_Avaliacao_Nutricional_e_Planejamento_Alimentar.pdf` | Avaliação nutricional, rótulos, porções, padrões alimentares e comportamento | Apoiar explicações gerais sobre pratos, rótulos e objetivos alimentares |
| `05_Nutricao_Ciclo_de_Vida_Esportiva_e_Clinica.pdf` | Ciclo de vida, exercício, condições comuns e quando encaminhar | Reforçar cuidados com grupos vulneráveis e limites clínicos |

Os PDFs estão em `C:\caminho\dos\pdfs`. O projeto não depende de enviar esses arquivos a um serviço externo.

## Pipeline de ingestão

1. `src/prepare_knowledge.py` localiza os PDFs.
2. `pypdf` extrai o texto página a página.
3. Cabeçalhos repetidos são removidos e espaços são normalizados.
4. Cada página é dividida em trechos de aproximadamente 2.200 caracteres.
5. O resultado é salvo em `data/knowledge.json` com `source`, `page`, `section` e `text`.

O arquivo derivado preserva o nome do PDF e a página para permitir rastreabilidade na interface.

## Recuperação no momento da pergunta

O agente normaliza acentos, remove palavras muito frequentes e compara os termos da pergunta com o título e o texto de cada trecho. Os quatro trechos com maior sobreposição são inseridos no contexto do modelo. Quando não existe correspondência, o agente recebe apenas um pequeno contexto inicial e deve declarar a limitação, em vez de inventar.

Essa estratégia é suficiente para um protótipo transparente e sem infraestrutura externa. Uma evolução possível seria usar embeddings locais e um banco vetorial, mas isso não é necessário para demonstrar os seis passos do Lab.

## Exemplo de contexto

Para uma pergunta como `Qual é a função das fibras?`, o prompt pode receber trechos relacionados ao papel das fibras, da microbiota, da saciedade e das fontes alimentares. A interface mostra as páginas recuperadas, enquanto a resposta separa o que está documentado de qualquer sugestão geral. Assim, a aplicação não depende de uma citação de página escrita pelo modelo.

Para uma pergunta sobre `IMC`, o contexto deve lembrar que o índice é útil para rastreamento em adultos, mas não distingue músculo de gordura e não é um diagnóstico isolado. Esse tipo de ressalva é essencial para manter a resposta educativa e segura.

## Privacidade e manutenção

- O JSON é um artefato derivado e pode ser recriado a qualquer momento.
- PDFs novos entram na base executando novamente o script de preparo.
- `data/*.pdf` está no `.gitignore` para evitar versionar arquivos brutos por engano.
- Antes de publicar o projeto, revise se a base não contém dados pessoais ou clínicos identificáveis.
