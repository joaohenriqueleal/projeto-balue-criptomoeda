from main_cli.Actions import *


class MainMenu:

    def __init__(self, wallet_name: str = None) -> None:
        if wallet_name:
            self.actions: 'Actions' = Actions(wallet_name)
        else:
            self.actions: 'Actions' = Actions()
        self.messages: 'Messages' = Messages()
        self.miner: 'Miner' = Miner(self.actions.data_views.wallet_manager.wallet.private_key,
                                    self.actions.data_views.wallet_manager.wallet.public_key,
                                    self.actions.data_views.wallet_manager.wallet.address)

    def main(self) -> None:
        if not self.actions.data_views.wallet_manager.wallet or not self.miner:
            self.actions.data_views.wallet_manager.create_new_wallet()
        self.actions.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.request_chain()
        self.messages.error_message(datetime.now().strftime("[INFO] Node initialized in %d/%m/%Y/%H:%M:%S"))
        self.messages.error_message('Synchronizing balance please, await some minutes or hours...')
        print('=' * 80)
        self.actions.node.node_infos()
        print('~' * 80)
        self.actions.data_views.print_balance()
        self.actions.print_address()
        while True:
            if not self.actions.data_views.wallet_manager.wallet or not self.miner:
                self.actions.data_views.wallet_manager.create_new_wallet()
            self.actions.data_views.wallet_manager.wallet.define_balance()
            self.actions.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.request_chain()
            self.actions.node.handle.broadcasts.sni.rpb.rni.bc.bp.broadcast_peers()
            self.actions.node.handle.broadcasts.sni.rpb.request_pending_block()
            print('~' * 80)
            print(self.actions.data_views.wallet_manager.wallet.wallet_storage.name.center(80))
            print('=' * 80)
            print('[ 1 ] Consult balance.')
            print('[ 2 ] Consult balue address.')
            print('[ 3 ] Transfer balue.')
            print('[ 4 ] Mine pending.')
            print('[ 5 ] View last ten blocks.')
            print('[ 6 ] View transactions descriptions.')
            print('[ 7 ] Add peer.')
            print('[ 8 ] View your node infos.')
            print('[ 9 ] Switch wallet.')
            print('[ 10 ] Create new wallet.')
            print('[ 11 ] Delete wallet.')
            print('[ 12 ] Add new pending block.')
            print('[ 13 ] Exit.')
            try:
                print('~' * 80)
                option: int = int(input('>>>  '))
                print('~' * 80)
            except ValueError:
                self.messages.error_message()
                continue
            if option == 1:
                self.actions.data_views.print_balance()
            elif option == 2:
                self.actions.print_address()
            elif option == 3:
                self.actions.transfer()
            elif option == 4:
                self.actions.mine()
            elif option == 5:
                self.actions.data_views.view_last_ten_blocks()
            elif option == 6:
                self.actions.data_views.view_transactions_descriptions()
            elif option == 7:
                self.actions.add_peer()
            elif option == 8:
                self.actions.node.node_infos()
            elif option == 9:
                self.actions.data_views.wallet_manager.switch_wallet()
            elif option == 10:
                self.actions.data_views.wallet_manager.create_new_wallet()
            elif option == 11:
                self.actions.data_views.wallet_manager.delete_wallet()
            elif option == 12:
                self.actions.new_pending()
            elif option == 13:
                print('bye!')
                exit()
            else:
                self.messages.error_message('Input a option between 1/12')
            if len(blockchain.pending_blocks) > 0:
                self.actions.node.handle.broadcasts.sni.rpb.rni.bc.bp.rc.blb.bpb.broadcast_pending_block()
