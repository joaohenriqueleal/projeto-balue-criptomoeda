# BALUE - Blockchain Descentralizada

**BALUE** é uma blockchain peer-to-peer (P2P) desenvolvida para transações descentralizadas e seguras. O sistema utiliza **blocos**, **mineração Proof of Work (PoW)**, **ajuste de dificuldade**, e um **mecanismo de halving** nas recompensas dos mineradores.

## Funcionamento Geral

- Cada **transação** é assinada digitalmente usando **Elliptic Curve Cryptography (ECC)**.
- As transações são agrupadas em **blocos**, que são minerados através de um sistema **Proof of Work (PoW)**.
- Os blocos são propagados pela rede de forma **descentralizada**, usando **sockets TCP** e **threads** para comunicação simultânea entre os nós.
- A **blockchain** é armazenada localmente em um arquivo **JSON**, permitindo validação rápida e persistência dos dados.
- Cada bloco contém:
  - Referência (`hash`) ao bloco anterior
  - Lista de transações
  - Nonce de mineração (prova de trabalho)
  - Timestamp de criação

## Mineração e Recompensa

- A recompensa por bloco **começa em 3.125 unidades de BALUE**.
- A cada **300.000 blocos minerados**, a recompensa sofre um **halving** (redução pela metade).
- Existe um **mínimo garantido**: a recompensa **nunca será inferior a 0.01 BALUE** por bloco, independentemente da quantidade de halvings ocorridos.
- Isso cria uma dinâmica de emissão limitada ao longo do tempo, aumentando a escassez da moeda.

### Exemplo de Halvings

- **Bloco 0**: 3.125 BALUE
- **Bloco 300.000**: 1.5625 BALUE
- **Bloco 600.000**: 0.78125 BALUE
- **Bloco 900.000**: 0.390625 BALUE
- **Bloco 1.200.000**: 0.1953125 BALUE
- **Bloco 1.500.000**: 0.09765625 BALUE
- **Bloco 1.800.000**: 0.048828125 BALUE
- **... até atingir 0.01 BALUE**, onde a recompensa se fixa permanentemente.

## Ajuste de Dificuldade

- A **dificuldade** da mineração é ajustada automaticamente a cada **2016 blocos**.
- O objetivo é manter o tempo médio de mineração constante, garantindo uma emissão estável de novos blocos.
- Se os últimos 2016 blocos forem minerados mais rapidamente do que o esperado, a dificuldade aumenta.
- Se forem minerados mais lentamente, a dificuldade diminui.

## Objetivo da BALUE

A BALUE tem como objetivo proporcionar uma infraestrutura descentralizada para transações digitais, utilizando criptografia moderna e mecanismos justos de mineração, reforçando os princípios de segurança, escassez programada e transparência distribuída.

---

## Tutorial: Como Rodar um Node BALUE

Você pode executar um nó BALUE de diferentes formas, dependendo da sua preferência por **linha de comando**, **interface gráfica** ou um **executável pré-compilado para Linux**.

### Pré-requisitos (caso queira rodar via código-fonte)

Antes de iniciar, verifique se você tem:

- **Python 3.10 ou superior**
- **pip** instalado
- Uma IDE como *VS Code*, *PyCharm*, ou o terminal

Instale as dependências com:

```bash
pip install -r requirements.txt
