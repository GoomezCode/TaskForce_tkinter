import tkinter as tk
from tkinter import ttk
from util import utilTask

class main:
    def __init__(self):
        self.window = tk.Tk()
        x,y = 450,400
        self.window.title("TaskForce")
        self.window.geometry(f"{x}x{y}")
        self.window.resizable(0,0)
        self.dados = utilTask.getTask()


        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)


        self.title = tk.Label(
            self.window,
            text="TaskForce Tkinter",
            font=("Arial", 16, "bold")
        ).grid(row=0, columnspan=3)

        self.entry = tk.Entry(
            self.window,
            font=("Arial", 15)
        )
        self.entry.grid(row=1, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.btn_criar = tk.Button(
            self.window,
            text="Criar",
            font=("Arial", 12, "bold"),
            command=lambda:self.criar_task(self.entry.get())
        ).grid(row=2, column=0)

        self.btn_deletar = tk.Button(
            self.window,
            text="Deletar",
            font=("Arial", 12, "bold"),
            command=lambda:self.deletar_task(self.entry.get())
        ).grid(row=2, column=1)

        self.btn_marcar = tk.Button(
            self.window,
            text="Marcar",
            font=("Arial", 12, "bold"),
            command=lambda:self.marcar_task(self.entry.get())
        ).grid(row=2, column=2, padx=30)

        # --------{ Configuração da treeview }-----------------------------------
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 13, "bold"))
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

        
        colunas = ("Id", "Tarefa", "Feito")
        self.list = ttk.Treeview(
            self.window,
            columns=colunas,
            show="headings",
            style="Treeview"   
        )
        self.list.column("Id", width=10, minwidth=10)
        self.list.column("Tarefa", width=150, minwidth=150)
        self.list.column("Feito", width=10, minwidth=10)

        for col in colunas:
            self.list.heading(col, text=col)

        self.list.grid(row=3, columnspan=3, sticky="nsew", pady=10)
        self.update_list()
        # -------------------------------------------

        self.lbl_info = tk.Label(
            self.window,
            text="",
            font=("Arial", 15, "bold")
        )
        self.lbl_info.grid(row=4, columnspan=3, sticky="nsew")

        self.window.mainloop()
    
    def update_list(self):
        self.dados = utilTask.getTask()
        self.list.delete(*self.list.get_children())
        for i in self.dados:
            self.list.insert("", tk.END, values=(i["id"], i["tarefa"], "✔️" if i["feito"] == True else "❌" ))
        
    def info_msg(self, response):
        msg = response.json()["detail"]
        status_code = response.status_code

        if status_code == 200:
            self.lbl_info.config(text=msg, fg="green", font=("Arial", 12))
        elif status_code == 422:
            self.lbl_info.config(text="Erro: coloque o Id para alterar", fg="red", font=("Arial", 12))
        else:
            self.lbl_info.config(text=msg, fg="red")

    def deletar_task(self, idTask):
        response = utilTask.deleteTask(idTask)
        self.info_msg(response)
        self.update_list()

    def criar_task(self, nmTarefa):
        response = utilTask.createTask(nmTarefa)
        self.info_msg(response)
        self.update_list()
    
    def marcar_task(self, idTask):
        response = utilTask.marcarTask(idTask)
        self.info_msg(response)
        self.update_list()

main()