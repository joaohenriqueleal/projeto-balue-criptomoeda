import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from p2p_protocol.node import *
from decimal import Decimal
from datetime import datetime, timezone
import threading


class BalueTkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Balue: Um novo sistema de pagamento P2P")
        self.root.geometry("800x600")

        # Initialize wallet and node
        self.wallet = Wallet(True)
        self.miner = Miner(self.wallet.private_key, self.wallet.public_key, self.wallet.address)
        self.node = Node(8888)

        # Start background threads
        threading.Thread(target=self.node.request_chain).start()
        threading.Thread(target=self.node.broadcast_peers).start()

        self.create_menu_bar()
        self.create_main_content()
        self.update_balance()

        if not chain_state.chain_is_valid():
            while not chain_state.chain_is_valid():
                os.remove(f'balue/chain/{len(chain_state.chain) - 1}.json')
                chain_state.chain.pop()

    def create_menu_bar(self):
        # Create main menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Sair", command=self.sair)

        # Wallet menu
        wallet_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Carteira", menu=wallet_menu)
        wallet_menu.add_command(label="Consultar saldo", command=self.consultar_saldo)
        wallet_menu.add_command(label="Consultar endereço", command=self.consultar_endereco)
        wallet_menu.add_separator()
        wallet_menu.add_command(label="Transferir Balue", command=self.transferir_balue)

        # Mining menu
        mining_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Mineração", menu=mining_menu)
        mining_menu.add_command(label="Minerar Bloco", command=self.minerar_balue)
        mining_menu.add_command(label="Adicionar Bloco Pendente", command=self.adicionar_bloco_pendente)

        # Network menu
        network_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Rede", menu=network_menu)
        network_menu.add_command(label="Consultar IP e Porta", command=self.consultar_ip_porta)
        network_menu.add_command(label="Adicionar Peer", command=self.adicionar_peer)
        network_menu.add_command(label="Ver Peers Conhecidos", command=self.ver_peers)

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Últimos Blocos", command=self.ver_ultimos_blocos)
        view_menu.add_command(label="Transações Recebidas", command=self.ver_descricoes_transacoes)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.mostrar_sobre)

    def create_main_content(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text="Balue: Um novo sistema de pagamento P2P",
                  font=('Helvetica', 14, 'bold')).pack()

        # Balance and address display
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.X, pady=10)

        self.balance_var = tk.StringVar()
        self.balance_label = ttk.Label(info_frame, textvariable=self.balance_var,
                                       font=('Helvetica', 12))
        self.balance_label.pack(anchor=tk.W)

        self.address_var = tk.StringVar(value=f"Endereço Balue: {self.wallet.address}")
        self.address_label = ttk.Label(info_frame, textvariable=self.address_var,
                                       font=('Helvetica', 12))
        self.address_label.pack(anchor=tk.W)

        # Copy address buttonamo
        ttk.Button(info_frame, text="Copiar Endereço", command=self.copy_address).pack(pady=5)

        # Separator
        ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(self.main_frame, textvariable=self.status_var,
                  relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)

        # Recent transactions/block area
        self.create_recent_activity_area()

    def create_recent_activity_area(self):
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Recent transactions tab
        trans_frame = ttk.Frame(notebook)
        self.trans_text = scrolledtext.ScrolledText(trans_frame, wrap=tk.WORD)
        self.trans_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(trans_frame, text="Transações Recentes")

        # Recent blocks tab
        blocks_frame = ttk.Frame(notebook)
        self.blocks_text = scrolledtext.ScrolledText(blocks_frame, wrap=tk.WORD)
        self.blocks_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(blocks_frame, text="Blocos Recentes")

        # Update content
        self.update_recent_activity()

    def update_recent_activity(self):
        # Update transactions
        self.trans_text.config(state=tk.NORMAL)
        self.trans_text.delete(1.0, tk.END)

        transactions_found = False
        for i in range(len(chain_state.chain[-5:][::-1])):  # Last 5 blocks, newest first
            blk = chain_state.load_block(i)
            for tr in blk["transactions"][::-1]:  # Reverse order to show newest first
                if tr["receiver"] == self.wallet.address:
                    transactions_found = True
                    timestamp_s = tr["timestamp"] / 1_000_000_000
                    dt = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)

                    self.trans_text.insert(tk.END, f"Bloco #{blk['index']} - {dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    self.trans_text.insert(tk.END, f"De: {tr['sender'][:10]}...\n")
                    self.trans_text.insert(tk.END, f"Valor: {tr['value']:.8f} B$\n")
                    if tr["metadata"] != "0":
                        self.trans_text.insert(tk.END, f"Descrição: {tr['metadata']}\n")
                    self.trans_text.insert(tk.END, "-" * 50 + "\n\n")

        if not transactions_found:
            self.trans_text.insert(tk.END, "Nenhuma transação recente encontrada.")
        self.trans_text.config(state=tk.DISABLED)

        # Update blocks
        self.blocks_text.config(state=tk.NORMAL)
        self.blocks_text.delete(1.0, tk.END)

        for i in range(0, len(chain_state.chain[-10:][::-1])):  # Last 10 blocks, newest first
            blk = chain_state.load_block(i)
            self.blocks_text.insert(tk.END, f"Bloco #{blk['index']}\n")
            self.blocks_text.insert(tk.END, f"Hash: {blk['hash'][:10]}...{blk['hash'][-10:]}\n")
            self.blocks_text.insert(tk.END, f"Transações: {len(blk['transactions'])}\n")
            timestamp_s = blk["timestamp"] / 1_000_000_000
            dt = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
            self.blocks_text.insert(tk.END, f"Data: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.blocks_text.insert(tk.END, "-" * 50 + "\n\n")

        if chain_state.pending_block:
            self.blocks_text.insert(tk.END, "\nBLOCO PENDENTE:\n")
            self.blocks_text.insert(tk.END, f"Bloco #{chain_state.pending_block[0].index}\n")
            self.blocks_text.insert(tk.END, f"Transações: {len(chain_state.pending_block[0].transactions)}\n")

        self.blocks_text.config(state=tk.DISABLED)

        # Schedule next update
        self.root.after(1000, self.update_recent_activity)

    def copy_address(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.wallet.address)
        self.status_var.set("Endereço copiado para a área de transferência!")
        self.root.after(3000, lambda: self.status_var.set("Pronto"))

    def update_balance(self):
        balance = round(Decimal(chain_state.get_balance(self.wallet.address)), 8)
        self.balance_var.set(f"Saldo Balue: {balance:.8f} B$")
        self.root.after(5000, self.update_balance)

    def mostrar_sobre(self):
        messagebox.showinfo("Sobre Balue", "Balue: Um novo sistema de pagamento P2P\nVersão Alpha. Está versão"
            " é experimental e aberta para modificações, forks de código e propostas de melhoria por parte da comunidade técnica.")

    def consultar_saldo(self):
        balance = round(Decimal(chain_state.get_balance(self.wallet.address)), 8)
        self.balance_var.set(f"Saldo Balue: {balance:.8f} B$")
        messagebox.showinfo("Saldo", f"Saldo Balue: {balance:.8f} B$")
        threading.Thread(target=self.node.request_chain).start()

    def consultar_endereco(self):
        messagebox.showinfo("Endereço Balue", f"Endereço Balue: {self.wallet.address}")
        threading.Thread(target=self.node.request_chain).start()

    def transferir_balue(self):
        transfer_window = tk.Toplevel(self.root)
        transfer_window.title("Transferir Balue")
        transfer_window.geometry("500x300")

        ttk.Label(transfer_window, text="Endereço balue do destinatário:").pack(pady=(10, 0))
        destino_entry = ttk.Entry(transfer_window, width=50)
        destino_entry.pack()

        ttk.Label(transfer_window, text="Valor da transação (B$):").pack(pady=(10, 0))
        valor_entry = ttk.Entry(transfer_window)
        valor_entry.pack()

        ttk.Label(transfer_window, text="Descrição (opcional):").pack(pady=(10, 0))
        descricao_entry = ttk.Entry(transfer_window, width=50)
        descricao_entry.pack()

        def confirmar_transferencia():
            try:
                destino = destino_entry.get().strip()
                valor = float(valor_entry.get())
                descricao = descricao_entry.get().strip() or "0"

                if len(descricao) > 80:
                    messagebox.showerror("Erro",
                                         f"Descrição muito grande! Max de 80 caractéres.")
                    return

                if valor == 0:
                    messagebox.showerror("Erro",
                                         f"Valor da transação deve ser acima de zero!")
                    return

                fees = chain_state.calculate_fees(valor)
                total = valor + fees

                if total > chain_state.get_balance(self.wallet.address):
                    messagebox.showerror("Erro",
                                         f"Saldo insuficiente!\nValor + Taxas: {total:.8f} B$\nSeu saldo: {chain_state.get_balance(self.wallet.address):.8f} B$")
                    return

                confirm = messagebox.askyesno("Confirmar",
                                              f"O valor mais as taxas ficará: {total:.8f} B$\nConfirmar transferência?")
                if len(chain_state.pending_block) > 0:
                    if len(chain_state.pending_block[0].transactions) + 1 > chain_state.max_transactions_per_block:
                        messagebox.showerror("Erro",
                                             f"Bloco pendente está cheio!")
                        return
                if confirm:
                    chain_state.new_pending_block()
                    t = Transaction(
                        self.wallet.address,
                        destino,
                        valor,
                        fees,
                        chave_publica_para_json(self.wallet.public_key),
                        descricao,
                        chain_state.transactions_difficulty()
                    )
                    t.signature = assinatura_para_json(assinar_hash(self.wallet.private_key, t.hash))
                    chain_state.add_transaction_to_pending(t)

                    messagebox.showinfo("Sucesso", "Transação adicionada com sucesso!")
                    transfer_window.destroy()
                    self.update_balance()
                    thread_broadcast_pending = threading.Thread(target=self.node.broadcast_pending_block)
                    thread_broadcast_pending.start()
            except ValueError:
                messagebox.showerror("Erro", "Digite um valor válido!")

        ttk.Button(transfer_window, text="Transferir", command=confirmar_transferencia).pack(pady=20)

    def minerar_balue(self):
        if not chain_state.pending_block:
            messagebox.showerror("Erro", "Não há bloco pendente!")
            return
        if len(chain_state.pending_block[0].transactions) < chain_state.min_transactions_block(chain_state.pending_block[0].index):
            messagebox.showerror("Erro", "O bloco não atingiu quantidade de transações suficiente!")
            return

        start_time = datetime.now()
        messagebox.showinfo("Mineração",
                            f"⛏️ Mineração iniciada em: {start_time.strftime('%y-%m-%d %H:%M:%S')}\nDificuldade: {chain_state.pending_block[0].difficulty}")

        def mine():
            resultado = self.miner.mine()

            if resultado:
                end_time = datetime.now()
                messagebox.showinfo("Sucesso",
                                    f"⛏️ Mineração terminada em: {end_time.strftime('%y-%m-%d %H:%M:%S')}\n"
                                    f"Recompensa de: {chain_state.load_block(len(chain_state.chain) - 1)['reward']} B$ adicionada!\n"
                                    f"Novo saldo: {round(Decimal(chain_state.get_balance(self.wallet.address)), 8):.8f} B$")

                threading.Thread(target=self.node.broadcast_last_block).start()
                self.update_balance()
            else:
                messagebox.showerror("Erro", "Bloco minerado é inválido! Sem recompensas!")

        threading.Thread(target=mine).start()

    def consultar_ip_porta(self):
        self.node.peer_infos()
        info = f"IP público: {self.node.public_ip}\nIP local: {self.node.local_ip}\nPorta: {self.node.port}"
        messagebox.showinfo("Informações do Node", info)
        threading.Thread(target=self.node.request_chain).start()

    def adicionar_peer(self):
        peer_window = tk.Toplevel(self.root)
        peer_window.title("Adicionar Peer")
        peer_window.geometry("400x200")

        ttk.Label(peer_window, text="IP do peer:").pack(pady=(10, 0))
        ip_entry = ttk.Entry(peer_window)
        ip_entry.pack()

        ttk.Label(peer_window, text="PORTA do peer:").pack(pady=(10, 0))
        port_entry = ttk.Entry(peer_window)
        port_entry.pack()

        def adicionar():
            try:
                ip = ip_entry.get().strip()
                port = int(port_entry.get())

                if self.node.add_peer(ip, port):
                    threading.Thread(target=self.node.broadcast_peers).start()
                    messagebox.showinfo("Sucesso", "Node adicionado com sucesso!")
                    peer_window.destroy()
                else:
                    messagebox.showerror("Erro", "Node inválido!")
            except ValueError:
                messagebox.showerror("Erro", "Digite uma porta válida!")

        ttk.Button(peer_window, text="Adicionar", command=adicionar).pack(pady=20)

    def ver_descricoes_transacoes(self):
        text_window = tk.Toplevel(self.root)
        text_window.title("Descrições de Transações")
        text_window.geometry("700x500")

        text_area = scrolledtext.ScrolledText(text_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)

        transactions_found = False

        for i in range(0, len(chain_state.chain)):
            blk = chain_state.load_block(i)
            for tr in blk["transactions"]:
                if tr["receiver"] == self.wallet.address and tr["metadata"] != "0":
                    transactions_found = True
                    timestamp_s = tr["timestamp"] / 1_000_000_000
                    dt = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)

                    text_area.insert(tk.END, f"Em:  {dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    text_area.insert(tk.END, f"De:  {tr['sender']}\n")
                    text_area.insert(tk.END, f"Descrição:  {tr['metadata']}\n")
                    text_area.insert(tk.END, "~" * 60 + "\n\n")

        if not transactions_found:
            text_area.insert(tk.END, "Nenhuma transação com descrição encontrada.")

        text_area.config(state=tk.DISABLED)
        threading.Thread(target=self.node.request_chain).start()

    def ver_ultimos_blocos(self):
        text_window = tk.Toplevel(self.root)
        text_window.title("Últimos Blocos")
        text_window.geometry("700x500")

        text_area = scrolledtext.ScrolledText(text_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)

        text_area.insert(tk.END, "Últimos 10 blocos da rede + o pendente:\n\n")

        for i in range(0, len(chain_state.chain[-10:])):
            blk = chain_state.load_block(i)
            text_area.insert(tk.END, f"Bloco #{blk['index']}, Hash:  {blk['hash'][:10]}...{blk['hash'][10:25]}...\n")
            text_area.insert(tk.END, f"      com {len(blk['transactions'])} transações.\n")
            text_area.insert(tk.END, "~" * 60 + "\n\n")

        if chain_state.pending_block:
            text_area.insert(tk.END, "=" * 60 + "\n")
            text_area.insert(tk.END, f"Bloco pendente #{chain_state.pending_block[0].index}\n")
            text_area.insert(tk.END, f"      com {len(chain_state.pending_block[0].transactions)} transações.\n")

        text_area.config(state=tk.DISABLED)
        threading.Thread(target=self.node.request_chain).start()

    def adicionar_bloco_pendente(self):
        if chain_state.new_pending_block():
            messagebox.showinfo("Sucesso", "Novo bloco pendente adicionado!")
            threading.Thread(target=self.node.broadcast_pending_block).start()
        else:
            messagebox.showerror("Erro", "Há um bloco pendente a ser minerado!")
        threading.Thread(target=self.node.request_chain).start()
        thread_broadcast_pending = threading.Thread(target=self.node.broadcast_pending_block)
        thread_broadcast_pending.start()

    def ver_peers(self):
        text_window = tk.Toplevel(self.root)
        text_window.title("Peers Conhecidos")
        text_window.geometry("400x300")

        text_area = scrolledtext.ScrolledText(text_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)

        text_area.insert(tk.END, "PEERS CONHECIDOS:\n\n")

        for peer in self.node.peers:
            text_area.insert(tk.END, f"Endereço:  {peer['ip']}:{peer['port']}\n")
            text_area.insert(tk.END, "~" * 47 + "\n")

        if not self.node.peers:
            text_area.insert(tk.END, "Nenhum peer conhecido.")

        text_area.config(state=tk.DISABLED)
        threading.Thread(target=self.node.request_chain).start()

    def sair(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do Balue?"):
            self.root.destroy()


if __name__ == "__main__":
    if chain_state.chain_is_valid():
        root = tk.Tk()
        app = BalueTkinterApp(root)
        root.mainloop()
    else:
        while not chain_state.chain_is_valid():
            os.remove(f'balue/chain/{len(chain_state.chain) - 1}.json')
            chain_state.chain.pop()
            chain_state.save_chain()
        root = tk.Tk()
        app = BalueTkinterApp(root)
        root.mainloop()
