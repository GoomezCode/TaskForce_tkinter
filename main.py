"""TaskForce Tkinter client for the TaskForce API v2 (`/api/v1/tasks`).

Run:
    python main.py
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Optional

import config
from api.client import ApiError, TaskForceClient

FILTER_OPTIONS = ("Todas", "Pendentes", "Concluídas")
PAGE_SIZE_OPTIONS = ("10", "20", "50")


def _filter_to_is_done(label: str) -> Optional[bool]:
    if label == "Concluídas":
        return True
    if label == "Pendentes":
        return False
    return None


class EditDialog(tk.Toplevel):
    """Modal dialog to edit a task title."""

    def __init__(self, parent: tk.Misc, initial: str, on_save: Callable[[str], None]):
        super().__init__(parent)
        self.title("Editar tarefa")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self._on_save = on_save

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Título da tarefa:").pack(anchor="w")
        self.entry = ttk.Entry(frame, width=45, font=("Arial", 12))
        self.entry.insert(0, initial)
        self.entry.pack(pady=(6, 12))
        self.entry.focus_set()
        self.entry.select_range(0, tk.END)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Salvar", command=self._save).pack(side="right", padx=(0, 8))
        self.entry.bind("<Return>", lambda _e: self._save())
        self.bind("<Escape>", lambda _e: self.destroy())

    def _save(self) -> None:
        title = self.entry.get().strip()
        if not title:
            messagebox.showwarning("Título vazio", "O título não pode ficar em branco.", parent=self)
            return
        self.destroy()
        self._on_save(title)


class TaskForceApp:
    def __init__(self) -> None:
        self.client = TaskForceClient(base_url=config.API_URL, timeout=config.TIMEOUT)
        self.page = 1
        self.size = config.PAGE_SIZE
        self.total_pages = 0
        self._busy = False
        self._pending_msg: Optional[str] = None

        self.window = tk.Tk()
        self.window.title("TaskForce")
        self.window.geometry("800x600")
        self.window.minsize(640, 480)
        self._build_layout()
        self.refresh_all()

    # -- layout ------------------------------------------------------
    def _build_layout(self) -> None:
        self.window.columnconfigure(0, weight=1)

        header = ttk.Frame(self.window, padding=(12, 12, 12, 4))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="TaskForce", font=("Arial", 18, "bold")).grid(row=0, column=0, sticky="w")
        self.lbl_stats = ttk.Label(header, text="Total: — • Feitas: — • Pendentes: —")
        self.lbl_stats.grid(row=1, column=0, sticky="w", pady=(2, 0))

        create_bar = ttk.Frame(self.window, padding=(12, 4, 12, 4))
        create_bar.grid(row=1, column=0, sticky="ew")
        create_bar.columnconfigure(0, weight=1)
        self.entry_title = ttk.Entry(create_bar, font=("Arial", 12))
        self.entry_title.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_title.insert(0, "")
        self.entry_title.bind("<Return>", lambda _e: self.on_create())
        self.btn_create = ttk.Button(create_bar, text="Criar", command=self.on_create)
        self.btn_create.grid(row=0, column=1)

        toolbar = ttk.Frame(self.window, padding=(12, 4, 12, 4))
        toolbar.grid(row=2, column=0, sticky="ew")  # below create bar
        toolbar.columnconfigure(1, weight=1)
        ttk.Label(toolbar, text="Buscar:").grid(row=0, column=0, padx=(0, 4))
        self.entry_search = ttk.Entry(toolbar, font=("Arial", 11))
        self.entry_search.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.entry_search.bind("<Return>", lambda _e: self.on_search())
        self.cmb_filter = ttk.Combobox(toolbar, values=list(FILTER_OPTIONS), state="readonly", width=12)
        self.cmb_filter.set(FILTER_OPTIONS[0])
        self.cmb_filter.grid(row=0, column=2, padx=(0, 8))
        self.cmb_filter.bind("<<ComboboxSelected>>", lambda _e: self.on_search())
        ttk.Button(toolbar, text="Buscar", command=self.on_search).grid(row=0, column=3, padx=(0, 4))
        ttk.Button(toolbar, text="Limpar", command=self.on_clear_filters).grid(row=0, column=4)

        table_frame = ttk.Frame(self.window, padding=(12, 4, 12, 4))
        table_frame.grid(row=3, column=0, sticky="nsew")  # expandable
        self.window.rowconfigure(3, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("Id", "Tarefa", "Feito", "Data", "Hora")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        widths = {"Id": 60, "Tarefa": 320, "Feito": 80, "Data": 110, "Hora": 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], minwidth=widths[col] // 2, anchor="w" if col == "Tarefa" else "center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Double-1>", lambda _e: self.on_toggle())

        actions = ttk.Frame(self.window, padding=(12, 4, 12, 4))
        actions.grid(row=4, column=0, sticky="ew")
        self.btn_toggle = ttk.Button(actions, text="Marcar/Desmarcar", command=self.on_toggle)
        self.btn_toggle.pack(side="left", padx=(0, 6))
        self.btn_edit = ttk.Button(actions, text="Editar", command=self.on_edit)
        self.btn_edit.pack(side="left", padx=(0, 6))
        self.btn_delete = ttk.Button(actions, text="Deletar", command=self.on_delete)
        self.btn_delete.pack(side="left", padx=(0, 6))
        self.btn_refresh = ttk.Button(actions, text="Atualizar", command=self.refresh_all)
        self.btn_refresh.pack(side="left")

        pager = ttk.Frame(self.window, padding=(12, 0, 12, 4))
        pager.grid(row=5, column=0, sticky="ew")
        self.btn_prev = ttk.Button(pager, text="◀ Anterior", command=self.on_prev_page)
        self.btn_prev.pack(side="left")
        self.lbl_page = ttk.Label(pager, text="Página 1")
        self.lbl_page.pack(side="left", padx=10)
        self.btn_next = ttk.Button(pager, text="Próxima ▶", command=self.on_next_page)
        self.btn_next.pack(side="left")
        ttk.Label(pager, text="Itens/pág:").pack(side="left", padx=(16, 4))
        self.cmb_size = ttk.Combobox(pager, values=list(PAGE_SIZE_OPTIONS), state="readonly", width=5)
        self.cmb_size.set(str(self.size) if str(self.size) in PAGE_SIZE_OPTIONS else "20")
        self.cmb_size.pack(side="left")
        self.cmb_size.bind("<<ComboboxSelected>>", lambda _e: self.on_size_change())

        footer = ttk.Frame(self.window, padding=(12, 4, 12, 12))
        footer.grid(row=6, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.lbl_status = ttk.Label(footer, text="Pronto.", foreground="gray")
        self.lbl_status.grid(row=0, column=0, sticky="w")
        self.lbl_api = ttk.Label(footer, text=f"API: {self.client.base_url}", foreground="gray")
        self.lbl_api.grid(row=1, column=0, sticky="w")

    # -- threading helpers -------------------------------------------
    def _run_async(self, work: Callable[[], Any], done: Callable[[Any], None]) -> None:
        """Run blocking HTTP work off the UI thread, then call `done` via `after`."""

        def runner() -> None:
            try:
                result: Any = ("ok", work())
            except ApiError as exc:
                result = ("api-error", exc)
            except Exception as exc:  # defensive: never crash the worker silently
                result = ("api-error", ApiError(f"Erro inesperado: {exc}"))
            self.window.after(0, lambda: self._finish_async(result, done))

        threading.Thread(target=runner, daemon=True).start()

    def _finish_async(self, result: tuple[str, Any], done: Callable[[Any], None]) -> None:
        kind, payload = result
        self._set_busy(False)
        if kind == "api-error":
            assert isinstance(payload, ApiError)
            self.show_error(payload)
            return
        done(payload)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        for btn in (self.btn_create, self.btn_toggle, self.btn_edit,
                    self.btn_delete, self.btn_refresh, self.btn_prev, self.btn_next):
            btn.configure(state=state)
        if busy:
            self.lbl_status.configure(text="Carregando...", foreground="gray")

    # -- status / errors ----------------------------------------------
    def show_status(self, message: str, ok: bool = True) -> None:
        self.lbl_status.configure(text=message, foreground="green" if ok else "red")

    def show_error(self, error: ApiError) -> None:
        prefix = ""
        if error.status == 404:
            prefix = "Não encontrado: "
        elif error.status == 409:
            prefix = "Já existe: "
        elif error.status == 422:
            prefix = "Dados inválidos: "
        self.show_status(f"{prefix}{error.message}", ok=False)

    # -- data loading ---------------------------------------------------
    def refresh_all(self) -> None:
        if self._busy:
            return
        search = self.entry_search.get().strip()
        is_done = _filter_to_is_done(self.cmb_filter.get())
        page, size = self.page, self.size
        self._set_busy(True)

        def work() -> tuple[dict[str, Any], dict[str, Any]]:
            stats = self.client.stats()
            listing = self.client.list_tasks(
                search=search or None, is_done=is_done, page=page, size=size
            )
            return stats, listing

        def done(result: tuple[dict[str, Any], dict[str, Any]]) -> None:
            stats, listing = result
            self._on_stats_loaded(stats)
            self._on_page_loaded(listing)

        self._run_async(work, done)

    def _on_stats_loaded(self, stats: dict[str, Any]) -> None:
        total = stats.get("total", "—")
        done = stats.get("done", "—")
        pending = stats.get("pending", "—")
        self.lbl_stats.configure(text=f"Total: {total} • Feitas: {done} • Pendentes: {pending}")

    def _load_page(self) -> None:
        search = self.entry_search.get().strip()
        is_done = _filter_to_is_done(self.cmb_filter.get())
        page, size = self.page, self.size
        self._set_busy(True)
        self._run_async(
            lambda: self.client.list_tasks(search=search or None, is_done=is_done, page=page, size=size),
            self._on_page_loaded,
        )

    def _on_page_loaded(self, data: dict[str, Any]) -> None:
        items = data.get("items", [])
        total = int(data.get("total", 0))
        self.page = int(data.get("page", self.page))
        self.size = int(data.get("size", self.size))
        pages = int(data.get("pages", 0))
        self.total_pages = pages
        self.tree.delete(*self.tree.get_children())
        for item in items:
            self.tree.insert("", tk.END, values=(
                item.get("id", ""),
                item.get("tarefa", ""),
                "✔️" if item.get("feito") else "❌",
                item.get("data", ""),
                item.get("hora", ""),
            ))
        label = f"Página {self.page}/{pages}" if pages else f"Página {self.page} (total {total})"
        self.lbl_page.configure(text=label)
        self.btn_prev.configure(state="disabled" if self.page <= 1 else "normal")
        self.btn_next.configure(state="disabled" if (pages and self.page >= pages) else "normal")
        if self._pending_msg:
            self.show_status(self._pending_msg)
            self._pending_msg = None
        else:
            self.show_status(f"{total} tarefa(s) carregada(s).")

    # -- selection -------------------------------------------------------
    def _selected_id(self) -> Optional[int]:
        selection = self.tree.selection()
        if not selection:
            return None
        values = self.tree.item(selection[0], "values")
        try:
            return int(values[0])
        except (IndexError, TypeError, ValueError):
            return None

    def _require_selection(self) -> Optional[int]:
        task_id = self._selected_id()
        if task_id is None:
            self.show_status("Selecione uma tarefa na tabela.", ok=False)
        return task_id

    # -- actions ----------------------------------------------------------
    def on_create(self) -> None:
        if self._busy:
            return
        title = self.entry_title.get().strip()
        if not title:
            self.show_status("Digite o título da tarefa.", ok=False)
            return
        self._set_busy(True)
        self._run_async(
            lambda: self.client.create(title),
            lambda _task: (self.entry_title.delete(0, tk.END), self._after_mutation("Tarefa criada.")),
        )

    def on_toggle(self) -> None:
        if self._busy:
            return
        task_id = self._require_selection()
        if task_id is None:
            return
        self._set_busy(True)
        self._run_async(lambda: self.client.toggle_done(task_id),
                         lambda _t: self._after_mutation("Status alternado."))

    def on_delete(self) -> None:
        if self._busy:
            return
        task_id = self._require_selection()
        if task_id is None:
            return
        if not messagebox.askyesno("Confirmar", f"Deletar a tarefa #{task_id}?"):
            return
        self._set_busy(True)
        self._run_async(lambda: self.client.delete(task_id),
                         lambda _x: self._after_mutation("Tarefa deletada."))

    def on_edit(self) -> None:
        if self._busy:
            return
        task_id = self._require_selection()
        if task_id is None:
            return
        selection = self.tree.selection()
        current = self.tree.item(selection[0], "values")[1] if selection else ""

        def save(new_title: str) -> None:
            self._set_busy(True)
            self._run_async(lambda: self.client.update(task_id, title=new_title),
                             lambda _t: self._after_mutation("Tarefa atualizada."))

        EditDialog(self.window, str(current), save)

    def _after_mutation(self, message: str) -> None:
        """Show `message` after the automatic refresh finishes."""
        self._pending_msg = message
        self.refresh_all()

    def on_search(self) -> None:
        self.page = 1
        self._load_page()

    def on_clear_filters(self) -> None:
        self.entry_search.delete(0, tk.END)
        self.cmb_filter.set(FILTER_OPTIONS[0])
        self.page = 1
        self._load_page()

    def on_prev_page(self) -> None:
        if self.page > 1 and not self._busy:
            self.page -= 1
            self._load_page()

    def on_next_page(self) -> None:
        if self._busy:
            return
        if self.total_pages and self.page >= self.total_pages:
            return
        self.page += 1
        self._load_page()

    def on_size_change(self) -> None:
        try:
            self.size = max(1, min(int(self.cmb_size.get()), 100))
        except ValueError:
            self.size = config.PAGE_SIZE
        self.page = 1
        self._load_page()

    def run(self) -> None:
        self.window.mainloop()


if __name__ == "__main__":
    TaskForceApp().run()
