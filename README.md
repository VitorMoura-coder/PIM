# 💻 PIM II: Sistema Acadêmico Colaborativo com Apoio de IA

## Visão Geral do Projeto

Este repositório apresenta o **Projeto Integrado Multidisciplinar (PIM II)**, desenvolvido para o curso de **Análise e Desenvolvimento de Sistemas (ADS)**. O projeto foca na construção de um **Sistema Acadêmico Colaborativo** para gerenciamento de alunos, turmas e atividades, com uma arquitetura preparada para incorporar um módulo de **Inteligência Artificial**.

O sistema foi concebido sob a metodologia **Scrum** e possui modelagem completa em **UML**, conforme os artefatos documentados.

---

## ⚙️ Arquitetura Técnica e Stack Tecnológico

O sistema adota uma arquitetura híbrida e modular, separando a responsabilidade de I/O (C) da lógica de negócio (Python).

| Categoria | Tecnologia | Aplicação no Projeto |
| :--- | :--- | :--- |
| **Core de Persistência** | **C** | Módulo de I/O de baixo nível, responsável pela gestão eficiente dos dados CSV. |
| **Lógica de Negócio / GUI** | **Python 3.x** | Responsável pela interface gráfica (`Tkinter`) e pela lógica de negócio principal. |
| **Persistência de Dados** | **CSV** | Formato de armazenamento leve para registros iniciais (usuários, alunos, turmas). |
| **Modelagem** | **UML (Astah)** | Modelagem da arquitetura de software (diagramas e artefatos de engenharia). |

---

## 📂 Estrutura do Repositório (Padrão Técnico)

O projeto segue um padrão de organização claro, separando código, dados e documentação:

| Diretório | Conteúdo Principal | Finalidade |
| :--- | :--- | :--- |
| **`src/`** | `/c` e `/python` | Contém o código-fonte executável do Core C e do Módulo Python. |
| **`data/`** | Arquivos `.csv` | Armazena os arquivos de persistência de dados consumidos pelo Core C. |
| **`docs/`** | Relatório, Modelagem UML, Artefatos. | Contém a documentação formal, incluindo o Relatório PIM e os diagramas de engenharia. |

---

## 📐 Artefatos de Engenharia e Documentação

### Documentação e Modelagem

| Artefato | Localização | Acesso Rápido |
| :--- | :--- | :--- |
| **Relatório Oficial PIM II** | `docs/pim final REV (1).pdf` | [Baixar PDF Aqui](docs/pim%20final%20REV%20(1).pdf) |
| **Projeto UML Nativo (Astah)** | `docs/uml_diagrams/astah projeto pim.asta` | [Baixar Projeto Astah](docs/uml_diagrams/astah%20projeto%20pim.asta) |

### Visualização Rápida

Para uma visualização rápida da modelagem de classes no GitHub:
* **Diagrama de Classes:**
    ![Diagrama de Classes Principal](docs/uml_diagrams/diagrama_classes.png)


---

## 🚀 Instruções de Execução

### Pré-requisitos
1.  Compilador C (GCC).
2.  Interpretador Python 3.x.

### Passos para Inicialização
1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/VitorMoura-coder/PIM.git](https://github.com/VitorMoura-coder/PIM.git)
    cd PIM
    ```

2.  **Compilar o Módulo Core C:**
    ```bash
    # Navega para a pasta do código C
    cd src/c
    # Compila o arquivo C (main_core.c) e gera o executável 'sistema_core'
    gcc main_core.c -o sistema_core
    cd ../..
    ```

3.  **Executar a Aplicação Principal (Python):**
    ```bash
    # Roda a interface e a lógica de negócio
    python3 src/python/main.py
    ```

---

## 👥 Autoria e Licença

Este projeto foi desenvolvido pelo grupo:

| Nome do Aluno | R.A. |
| :--- | :--- |
| ARTHUR FERNANDES REIS | H59DAH1 |
| JOÃO EDUARDO SILVA NEIVA NEU | H658GF0 |
| JOÃO PEDRO AMÉRICO DA SILVA | H70IFB0 |
| LUCAS MATHEUS MARQUES GONÇALVES | F3618A6 |
| MIGUEL DINIZ BARRETO DOS SANTOS FILHO | R873528 |
| VITOR DE MOURA DA SILVA | H6619J8 |
