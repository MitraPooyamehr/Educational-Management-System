
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from Model.UserModel import User_Model_class
from Model.DepartmentModel import DepartmentModel
from BusinessLogicLayer.Department_CRUD_BLL import Department_CRUD_BLL


class DepartmentForm:
    def __init__(self, user_param: User_Model_class, master: tk.Misc = None):
        self.user = user_param
        self.master = master
        self.win = None
        self._created_root = False

        self.bll = Department_CRUD_BLL()

        self.id_var = None
        self.search_var = None

        self.var_department_name = None
        self.var_english_name = None

        self.tree = None
        self.context_menu = None

        self.btn_save = None
        self.btn_update = None
        self.btn_delete = None

        self.columns = ["ID", "Row", "DepartmentName", "EnglishDepartmentName"]

    # ---------- helpers ----------
    def _msg_parent(self):
        return self.win if (self.win is not None and self.win.winfo_exists()) else None

    def _set_selection_state(self, has_selection: bool):
        state = "normal" if has_selection else "disabled"
        if self.btn_update:
            self.btn_update.config(state=state)
        if self.btn_delete:
            self.btn_delete.config(state=state)

        if self.btn_save:
            self.btn_save.config(state="disabled" if has_selection else "normal")

    def _clear_form(self):
        self.id_var.set("")
        self.var_department_name.set("")
        self.var_english_name.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self._set_selection_state(False)

    def _validate(self) -> bool:
        dn = (self.var_department_name.get() or "").strip()
        en = (self.var_english_name.get() or "").strip()

        if not dn:
            messagebox.showerror("Validation", "DepartmentName is required.", parent=self._msg_parent())
            return False
        if not en:
            messagebox.showerror("Validation", "EnglishDepartmentName is required.", parent=self._msg_parent())
            return False
        if len(dn) > 50 or len(en) > 50:
            messagebox.showerror("Validation", "Max length is 50.", parent=self._msg_parent())
            return False

        return True

    # ---------- Context Menu ----------
    def _show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self._on_tree_select(None)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    # ---------- CRUD ----------
    def _save(self):
        if not self._validate():
            return

        dept = DepartmentModel(
            DepartmentName=self.var_department_name.get().strip(),
            EnglishDepartmentName=self.var_english_name.get().strip(),
        )

        try:
            new_id = self.bll.add_department(dept)
            if new_id <= 0:
                messagebox.showerror("Save", "Insert failed.", parent=self._msg_parent())
                return

            self.id_var.set(str(new_id))
            messagebox.showinfo("Saved", f"Department saved successfully. ID={new_id}", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()

        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())

    def _update(self):
        pid = (self.id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Update", "Select a row first.", parent=self._msg_parent())
            return

        if not self._validate():
            return

        try:
            dept = DepartmentModel(
                ID=int(pid),
                DepartmentName=self.var_department_name.get().strip(),
                EnglishDepartmentName=self.var_english_name.get().strip(),
            )
            self.bll.edit_department(dept)
            messagebox.showinfo("Updated", "Department updated successfully.", parent=self._msg_parent())
            self._refresh_tree()

        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())

    def _delete(self):
        pid = (self.id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Delete", "Select a row first.", parent=self._msg_parent())
            return

        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete Department ID={pid}?",
                                   parent=self._msg_parent()):
            return

        try:
            self.bll.remove_department(int(pid))
            messagebox.showinfo("Deleted", "Department deleted successfully.", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()

        except Exception as e:
            # مدیریت خطای Foreign Key اگر دپارتمان در جدول کارمندان استفاده شده باشد
            if "REFERENCE constraint" in str(e):
                msg = "Cannot delete this department because it is assigned to one or more employees."
                messagebox.showerror("Dependency Error", msg, parent=self._msg_parent())
            else:
                messagebox.showerror("DB Error", str(e), parent=self._msg_parent())

    # ---------- Tree/Search ----------
    def _refresh_tree(self):
        try:
            rows = self.bll.get_all()
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())
            return

        self.tree.delete(*self.tree.get_children())

        i = 1
        for r in rows:
            # SP: ID, DepartmentName, EnglishDepartmentName
            dept_id = r[0]
            dn = r[1]
            en = r[2]
            self.tree.insert("", "end", iid=str(dept_id), values=[dept_id, i, dn, en])
            i += 1

        if not (self.id_var.get() or "").strip():
            self._set_selection_state(False)

    def _search(self):
        q = (self.search_var.get() or "").strip()
        if not q:
            self._refresh_tree()
            return

        try:
            rows = self.bll.search(q)
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())
            return

        self.tree.delete(*self.tree.get_children())
        i = 1
        for r in rows:
            dept_id = r[0]
            dn = r[1]
            en = r[2]
            self.tree.insert("", "end", iid=str(dept_id), values=[dept_id, i, dn, en])
            i += 1

        self._set_selection_state(False)

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_tree()

    def _on_tree_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            self._clear_form()
            return

        item = self.tree.item(sel[0])
        values = item.get("values", [])
        if not values or len(values) < 4:
            self._clear_form()
            return

        dept_id = str(values[0]).strip()
        dn = str(values[2]).strip()
        en = str(values[3]).strip()

        self.id_var.set(dept_id)
        self.var_department_name.set(dn)
        self.var_english_name.set(en)

        self._set_selection_state(True)

    # ===================== UI =====================
    def department_form_load(self):
        try:
            # build window
            use_toplevel = False
            if self.master is not None:
                try:
                    use_toplevel = bool(self.master.winfo_exists())
                except Exception:
                    use_toplevel = False

            if use_toplevel:
                self.win = tk.Toplevel(self.master)
                self._created_root = False
            else:
                self.win = tk.Tk()
                self._created_root = True

            self.win.title("Department CRUD")
            self.win.configure(bg="#111111")

            self.win.update_idletasks()
            sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            W = max(1100, int(sw * 0.85))
            H = max(750, int(sh * 0.80))
            x = sw // 2 - W // 2
            y = sh // 2 - H // 2
            self.win.geometry(f"{W}x{H}+{x}+{y}")
            self.win.minsize(1100, 750)

            # vars
            self.id_var = tk.StringVar(master=self.win, value="")
            self.search_var = tk.StringVar(master=self.win, value="")
            self.var_department_name = tk.StringVar(master=self.win, value="")
            self.var_english_name = tk.StringVar(master=self.win, value="")

            # style
            style = ttk.Style(self.win)
            try:
                style.theme_use("clam")
            except Exception:
                pass

            font_sm = ("Segoe UI", 9)
            font_sm_b = ("Segoe UI", 9, "bold")
            font_title = ("Segoe UI Black", 16)

            style.configure("Root.TFrame", background="#111111")
            style.configure("Panel.TFrame", background="#1a1a1a")
            style.configure("Title.TLabel", background="#111111", foreground="white", font=font_title)
            style.configure("Info.TLabel", background="#111111", foreground="#bdbdbd", font=font_sm)
            style.configure("Form.TLabel", background="#1a1a1a", foreground="#e6e6e6", font=font_sm_b)
            style.configure("Value.TLabel", background="#1a1a1a", foreground="white", font=font_sm_b)

            style.configure("Form.TEntry", fieldbackground="#242424", background="#242424",
                            foreground="white", padding=4, font=font_sm)
            style.configure("Primary.TButton", padding=(10, 7), font=font_sm_b)

            style.configure("Treeview", background="#1f1f1f", fieldbackground="#1f1f1f",
                            foreground="white", rowheight=24, borderwidth=0, font=font_sm)
            style.configure("Treeview.Heading", background="#2a2a2a", foreground="white", font=font_sm_b)
            style.map("Treeview", background=[("selected", "#3a3a3a")])

            # root
            root = ttk.Frame(self.win, style="Root.TFrame")
            root.pack(fill="both", expand=True, padx=16, pady=16)

            # header
            header = ttk.Frame(root, style="Root.TFrame")
            header.pack(fill="x", pady=(0, 10))
            fn = (self.user.firstname or "").strip()
            ln = (self.user.lastname or "").strip()
            ttk.Label(header, text="Department Management", style="Title.TLabel").pack(side="left")
            ttk.Label(header, text=f"User: {fn} {ln}".strip(), style="Info.TLabel").pack(side="left", padx=(12, 0))

            ttk.Separator(root, orient="horizontal").pack(fill="x", pady=(0, 10))

            # paned
            paned = ttk.Panedwindow(root, orient="vertical")
            paned.pack(fill="both", expand=True)

            top_panel = ttk.Frame(paned, style="Panel.TFrame")
            bottom_panel = ttk.Frame(paned, style="Panel.TFrame")
            paned.add(top_panel, weight=2)
            paned.add(bottom_panel, weight=6)

            # toolbar
            toolbar = ttk.Frame(top_panel, style="Panel.TFrame")
            toolbar.pack(fill="x", padx=14, pady=(12, 8))

            ttk.Label(toolbar, text="Department ID:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(toolbar, textvariable=self.id_var, style="Value.TLabel").grid(row=0, column=1, padx=(8, 20),
                                                                                    sticky="w")

            self.btn_save = ttk.Button(toolbar, text="Save", style="Primary.TButton", command=self._save)
            self.btn_save.grid(row=0, column=2, padx=(0, 8))

            self.btn_update = ttk.Button(toolbar, text="Update", style="Primary.TButton", command=self._update)
            self.btn_update.grid(row=0, column=3, padx=(0, 8))

            self.btn_delete = ttk.Button(toolbar, text="Delete", style="Primary.TButton", command=self._delete)
            self.btn_delete.grid(row=0, column=4, padx=(0, 8))

            ttk.Button(toolbar, text="Clear", style="Primary.TButton", command=self._clear_form).grid(row=0, column=5,
                                                                                                      padx=(0, 8))
            ttk.Button(toolbar, text="Refresh", style="Primary.TButton", command=self._refresh_tree).grid(row=0,
                                                                                                          column=6,
                                                                                                          padx=(0, 8))
            ttk.Button(toolbar, text="Close", style="Primary.TButton", command=self.win.destroy).grid(row=0, column=7)

            self._set_selection_state(False)

            # fields
            fields = ttk.Frame(top_panel, style="Panel.TFrame")
            fields.pack(fill="x", padx=14, pady=(0, 14))
            fields.columnconfigure(0, weight=1)
            fields.columnconfigure(1, weight=1)

            # DepartmentName
            left = ttk.Frame(fields, style="Panel.TFrame")
            left.grid(row=0, column=0, sticky="ew", padx=(0, 15))

            ttk.Label(left, text="Department Name (Persian)", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Entry(left, textvariable=self.var_department_name, style="Form.TEntry", width=40).grid(
                row=1, column=0, sticky="w", pady=(4, 0)
            )

            # EnglishDepartmentName
            right = ttk.Frame(fields, style="Panel.TFrame")
            right.grid(row=0, column=1, sticky="ew")

            ttk.Label(right, text="English Department Name", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Entry(right, textvariable=self.var_english_name, style="Form.TEntry", width=40).grid(
                row=1, column=0, sticky="w", pady=(4, 0)
            )

            # bottom panel (Search + Tree)
            bottom_panel.pack_propagate(False)

            search = ttk.Frame(bottom_panel, style="Panel.TFrame")
            search.pack(fill="x", padx=14, pady=(12, 8))
            search.columnconfigure(1, weight=1)

            ttk.Label(search, text="Search Department:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ent_search = ttk.Entry(search, textvariable=self.search_var, style="Form.TEntry")
            ent_search.grid(row=0, column=1, sticky="ew", padx=(8, 10))
            ttk.Button(search, text="Search", style="Primary.TButton", command=self._search).grid(row=0, column=2,
                                                                                                  padx=(0, 8))
            ttk.Button(search, text="Clear", style="Primary.TButton", command=self._clear_search).grid(row=0, column=3)

            ent_search.bind("<Return>", lambda e: self._search())

            tree_frame = ttk.Frame(bottom_panel, style="Panel.TFrame")
            tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
            tree_frame.rowconfigure(0, weight=1)
            tree_frame.columnconfigure(0, weight=1)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

            self.tree = ttk.Treeview(
                tree_frame,
                columns=self.columns,
                show="headings",
                yscrollcommand=vsb.set,
                xscrollcommand=hsb.set
            )

            vsb.config(command=self.tree.yview)
            hsb.config(command=self.tree.xview)

            self.tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")

            # headings
            self.tree.heading("ID", text="ID")
            self.tree.heading("Row", text="Row")
            self.tree.heading("DepartmentName", text="DepartmentName")
            self.tree.heading("EnglishDepartmentName", text="EnglishDepartmentName")

            # hide ID column
            self.tree.column("ID", width=0, stretch=False)
            self.tree.column("Row", width=70, anchor="center")
            self.tree.column("DepartmentName", width=350, anchor="w")
            self.tree.column("EnglishDepartmentName", width=350, anchor="w")

            self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

            # --- ایجاد منوی کلیک راست (Context Menu) ---
            self.context_menu = tk.Menu(self.win, tearoff=0, bg="#1a1a1a", fg="white", font=font_sm)
            self.context_menu.add_command(label="Update Record", command=self._update)
            self.context_menu.add_command(label="Delete Record", command=self._delete)
            self.tree.bind("<Button-3>", self._show_context_menu)

            # fill data
            self._refresh_tree()

            if self._created_root:
                self.win.mainloop()

        except Exception as e:
            messagebox.showerror("Department Form Error", str(e), parent=self._msg_parent())