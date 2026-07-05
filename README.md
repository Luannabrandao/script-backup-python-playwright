# Documentação Técnica: Automação para Extração Sequencial de Relatórios (RPA)

Este documento descreve a arquitetura, a lógica de otimização e as decisões de implementação do robô de Automação de Processos de Negócios (RPA) desenvolvido em **Python** com o framework **Playwright**.

---

## 🎯 Objetivo do Projeto

O script foi projetado para automatizar a extração massiva de relatórios gerenciais estruturados a partir de uma plataforma web corporativa. A solução realiza de forma autônoma o cruzamento de três dimensões principais de dados:
1. **Módulos de Relatórios:** Múltiplas abas de análise contidas no menu lateral.
2. **Escopo Temporal:** Histórico anual completo (2023 a 2026).
3. **Unidades de Negócio:** Listagem sequencial de filiais/lojas cadastradas no sistema.

Ao final do ciclo de execução, os dados são validados e salvos localmente em arquivos `.csv` organizados de forma hierárquica.

---

## 🧠 Arquitetura e Lógica de Otimização

### 1. Inversão de Loops para Ganho de Performance
A principal otimização do algoritmo reside na ordem de execução dos loops (*for*). Em interfaces de sistemas ERP tradicionais, a alteração de filtros de calendário costuma disparar recarregamentos pesados de scripts internos. 

Para mitigar a latência, o robô aplica a seguinte hierarquia:
* **Loop Principal:** Seleciona o módulo do relatório no menu lateral.
* **Loop Secundário:** Fixa o ano de vigência no calendário (executado poucas vezes).
* **Loop Interno:** Percorre a listagem de lojas consecutivamente.

**Resultado:** O calendário é preenchido apenas uma vez por ano selecionado, permitindo que a maratona de lojas seja processada em lote sem a necessidade de reconfigurar as datas a cada clique, reduzindo o tempo total de processamento da rotina.

### 2. Gerenciamento de Estado Dinâmico (React Select)
Componentes modernos de front-end com comportamento assíncrono frequentemente ocultam elementos de entrada de texto nativos por motivos estéticos. O script lida com essa complexidade ao mapear o input real de digitação através de seletores posicionais (`nth`), aplicando comandos de teclado em nível de sistema (`Control+A` + `Backspace`) para garantir a limpeza prévia do buffer de memória do elemento antes de preencher a nova unidade.

### 3. Prevenção de Falsos Positives e Validação do DOM
Para evitar o download desnecessário de datasets nulos, o fluxo valida o estado da tabela após a submissão do filtro:
* O robô inspeciona o DOM em busca de strings indicativas de ausência de dados (ex: *"Nenhum resultado encontrado"*).
* Caso o elemento esteja visível, a rotina de download é abortada para aquela unidade específica e o ponteiro salta para o próximo alvo, mantendo o repositório local limpo.

---

## 📁 Modelo de Persistência e Estrutura de Saída

Os arquivos baixados via interceptação assíncrona de eventos de download do navegador (`expect_download`) são salvos seguindo uma árvore de diretórios criada dinamicamente conforme os parâmetros de busca:

```text
arquivos_extraidos/
├── Por_dia/
│   ├── 2023/
│   │   ├── Unidade_A_Teste_2023.csv
│   │   └── Unidade_B_Teste_2023.csv
│   └── 2024/
└── Por_Pagamentos/
    └── 2023/ 
