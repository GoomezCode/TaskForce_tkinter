<h1 align="center">🖥️ TaskForce Tkinter</h1>

<p align="center">Aplicação <b>desktop</b> desenvolvida em <b>Python + Tkinter</b> para gerenciar tarefas (to-do list), consumindo a [TaskForce API](https://github.com/GoomezCode/TaskForce_api) através de requisições HTTP.</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white">
    <img src="https://img.shields.io/badge/GUI-Tkinter-orange">
    <img src="https://img.shields.io/badge/Requests-2.34.2-lightgrey">
    <img src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## 🖼️ Preview da tela

<p align="center"><img src="./assets/preview.svg"></p>

> Representação ilustrativa da interface: campo de entrada para digitar a tarefa (ou o Id, dependendo da ação), botões de **Criar**, **Deletar** e **Marcar**, uma tabela (Treeview) listando as tarefas cadastradas e um label de feedback na parte inferior.

---

## 📌 Sobre o projeto

O **TaskForce Tkinter** é o cliente gráfico (front-end desktop) do projeto TaskForce. Ele não armazena nenhum dado localmente — toda a lógica de persistência acontece na **TaskForce API**, e esta aplicação apenas consome os endpoints via HTTP usando a biblioteca `requests`.

Funcionalidades:

- ✅ Criar novas tarefas
- ✅ Listar tarefas em uma tabela organizada (Id, Tarefa, Feito)
- ✅ Marcar/desmarcar tarefas como concluídas
- ✅ Deletar tarefas
- ✅ Feedback visual das operações (mensagens de sucesso/erro)

---

## 🚀 Tecnologias utilizadas

- [Python 3](https://www.python.org/)
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — biblioteca padrão do Python para GUI
- [ttk (Treeview)](https://docs.python.org/3/library/tkinter.ttk.html) — componente de tabela
- [Requests](https://requests.readthedocs.io/) — comunicação HTTP com a API

---

## 🔗 Projeto relacionado

Esta aplicação depende da API abaixo estar no ar para funcionar:

- 🔌 [TaskForce API](https://github.com/GoomezCode/TaskForce_api) — back-end em FastAPI responsável por criar, listar, marcar e deletar as tarefas.

---

## 📂 Estrutura do projeto

```
TaskForce_tkinter/
├── util/
│   └── utilTask.py       # Funções que se comunicam com a API (GET, POST, PUT, DELETE)
├── main.py                # Interface gráfica (Tkinter) e lógica da aplicação
├── requirements.txt        # Dependências do projeto
└── README.md
```

---

## ⚙️ Como executar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/GoomezCode/TaskForce_tkinter.git
cd TaskForce_tkinter
```

### 2. Crie e ative um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a URL da API (se necessário)

Por padrão, a aplicação já aponta para a API hospedada:

```python
# util/utilTask.py
url = "https://taskforce-api-zxag.onrender.com/task"
```

Se você estiver rodando sua própria instância da API (por exemplo, localmente), atualize essa URL para o endereço correto (ex: `http://localhost:8000/task`).

> ⚠️ Se a API estiver hospedada no plano gratuito do Render, o primeiro acesso após um período de inatividade pode demorar alguns segundos (cold start) — isso é esperado.

### 5. Execute a aplicação

```bash
python main.py
```

Uma janela do Tkinter será aberta com a interface do TaskForce.

---

## 🕹️ Como usar

| Ação | Como fazer |
|---|---|
| **Criar tarefa** | Digite o nome da tarefa no campo de texto e clique em **Criar** |
| **Marcar como concluída** | Digite o **Id** da tarefa no campo de texto e clique em **Marcar** |
| **Deletar tarefa** | Digite o **Id** da tarefa no campo de texto e clique em **Deletar** |

A tabela é atualizada automaticamente após cada ação, e a mensagem na parte inferior da tela informa se a operação foi bem-sucedida ou se ocorreu algum erro.

---

## 🛠️ Melhorias futuras

- [ ] Substituir o campo único de entrada por campos separados para nome da tarefa e Id
- [ ] Adicionar confirmação antes de deletar uma tarefa
- [ ] Adicionar edição do texto de uma tarefa já criada
- [ ] Melhorar o tratamento de erros de conexão com a API (ex: quando ela está "dormindo" no Render)
- [ ] Permitir configurar a URL da API por variável de ambiente/arquivo de configuração

---

## 👤 Autor

Desenvolvido por [**GoomezCode**](https://github.com/GoomezCode).