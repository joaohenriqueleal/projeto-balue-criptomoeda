import tkinter as tk
from tkinter import messagebox
from decimal import Decimal

from src.main.connection.node import *

class BalueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BALUE: A New P2P Decentralized Cash System")
        self.root.geometry("800x600")

        # Inicializa os componentes principais
        self.wallet = Wallet(True)
        self.miner = Miner(self.wallet.address, self.wallet.public_key, self.wallet.private_key)
        self.node = Node(8888)
        threading.Thread(target=self.node.start_node, daemon=True).start()

        # Atualiza a cadeia do peer
        threading.Thread(target=self.node.request_chain, daemon=True).start()

        self.create_menu()
        self.create_main_panel()
        self.update_balance()

        if b.chain_is_valid(): pass
        else:
            messagebox.showinfo("Erro", f"Blockchain inválido! Removendo...")
            os.remove(b.chain_path)
            b.chain = []

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Atualizar Saldo", command=self.consultar_saldo)
        options_menu.add_command(label="Atualizar Endereço", command=self.consultar_endereco)
        options_menu.add_command(label="Adicionar novo bloco", command=self.add_block)
        options_menu.add_command(label="Transferir Balue", command=self.transferir_balue)
        options_menu.add_command(label="Minerar Balue", command=self.minerar_balue)
        options_menu.add_command(label="Ver Últimos Blocos", command=self.ver_blocos)
        options_menu.add_command(label="Adicionar Peer", command=self.adicionar_peer)
        options_menu.add_command(label="Consultar IP e Porta", command=self.consultar_ip_porta)
        options_menu.add_command(label="Ver Descrições de Transações", command=self.ver_transacoes)

    def create_main_panel(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.balance_label = tk.Label(self.main_frame, text="Saldo: 0.00000000 B$", font=("Arial", 14))
        self.balance_label.pack(pady=10)

        self.address_label = tk.Label(self.main_frame, text=f"Endereço Balue: {self.wallet.address}", font=("Arial", 14))
        self.address_label.pack(pady=10)

        # Botão para copiar o endereço
        def copy_address():
            self.root.clipboard_clear()  # Limpa o conteúdo atual da área de transferência
            self.root.clipboard_append(self.wallet.address)  # Copia o endereço para a área de transferência
            messagebox.showinfo("Copiado", "Endereço copiado para a área de transferência!")

        copy_button = tk.Button(self.main_frame, text="Copiar Endereço", command=copy_address)
        copy_button.pack(pady=5)

        self.status_label = tk.Label(self.main_frame, text="Sistema Online", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def consultar_saldo(self):
        saldo = Decimal(b.get_balance(self.wallet.address))
        self.balance_label.config(text=f"Saldo: {saldo:.8f} B$")
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()

    def consultar_endereco(self):
        self.address_label.config(text=f"Endereço Balue: {self.wallet.address}")
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()

    def add_block(self):
        if len(b.pending_block) == 0:
            new_block = Block(b.index(), b.previous_hash(), b.adjust_difficulty(), None, None, None, b.adjust_reward())
            b.pending_block.append(new_block)
            messagebox.showinfo("Bloco adicionado", "Bloco adicionado com sucesso!")
        else:
            messagebox.showerror("Erro", "Há um bloco pendente a ser minerado!")
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()
        thread_br_pending = threading.Thread(target=self.node.broadcast_pending)
        thread_br_pending.start()

    def transferir_balue(self):
        win = tk.Toplevel(self.root)
        win.title("Transferir Balue")

        tk.Label(win, text="Endereço do destinatário:").pack()
        dest = tk.Entry(win, width=50)
        dest.pack()

        tk.Label(win, text="Valor:").pack()
        val = tk.Entry(win, width=50)
        val.pack()

        tk.Label(win, text="Descrição (opcional):").pack()
        meta = tk.Entry(win, width=50)
        meta.pack()

        def enviar():
            try:
                receiver = dest.get()
                value = float(val.get())
                metadata = meta.get() if meta.get() != "" else None
                messagebox.showinfo("Valor total", f"Valor + taxas: {Decimal(value + b.adjust_mining_fees()):.8f} B$")
                if (value + b.adjust_mining_fees()) > b.get_balance(self.wallet.address):
                    messagebox.showerror("Erro", "Saldo insuficiente!")
                    return

                tr = Transaction(self.wallet.address, receiver, value, b.adjust_mining_fees(), None,
                                 chave_publica_para_json(self.wallet.public_key), metadata)
                sign = assinar_hash(self.wallet.private_key, tr.hash)
                tr.signature = assinatura_para_json(sign)
                b.add_transaction_to_pending(tr)
                threading.Thread(target=self.node.broadcast_pending).start()
                messagebox.showinfo("Sucesso", "Transação adicionada!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(win, text="Enviar", command=enviar).pack(pady=10)
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()
        if b.chain_is_valid(): pass
        else:
            messagebox.showinfo("Erro", f"Blockchain inválido! Removendo...")
            os.remove(b.chain_path)
            b.chain = []

    def minerar_balue(self):
        if b.chain:
            if not b.pending_block or b.pending_block[0].index == b.chain[-1]["index"]:
                messagebox.showerror("Erro", "Não há bloco pendente.")
                return

        messagebox.showinfo("Minerando", "Mineração iniciada...")

        def minerar():
            result = self.miner.mine()
            if result:
                self.update_balance()
                self.node.broadcast_chain()
                messagebox.showinfo("Sucesso", "Bloco minerado com sucesso!")
            else:
                messagebox.showerror("Erro", "Falha na mineração.")

        threading.Thread(target=minerar).start()
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()
        if b.chain_is_valid(): pass
        else:
            messagebox.showinfo("Erro", f"Blockchain inválido! Removendo...")
            os.remove(b.chain_path)
            b.chain = []

    def ver_blocos(self):
        ultimos_blocos = b.chain[-5:] if len(b.chain) >= 5 else b.chain
        blocos_texto = "\n\n".join([f"Índice: {blk['index']}, Hash: {blk['hash'][:10]}... \n  com {len(blk['transactions'])} transações \n ~~~~~~~~~~~~~~~~~~~~~" for blk in ultimos_blocos])
        messagebox.showinfo("Últimos Blocos", blocos_texto or "Sem blocos.")
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()

    def adicionar_peer(self):
        win = tk.Toplevel(self.root)
        win.title("Adicionar Peer")

        tk.Label(win, text="IP:").pack()
        ip = tk.Entry(win)
        ip.pack()

        tk.Label(win, text="Porta:").pack()
        port = tk.Entry(win)
        port.pack()

        def add():
            try:
                self.node.add_peer(ip.get(), int(port.get()))
                messagebox.showinfo("Adicionado", "Peer adicionado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(win, text="Adicionar", command=add).pack(pady=10)
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()

    def consultar_ip_porta(self):
        msg = f"IP Local: {self.node.local_ip}\nIP Público: {self.node.public_ip}\nPorta: {self.node.port}"
        messagebox.showinfo("IP e Porta", msg)
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()

    def ver_transacoes(self):
        txs = ''
        for block in b.chain:
            for tr in block["transactions"]:
                if tr["receiver"] == self.wallet.address and tr["metadata"] != "0":
                    txs += f'\nBloco: {block["index"]}, transação: {tr["hash"][:8]}... em {b.formatar_timestamp(tr["timestamp"])}  \n descrição: "{tr["metadata"]}" de: {tr["sender"]} \n ~~~~~~~~~~~~~~~~~~~~~ \n'
        messagebox.showinfo("Transações", txs or "Nenhuma transação encontrada.")
        thread_request_chain = threading.Thread(target=self.node.request_chain)
        thread_request_chain.start()
        thread_peers = threading.Thread(target=self.node.broadcast_peers)
        thread_peers.start()

    def update_balance(self):
        self.consultar_saldo()
        self.root.after(15000, self.update_balance)  # Atualiza a cada 15 segundos

# Executar app
if __name__ == "__main__":
    root = tk.Tk()
    app = BalueApp(root)
    root.mainloop()
