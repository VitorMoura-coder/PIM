# 💻 PIM II: Sistema Acadêmico Colaborativo com Apoio de IA

## Visão Geral do Projeto

Este repositório contém o Projeto Integrado Multidisciplinar (PIM II) do Curso Superior de Tecnologia em **Análise e Desenvolvimento de Sistemas (ADS)**. O foco é a construção de um **Sistema Acadêmico Colaborativo** para gerenciamento de alunos, turmas e atividades, incorporando recursos de **Inteligência Artificial** para análise preditiva de desempenho.

O sistema foi concebido para ser uma solução automatizada, aderente à metodologia **Scrum** e modelado com **UML**.

## ⚙️ Arquitetura e Tecnologia

O sistema adota uma arquitetura modular, separando a lógica de baixo nível do front-end e da lógica de negócio.

### Linguagens e Ferramentas

| Categoria | Tecnologia | Aplicação no Projeto |
| :--- | :--- | :--- |
| **Linguagem Principal** | Python 3.x | Lógica de negócio, Interface Gráfica (Tkinter) e Módulo de IA. |
| **Módulo Core** | C | Utilizado para módulos críticos de baixo nível e otimização de performance (ex: gestão inicial de usuários). |
| **Persistência** | CSV (Comma Separated Values) | Armazenamento leve e portátil para dados de usuários, turmas e atividades. |
| **Metodologia** | Scrum / UML | Utilizada para gestão do projeto e modelagem de arquitetura (Diagramas de Caso de Uso e Classe). |

### Estrutura do Repositório

O projeto segue um padrão técnico claro para separação de responsabilidades:

| Diretório | Descrição |
| :--- | :--- |
| **`src/`** | Contém todo o código-fonte principal (dividido em `/c` e `/python`). |
| **`data/`** | Contém os arquivos de persistência (`.csv`) usados pelo sistema. |
| **`docs/`** | Contém a documentação formal: o relatório PIM, diagramas UML e artefatos de outras disciplinas (`artefatos_academicos/`). |
| **`assets/`** | Mídia de apoio, como capturas de tela do sistema em execução. |

## 🚀 Como Executar o Sistema

### Pré-requisitos

* Interpretador Python 3.x (com Tkinter).
* Compilador C (GCC ou equivalente) para o módulo de baixo nível.

### Passos para Inicialização

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/VitorMoura-coder/PIM.git](https://github.com/VitorMoura-coder/PIM.git)
    cd PIM
    ```
2.  **Compilar o Módulo C:**
    ```bash
    # Se aplicável, compile o módulo C na pasta src/c antes de rodar o Python.
    cd src/c
    gcc -o user_module *.c
    cd ../..
    ```
3.  **Executar a Aplicação Principal (Python):**
    ```bash
    python3 src/python/main.py
    ``` 

## 👥 Autoria (Novembro / 2025)

Este projeto foi desenvolvido pelo grupo:

* ARTHUR FERNANDES REIS
* JOÃO EDUARDO SILVA NEIVA NEU
* JOÃO PEDRO AMÉRICO DA SILVA
* LUCAS MATHEUS MARQUES GONÇALVES
* MIGUEL DINIZ BARRETO DOS SANTOS FILHO
* VITOR DE MOURA DA SILVA

