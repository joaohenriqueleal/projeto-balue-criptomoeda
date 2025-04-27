from balue_master.src.main.connection.node import *
from decimal import Decimal
from datetime import datetime


def main_menu():
    wallet = Wallet(True)
    miner = Miner(wallet.address, wallet.public_key, wallet.private_key)
    node = Node(8888)
    thread_node = threading.Thread(target=node.start_node)
    thread_node.start()
    print('=' * 80)
    node.peer_infos()
    print('=' * 80)
    print('BALUE: A New P2P Decentralized Cash System.')
    print('=' * 80)
    print(f'\033[;32mSaldo: {Decimal(b.get_balance(wallet.address)):.8f} B$\033[m')
    print(f'Endereço Balue:  {wallet.address}')
    print('~' * 80)
    while True:
        thread_request_chain = threading.Thread(target=node.request_chain)
        thread_request_chain.start()
        print('[1] para Consultar Saldo.')
        print('[2] para Consultar Endereço Balue.')
        print('[3] para Transferir Balue.')
        print('[4] para Minerar Balue.')
        print('[5] para Ver últimos dez blocos.')
        print('[6] para Adicionar um peer a sua lista.')
        print('[7] para Consultar IP e PORTA.')
        print('[8] para Sair.')
        try:
            print('~' * 80)
            opcao = int(input('>>>  '))
            print('~' * 80)
        except:
            print('~' * 80)
            print('\033[;31mDigite algo válido!\033[m')
            print('~' * 80)
            continue
        if opcao == 1:
            print(f'\033[32mSaldo: {Decimal(b.get_balance(wallet.address)):.8f} B$\033[m')
            print('~' * 80)
        elif opcao == 2:
            print(f'Endereço Balue:  {wallet.address}')
            print('~' * 80)
        elif opcao == 3:
            try:
                receiver = input('Endereço do Balue destinatário:  ').strip()
                value = float(input('\033[32mValor da transação: B$ \033[m'))
                print('~' * 80)
                metadata = input('Descrição (opcional): ')
                if metadata == "":
                    metadata = None
                tr = Transaction(wallet.address, receiver, value, b.adjust_mining_fees(), None, chave_publica_para_json(wallet.public_key), metadata)
                sign = assinar_hash(wallet.private_key, tr.hash)
                tr.signature = assinatura_para_json(sign)
                print('~' * 80)
                print(f'Com as taxas a transação sairá por: \033[;32m{Decimal(tr.value + tr.fees):.8f} B$\033[m')
                confirmacao = input('Confirma a transação?  ').strip().lower()[0]
                if confirmacao in 'sy':
                    if value >= b.get_balance(wallet.address):
                        print('~' * 80)
                        print('\033[;31mSaldo insuficiente!\033[m')
                        print('~' * 80)
                        continue
                    b.add_transaction_to_pending(tr)
                    thread_broadcast_pending = threading.Thread(target=node.broadcast_pending)
                    thread_broadcast_pending.start()
                    print('~' * 80)
                    print('\033[32mAdicionada ao bloco!\033[m')
                    print('~' * 80)
                else:
                    print('~' * 80)
                    print('\033[;31mTransação cancelada!\033[m')
                    print('~' * 80)
            except:
                print('~' * 80)
                print('\033[;31mDigite valores válidos!\033[m')
                print('~' * 80)
        elif opcao == 4:
            if b.chain:
                if not b.pending_block or b.pending_block[0].index == b.chain[-1]["index"]:
                    print('\033[;31mNão há blocos pendentes há minerar!\033[m')
                    print('~' * 80)
                    continue
            now = datetime.now()
            print(now.strftime('\033[;31m⛏️ Mineração iniciada em: %y-%m-%d %H:%M:%S\033[m'))
            mine = miner.mine()
            print(f'\033[;33mBloco {b.chain[-1]["index"]} minerado!\033[m')
            print(f'\033[1;43m  Recompensa de: {b.chain[-1]["reward"]} B$ adicionada com sucesso!  \033[0m')
            print(f'Novo saldo: {Decimal(b.get_balance(wallet.address)):.8f}')
            now = datetime.now()
            print(now.strftime('\033[;31m⛏️ Terminada em: %y-%m-%d %H:%M:%S\033[m'))
            if mine:
                thread_broadcast_chain = threading.Thread(target=node.broadcast_chain)
                thread_broadcast_chain.start()
            print('~' * 80)
        elif opcao == 5:
            print('ultimate 10 blocks: ')
            print('~' * 80)
            b.print_chain()
            print('~' * 80)
        elif opcao == 6:
            try:
                ip = input('IP do peer:  ').strip()
                port = int(input('PORTA do peer:  '))
                node.add_peer(ip, port)
                thread_peers = threading.Thread(target=node.broadcast_peers)
                thread_peers.start()
                print('~' * 80)
                print('Peer adicionado com sucesso!')
                print('~' * 80)
            except:
                print('\033[;31mDigite algo válido!\033[m')
                print('~' * 80)
                continue
        elif opcao == 7:
            node.peer_infos()
            print('~' * 80)
        elif opcao == 8:
            print('Volte Sempre!')
            time.sleep(3)
            exit()
        else:
            print('\033[;31mDigite um inteiro entre 1 e 8!\033[m')
        integridade = b.chain_is_valid()
        if integridade: pass
        else:
            print('~' * 80)
            print('\033[;31mBlockchain inválido! Removendo...\033[m')
            os.remove(b.chain_path)
            print('~' * 80)


if __name__ == '__main__':
    main_menu()
