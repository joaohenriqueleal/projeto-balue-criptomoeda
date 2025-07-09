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

**Recompensa inicial:** 25

**Halving:** A cada 360.000 blocos (redução pela metade)

### Exemplo de Halvings
| Bloco | Recompensa |
|-------|------------|
| 0 | 25 |
| 360.000 | 12.5 |
| 720.000 | 6.25 |
| 1.440.000 | 3.125 |
| ... | ... |

## Como Rodar um Nó

### Pré-requisitos
- Python 3.x
- IDE (VS Code, PyCharm) ou terminal
- Dependências do projeto

### Versões Disponíveis
| Versão | Arquivo | Tipo |
|--------|---------|------|
| Linha de comando | `main_cli.py` | Terminal |
| Interface gráfica | `main_gui.py` | GUI |

### Execução via IDE
1. Abra o projeto
2. Execute:
   - `main_cli.py` (CLI)
   - `main_gui.py` (GUI)

### Execução via Terminal
```bash
cd Downloads/balue_master
python3 main_cli.py       # CLI
python3 main_gui.py     # GUI
