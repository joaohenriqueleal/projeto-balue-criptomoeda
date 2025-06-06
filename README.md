# BALUE - Blockchain Descentralizada

**BALUE** é uma blockchain peer-to-peer (P2P) desenvolvida para transações descentralizadas e seguras.

## Funcionamento Geral

- Cada **transação** é assinada digitalmente usando **Elliptic Curve Cryptography (ECC)**
- Utiliza:
  - Blocos
  - Mineração Proof of Work (PoW)
  - Ajuste de dificuldade
  - Mecanismo de halving nas recompensas

### Estrutura dos Blocos
| Componente | Descrição |
|------------|-----------|
| Hash anterior | Referência ao bloco anterior |
| Transações | Lista de transações incluídas |
| Nonce | Prova de trabalho |
| Timestamp | Data de criação |

## Mineração e Recompensa

**Recompensa inicial:** 12.5 BALUE

**Halving:** A cada 250.000 blocos (redução pela metade)

### Exemplo de Halvings
| Bloco | Recompensa |
|-------|------------|
| 0 | 12.5 |
| 250_000 | 6.25 |
| 500_000 | 3.125 |
| 750_000 | 1.5625 |
| ... | ... |

## Como Rodar um Nó

### Pré-requisitos
- Python 3.x
- IDE (VS Code, PyCharm) ou terminal
- Dependências do projeto

### Versões Disponíveis
| Versão | Arquivo | Tipo |
|--------|---------|------|
| Linha de comando | `main.py` | Terminal |
| Interface gráfica | `mainqt.py` | GUI |

### Execução via IDE
1. Abra o projeto
2. Execute:
   - `main.py` (CLI)
   - `main-qt.py` (GUI)

### Execução via Terminal
```bash
cd balue_master/main/
python3 main.py       # CLI
python3 main-qt.py     # GUI
