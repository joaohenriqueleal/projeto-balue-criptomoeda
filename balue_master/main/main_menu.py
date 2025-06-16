from p2p_protocol.node import *
from mine.miner import *
from decimal import Decimal
from datetime import datetime, timezone


def main() -> None:
    wallet = Wallet(True)
    miner = Miner(wallet.private_key, wallet.public_key, wallet.address)
    node = Node(8888)
    thread_request = threading.Thread(target=node.request_chain)
    thread_request.start()
    thread_broadcast_peers = threading.Thread(target=node.broadcast_peers)
    thread_broadcast_peers.start()
    print('=' * 60)
    node.peer_infos()
    print('=' * 60)
    print('Balue: Um novo sistema de pagamento P2P.'.center(60))
    print('~' * 60)
    print(f'\033[;32mSaldo Balue:  {round(Decimal(chain_state.get_balance(wallet.address)), 8):.8f} B$\033[m')
    print(f'Endereço Balue:  {wallet.address}')
    print('=' * 60)
    while True:
        thread_request = threading.Thread(target=node.request_chain)
        thread_request.start()
        print('[ 1 ] para Consultar saldo.')
        print('[ 2 ] para Consultar endereço Balue.')
        print('[ 3 ] para Transferir Balue.')
        print('[ 4 ] para Minerar Balue.')
        print('[ 5 ] para Consultar IP e PORTA.')
        print('[ 6 ] para Adicionar um novo peer a sua lista.')
        print('[ 7 ] para Ver descrições de transações para o seu endereço.')
        print('[ 8 ] para Ver os últimos 10 blocos + o bloco pendente.')
        print('[ 9 ] para Adicionar um novo bloco aos blocos pendentes.')
        print('[ 10 ] para Ver peers conhecidos.')
        print('[ 11 ] para Sair.')
        print('~' * 60)
        try:
            option = int(input('>>>  '))
            print('~' * 60)
        except:
            print('\033[;31mDigite um inteiro válido.\033[m')
            continue
        else:
            if option == 1:
                print(f'\033[;32mSaldo Balue:  {round(Decimal(chain_state.get_balance(wallet.address)), 8):.8f} B$\033[m')
                print('=' * 60)
            elif option == 2:
                print(f'Endereço Balue:  {wallet.address}')
                print('=' * 60)
            elif option == 3:
                if len(chain_state.pending_block) > 0:
                    if len(chain_state.pending_block[0].transactions) + 1 > chain_state.max_transactions_per_block:
                        print('\033[;31mO bloco pendente está cheio no momento!\033[m')
                        continue
                try:
                    destino = str(input('Endereço balue do destinatário:  ')).strip()
                    valor = float(input('Valor da transação:  B$'))
                    descricao = str(input('Descrição (opcional):  ')).strip()
                    if not descricao: descricao = "0"
                    if len(descricao) > 80:
                        print('\033[;31mDescrição muito grande! Cancelada! Máximo 80 caractéres.\033[m')
                        print('=' * 60)
                        continue
                    if valor == 0:
                        print('\033[;31mO valor deve ser maior que zero!\033[m')
                        print('=' * 60)
                        continue
                except:
                    print('\033[;31mDigite um valor válido!\033[m')
                    continue
                else:
                    fees = chain_state.calculate_fees(valor)
                    if (valor + fees) > chain_state.get_balance(wallet.address):
                        print(f'Valor + Taxas: {fees + valor:.8f}')
                        print('\033[;31mSaldo insuficiente!\033[m')
                        print('=' * 60)
                        continue
                    try:
                        print('~' * 60)
                        print(f'O valor mais as taxas ficará: {valor + fees:.8f} B$')
                        confirmacao = str(input('Confirma?  [s/n]')).strip().lower()[0]
                    except:
                        print('\033[;31mInválido!\033[m')
                        print('=' * 60)
                    else:
                        if confirmacao in 'sy':
                            chain_state.new_pending_block()
                            t = Transaction(wallet.address, destino, valor, chain_state.calculate_fees(valor),
                                            chave_publica_para_json(wallet.public_key), descricao,
                                            chain_state.transactions_difficulty())
                            t.signature = assinatura_para_json(assinar_hash(wallet.private_key, t.hash))
                            chain_state.add_transaction_to_pending(t)
                            thread_broadcast_pending = threading.Thread(target=node.broadcast_pending_block)
                            thread_broadcast_pending.start()
                            print('\033[;32mTransação adicionada com sucesso!\033[m')
                            print('=' * 60)
                        else:
                            print('\033[;31mTransação cancelada!\033[m')
                            print('=' * 60)
            elif option == 4:
                if len(chain_state.pending_block) > 0:
                    if len(chain_state.pending_block[0].transactions) < chain_state.min_transactions_block(chain_state.pending_block[0].index):
                        print('\033[;31mErro! O bloco pendente precisa de mais transações!\033[m')
                        continue
                    now = datetime.now()
                    print(now.strftime(f'\033[;31m⛏️ Mineração iniciada em: %y-%m-%d %H:%M:%S\033[m com dificuldade {chain_state.pending_block[0].difficulty}.'))
                    print(f'\033[;31mMinerando bloco #{chain_state.pending_block[0].index}...\033[m')
                    resultado = miner.mine()
                    if resultado:
                        now = datetime.now()
                        print(now.strftime(f'\033[;31m⛏️ Mineração Terminada em: %y-%m-%d %H:%M:%S\033[m.'))
                        print(f'\033[;32mRecompensa de:  {chain_state.load_block(len(chain_state.chain) - 1)["reward"]} B$ adicionada!\033[m')
                        print(f'\033[;32mNovo saldo:  {round(Decimal(chain_state.get_balance(wallet.address)), 8):.8f} B$\033[m')
                        thread_broadcast_last_block = threading.Thread(target=node.broadcast_last_block)
                        thread_broadcast_last_block.start()
                        print('=' * 60)
                    else:
                        print('\033[;31mBloco minerado é inválido! Sem recompensas!\033[m')
                        print('=' * 60)
                else:
                    print('\033[;31mNão há bloco pendente!\033[m')
                    print('=' * 60)
            elif option == 5:
                node.peer_infos()
                print('=' * 60)
            elif option == 6:
                try:
                    ip = str(input('IP do peer:  ')).strip()
                    port = int(input('PORTA do peer:  '))
                    if node.add_peer(ip, port):
                        thread_broadcast_peers = threading.Thread(target=node.broadcast_peers)
                        thread_broadcast_peers.start()
                        print('\033[;32mNode adicionado com sucesso!\033[m')
                        print('=' * 60)
                    else:
                        print('\033[;31mNode inválido!\033[m')
                        print('=' * 60)
                except:
                    print('\033[;31mDigite uma porta válida!\033[m')
                    print('=' * 60)
            elif option == 7:
                print('DESCRIÇÕES DE TRANSAÇÕES'.center(60))
                print('=' * 60)
                for i in range(len(chain_state.chain) - 1):
                    blk = chain_state.load_block(i)
                    for tr in blk["transactions"]:
                        if tr["receiver"] == wallet.address and tr["metadata"] != "0":
                            timestamp_s = tr["timestamp"] / 1_000_000_000
                            dt = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
                            print(f'Em:  {dt.strftime("%Y-%m-%d %H:%M:%S")}')
                            print(f'De:  {tr["receiver"]}')
                            print(f'Descrição:  {tr["metadata"]}')
                            print('~' * 60)
                print('=' * 60)
            elif option == 8:
                print('Últimos 10 blocos da rede + o pendente em amarelo.'.center(60))
                print('=' * 60)

                total_blocks = len(chain_state.chain)
                for i in range(max(0, total_blocks - 10), total_blocks):
                    blk = chain_state.load_block(i)
                    print(f'Bloco #{blk["index"]}, Hash:  {blk["hash"][:10]}...{blk["hash"][10:25]}...')
                    print(f'      com {len(blk["transactions"])} transações.')
                    print('~' * 60)

                if len(chain_state.pending_block) > 0:
                    print('=' * 60)
                    print(f'\033[;33mBloco pendente #{chain_state.pending_block[0].index}\033[m')
                    print(f'\033[;33m      com {len(chain_state.pending_block[0].transactions)} transações.\033[m')

                print('=' * 60)
            elif option == 9:
                    if chain_state.new_pending_block():
                        print('\033[;32mNovo bloco pendente adicionado!\033[m')
                        thread_broadcast_pending = threading.Thread(target=node.broadcast_pending_block)
                        thread_broadcast_pending.start()
                        print('=' * 60)
                    else:
                        print('\033[;31mHá um bloco pendente a ser minerado!\033[m')
                        print('=' * 60)
            elif option == 10:
                print('PEERS CONHECIDOS.'.center(60))
                print('=' * 60)
                for peer in node.peers:
                    print(f'Endereço:  {peer["ip"]}:{peer["port"]}')
                    print('~' * 60)
            elif option == 11:
                print('Processo finalizado.')
                exit()
            else:
                print('\033[;31mDigite um inteiro de 1 a 10.\033[m')
                continue



if __name__ == '__main__':
    if chain_state.chain_is_valid():
        main()
    else:
        while not chain_state.chain_is_valid():
            os.remove(f'balue/chain/{len(chain_state.chain) - 1}.json')
            chain_state.chain.pop()
            chain_state.save_chain()
        main()
