from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem, ThreeLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from datetime import datetime, timedelta
from decimal import Decimal

from network_protocol.node import *

Builder.load_string('''
<CustomTextField>:
    size_hint_y: None
    height: dp(48)
    mode: "rectangle"
    font_size: dp(16)

<TransactionCard>:
    orientation: "vertical"
    size_hint: None, None
    size: dp(300), dp(150)
    padding: dp(10)
    spacing: dp(5)
    pos_hint: {"center_x": 0.5}
    md_bg_color: app.theme_cls.primary_color
    elevation: 2
    radius: [12,]

    MDLabel:
        text: root.title
        font_style: "H6"
        size_hint_y: None
        height: self.texture_size[1]
        halign: "center"
        text_size: self.width, None

    MDLabel:
        text: root.details
        font_style: "Body2"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: self.texture_size[1]
        halign: "center"
        text_size: self.width, None
        padding: [dp(5), dp(5)]

    MDLabel:
        text: root.amount
        font_style: "Subtitle1"
        theme_text_color: "Primary"
        size_hint_y: None
        height: self.texture_size[1]
        halign: "center"
        text_size: self.width, None

<NavigationDrawerContent>:
    orientation: "vertical"
    padding: dp(15)
    spacing: dp(15)

    MDLabel:
        text: "Menu"
        font_style: "H5"
        size_hint_y: None
        height: self.texture_size[1]
        halign: "center"

    MDRectangleFlatButton:
        text: "Refresh Data"
        on_release: root.refresh_data()
        size_hint_y: None
        height: dp(48)

    MDRectangleFlatButton:
        text: "Node Info"
        on_release: root.show_node_info()
        size_hint_y: None
        height: dp(48)

    MDRectangleFlatButton:
        text: "Exit"
        on_release: root.exit_app()
        size_hint_y: None
        height: dp(48)

<MainScreen>:
    name: "main"

    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Balue Wallet"
            elevation: 4
            left_action_items: [["menu", lambda x: root.toggle_nav_drawer()]]
            right_action_items: [["refresh", lambda x: root.refresh_data()]]

        MDBottomNavigation:
            id: bottom_nav
            panel_color: app.theme_cls.primary_color

            MDBottomNavigationItem:
                name: "wallet"
                text: "Wallet"
                icon: "wallet"

                ScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: dp(20)
                        spacing: dp(20)
                        size_hint_y: None
                        height: self.minimum_height

                        MDCard:
                            orientation: "vertical"
                            padding: dp(20)
                            spacing: dp(10)
                            size_hint_y: None
                            height: dp(150)
                            pos_hint: {"center_x": 0.5}
                            elevation: 2
                            radius: [12,]

                            MDLabel:
                                text: "Your Balance"
                                font_style: "H6"
                                halign: "center"
                                size_hint_y: None
                                height: self.texture_size[1]

                            MDLabel:
                                text: root.balance
                                font_style: "H4"
                                halign: "center"
                                size_hint_y: None
                                height: self.texture_size[1]

                            MDRectangleFlatButton:
                                text: "Copy Address"
                                size_hint: None, None
                                size: dp(200), dp(40)
                                pos_hint: {"center_x": 0.5}
                                on_release: root.copy_address()

                        MDRaisedButton:
                            text: "Send BAL$"
                            size_hint: None, None
                            size: dp(200), dp(48)
                            pos_hint: {"center_x": 0.5}
                            on_release: root.show_send_dialog()

                        MDRaisedButton:
                            text: "Mine BAL$"
                            size_hint: None, None
                            size: dp(200), dp(48)
                            pos_hint: {"center_x": 0.5}
                            on_release: root.show_mine_dialog()

                        MDBoxLayout:
                            size_hint_y: None
                            height: dp(30)
                            padding: [0, dp(10), 0, 0]

                            MDLabel:
                                text: "Recent Transactions (Last 7 days)"
                                font_style: "H6"
                                halign: "center"
                                size_hint_x: 1

                        GridLayout:
                            id: recent_transactions
                            cols: 2
                            spacing: dp(10)
                            padding: dp(10)
                            size_hint_y: None
                            height: self.minimum_height

            MDBottomNavigationItem:
                name: "blocks"
                text: "Blocks"
                icon: "cube"

                ScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: dp(20)
                        spacing: dp(20)
                        size_hint_y: None
                        height: self.minimum_height

                        MDLabel:
                            text: "Latest Blocks"
                            font_style: "H6"
                            halign: "center"
                            size_hint_y: None
                            height: self.texture_size[1]

                        MDBoxLayout:
                            id: blocks_list
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(10)

            MDBottomNavigationItem:
                name: "network"
                text: "Network"
                icon: "lan"

                ScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: dp(20)
                        spacing: dp(20)
                        size_hint_y: None
                        height: self.minimum_height

                        MDLabel:
                            text: "Network Peers"
                            font_style: "H6"
                            halign: "center"
                            size_hint_y: None
                            height: self.texture_size[1]

                        MDRaisedButton:
                            text: "Add Peer"
                            size_hint: None, None
                            size: dp(200), dp(48)
                            pos_hint: {"center_x": 0.5}
                            on_release: root.show_add_peer_dialog()

                        MDBoxLayout:
                            id: peers_list
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(10)

    MDNavigationDrawer:
        id: nav_drawer
        size_hint: 0.8, 1
        elevation: 10

        NavigationDrawerContent:
            id: nav_content
            refresh_data: root.refresh_data
            show_node_info: root.show_node_info
            exit_app: root.exit_app
''')


class CustomTextField(MDTextField):
    pass


class TransactionCard(MDCard):
    title = StringProperty()
    details = StringProperty()
    amount = StringProperty()


class NavigationDrawerContent(MDBoxLayout):
    refresh_data = ObjectProperty()
    show_node_info = ObjectProperty()
    exit_app = ObjectProperty()


class MainScreen(Screen):
    balance = StringProperty("0.00000000 BAL$")
    wallet_address = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wallet = Wallet(True)
        self.miner = Miner(self.wallet.private_key, self.wallet.public_key, self.wallet.address)
        self.node = Node()
        self.dialog = None

        # Initialize network
        self.node.broadcasts.broadcast_peers()
        self.node.broadcasts.request_chain()

        # Set wallet address
        self.wallet_address = self.wallet.address

        # Schedule periodic updates
        Clock.schedule_interval(self.update_data, 30)
        Clock.schedule_once(self.update_data, 0)

    def toggle_nav_drawer(self):
        nav_drawer = self.ids.nav_drawer
        nav_drawer.set_state("open" if nav_drawer.state == "close" else "close")

    def update_data(self, *args):
        self.update_balance()
        self.update_transactions()
        self.update_blocks()
        self.update_peers()

    def refresh_data(self):
        self.node.broadcasts.broadcast_peers()
        self.node.broadcasts.request_chain()
        self.update_data()
        self.show_success("Data refreshed successfully!")

    def show_node_info(self):
        self.show_success(f"  Public IP:  {self.node.handle.public_ip} \n"
                          f"  Local IP:  {self.node.handle.local_ip} \n"
                          f"  PORT:  {self.node.handle.port}")

    def exit_app(self):
        MDApp.get_running_app().stop()

    def copy_address(self):
        Clipboard.copy(self.wallet.address)
        self.show_success("Address copied to clipboard!")

    def get_balance(self) -> float:
        address: str = self.wallet.address
        balance: float = 0
        for blk in blockchain.pending_block:
            for tr in blk.transactions:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
        for i in range(0, len(blockchain.validations.adjusts.storage.chain)):
            blk = blockchain.validations.adjusts.storage.load_block(i)
            if blk["miner_address"] == self.wallet.address:
                balance += (blk["reward"] + blk["total_fees"])
            for tr in blk["transactions"]:
                if tr["sender"] == address:
                    balance -= (tr["value"] + tr["fee"])
                if tr["receiver"] == address:
                    balance += tr["value"]
        return balance

    def update_balance(self):
        balance = self.get_balance()
        self.balance = f"{Decimal(balance):.8f} BAL$"

    @staticmethod
    def format_timestamp(timestamp_ns: int) -> str:
        timestamp_sec = timestamp_ns / 1_000_000_000
        dt = datetime.fromtimestamp(timestamp_sec)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def is_within_7_days(self, timestamp_ns: int) -> bool:
        timestamp_sec = timestamp_ns / 1_000_000_000
        transaction_time = datetime.fromtimestamp(timestamp_sec)
        return datetime.now() - transaction_time <= timedelta(days=7)

    def update_transactions(self):
        transactions_container = self.ids.recent_transactions
        transactions_container.clear_widgets()

        # Get recent transactions involving this wallet from last 7 days
        transactions = []
        for i in range(max(0, len(blockchain.validations.adjusts.storage.chain) - 100), len(blockchain.validations.adjusts.storage.chain)):
            blk = blockchain.validations.adjusts.storage.load_block(i)
            for tr in blk["transactions"]:
                if (tr["receiver"] == self.wallet.address or tr["sender"] == self.wallet.address) and \
                        self.is_within_7_days(tr["validation_timestamp"]):
                    transactions.append((blk["index"], tr))

        # Sort by block index (newest first)
        transactions.sort(key=lambda x: x[0], reverse=True)

        # Display transactions in grid
        for blk_index, tr in transactions[:10]:  # Limit to 10 most recent
            card = TransactionCard()
            if tr["receiver"] == self.wallet.address:
                card.title = "Received BAL$"
                card.amount = f"+{tr['value']:.8f} BAL$"
            else:
                card.title = "Sent BAL$"
                card.amount = f"-{tr['value'] + tr['fee']:.8f} BAL$"

            details = []
            if tr["receiver"] == self.wallet.address:
                details.append(f"From: {tr['sender'][:10]}...")
            else:
                details.append(f"To: {tr['receiver'][:10]}...")
            details.append(f"Block: #{blk_index}")
            details.append(f"Time: {self.format_timestamp(tr['validation_timestamp'])}")

            if tr["metadata"] != "0":
                details.append(f"Note: {tr['metadata']}")

            card.details = "\n".join(details)
            transactions_container.add_widget(card)

    def update_blocks(self):
        blocks_container = self.ids.blocks_list
        blocks_container.clear_widgets()

        chain_length = len(blockchain.validations.adjusts.storage.chain)
        start_index = max(0, chain_length - 10)

        for pending_blk in blockchain.pending_block:
            item = ThreeLineListItem(
                text=f"[Pending] Block #{pending_blk.index}",
                secondary_text=f"Hash: {pending_blk.hash[:10]}...{pending_blk.hash[-10:]}",
                tertiary_text=f"{pending_blk.total_transactions} transactions",
                bg_color=(0.9, 0.9, 0.3, 0.3)
            )
            blocks_container.add_widget(item)

        for i in range(start_index, chain_length)[::-1]:
            blk = blockchain.validations.adjusts.storage.load_block(i)
            item = ThreeLineListItem(
                text=f"Block #{blk['index']}",
                secondary_text=f"Hash: {blk['hash'][:10]}...{blk['hash'][-10:]}",
                tertiary_text=f"{blk['total_transactions']} transactions",
            )
            blocks_container.add_widget(item)

    def update_peers(self):
        peers_container = self.ids.peers_list
        peers_container.clear_widgets()

        for peer in self.node.broadcasts.peers.peers:
            item = TwoLineListItem(
                text=f"{peer['ip']}:{peer['port']}",
                secondary_text=f"Last seen: {peer.get('last_seen', 'unknown')}"
            )
            peers_container.add_widget(item)

    def show_send_dialog(self):
        content = MDBoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, height=dp(250))

        value_field = CustomTextField(hint_text="Amount (BAL$)")
        fee_field = CustomTextField(hint_text="Fee (BAL$)")
        receiver_field = CustomTextField(hint_text="Receiver Address")
        note_field = CustomTextField(hint_text="Note (optional)")

        content.add_widget(value_field)
        content.add_widget(fee_field)
        content.add_widget(receiver_field)
        content.add_widget(note_field)

        self.dialog = MDDialog(
            title="Send BAL$",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SEND", on_release=lambda x: self.send_transaction(
                    value_field.text,
                    fee_field.text,
                    receiver_field.text,
                    note_field.text
                ))
            ]
        )
        self.dialog.open()

    def send_transaction(self, value_str, fee_str, receiver, metadata):
        try:
            value = float(value_str)
            fee = float(fee_str)

            if value + fee > self.get_balance():
                self.show_error("Insufficient balance!")
                return

            if len(blockchain.pending_block) > 0:
                if blockchain.pending_block[0].total_transactions >= MAX_TRANSACTIONS_PER_BLOCK:
                    self.show_error('Pending block is full! Please wait for the next one!')
                    return

            blockchain.new_pending_block()
            t = Transaction(
                self.wallet.address,
                receiver.strip(),
                value,
                fee,
                blockchain.validations.adjusts.adjust_transactions_difficulty(blockchain.index()),
                metadata.strip()
            )

            t.validate(self.wallet.wallet_methods.public_key_to_json(self.wallet.public_key))
            sign = self.wallet.wallet_methods.sign_hash(self.wallet.private_key, t.hash)
            t.sign(self.wallet.wallet_methods.signature_to_json(sign))

            blockchain.add_transaction_to_pending(t)
            self.node.broadcasts.broadcast_pending_block()

            # Show transaction added confirmation
            confirmation_dialog = MDDialog(
                title="Transaction Submitted",
                text="Your transaction has been added to the pending block and will be mined soon.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: confirmation_dialog.dismiss())]
            )
            confirmation_dialog.open()

            self.update_data()
            self.dialog.dismiss()
        except ValueError:
            self.show_error("Please enter valid numbers for amount and fee")

    def show_mine_dialog(self):
        content = MDBoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, height=dp(120))

        note_field = CustomTextField(hint_text="Block Note (optional)")

        content.add_widget(note_field)

        self.dialog = MDDialog(
            title="Mine BAL$",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="MINE", on_release=lambda x: self.start_mining(note_field.text))
            ]
        )
        self.dialog.open()

    def start_mining(self, metadata):
        self.dialog.dismiss()

        if len(blockchain.pending_block) > 0:
            if blockchain.validations.adjusts.min_transactions(blockchain.index()) > blockchain.pending_block[0].total_transactions:
                self.show_error('block has not yet reached the minimum number of transactions to mine')
                return
        else:
            blockchain.new_pending_block()
            self.node.broadcasts.broadcast_pending_block()
            if blockchain.validations.adjusts.min_transactions(blockchain.index()) > blockchain.pending_block[0].total_transactions:
                self.show_error('block has not yet reached the minimum number of transactions to mine')
                return

        mining_dialog = MDDialog(
            title="Mining in progress...",
            text="Please wait while your node mines the next block",
            auto_dismiss=False
        )
        mining_dialog.open()

        def mine_complete(*args):
            now = datetime.now()
            self.miner.unique_mine(metadata)
            self.node.broadcasts.broadcast_last_block()

            mining_dialog.dismiss()

            # Show mining complete confirmation
            confirmation_dialog = MDDialog(
                title="Mining Complete",
                text=f"Block #{len(blockchain.validations.adjusts.storage.chain) - 1} mined successfully!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: confirmation_dialog.dismiss())]
            )
            confirmation_dialog.open()

            self.update_data()

        Clock.schedule_once(mine_complete, 0.1)

    def show_add_peer_dialog(self):
        content = MDBoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, height=dp(150))

        ip_field = CustomTextField(hint_text="Peer IP")
        port_field = CustomTextField(hint_text="Peer Port")

        content.add_widget(ip_field)
        content.add_widget(port_field)

        self.dialog = MDDialog(
            title="Add Network Peer",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="ADD", on_release=lambda x: self.add_peer(ip_field.text, port_field.text))
            ]
        )
        self.dialog.open()

    def add_peer(self, ip, port_str):
        try:
            port = int(port_str)
            feedback = self.node.broadcasts.peers.add_peer(ip.strip(), port)
            self.node.broadcasts.broadcast_peers()
            self.node.broadcasts.request_chain()

            self.show_success(feedback)
            self.update_peers()
            self.dialog.dismiss()
        except ValueError:
            self.show_error("Please enter a valid port number")

    def show_error(self, message):
        self.dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    def show_success(self, message):
        self.dialog = MDDialog(
            title="Success",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()


class BalueWalletApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Dark"

        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == '__main__':
    BalueWalletApp().run()
