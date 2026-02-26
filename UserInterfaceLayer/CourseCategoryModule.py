

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from Model.UserModel import User_Model_class
from Model.CourseCategoryModel import CourseCategory_Model_Class
from BusinessLogicLayer.CourseCategory_CRUD_BLL import CourseCategory_CRUD_BLL_Class


class CourseCategoryForm:
    def __init__(self, user_param: User_Model_class, master: tk.Misc = None):
        self.user = user_param
        self.master = master
        self.win = None
        self._created_root = False

        self.bll = CourseCategory_CRUD_BLL_Class()

        self.search_var = None
        self.category_id_var = None

        self.var_name = None
        self.var_english_name = None

        self.btn_update = None
        self.btn_delete = None
        self.btn_save = None

        self.tree = None
        self.context_menu = None

    # ---------- helpers ----------
    def _msg_parent(self):
        return self.win if (self.win is not None and self.win.winfo_exists()) else None

    def _set_selection_state(self, has_selection: bool):
        state = ("normal" if has_selection else "disabled")
        if self.btn_update:
            self.btn_update.config(state=state)
        if self.btn_delete:
            self.btn_delete.config(state=state)

        if self.btn_save:
            self.btn_save.config(state="disabled" if has_selection else "normal")

    def _clear_form(self):
        self.category_id_var.set("")
        self.var_name.set("")
        self.var_english_name.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self._set_selection_state(False)

    def _validate_form(self) -> bool:
        name = (self.var_name.get() or "").strip()
        en = (self.var_english_name.get() or "").strip()

        if not name:
            messagebox.showerror("Validation", "CourseCategoryName is required.", parent=self._msg_parent())
            return False
        if not en:
            messagebox.showerror("Validation", "EnglishCourseCategoryName is required.", parent=self._msg_parent())
            return False

        if len(name) > 50:
            messagebox.showerror("Validation", "CourseCategoryName max length is 50.", parent=self._msg_parent())
            return False
        if len(en) > 50:
            messagebox.showerror("Validation", "EnglishCourseCategoryName max length is 50.", parent=self._msg_parent())
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
        if not self._validate_form():
            return

        obj = CourseCategory_Model_Class(
            ID=None,
            CourseCategoryName=(self.var_name.get() or "").strip(),
            EnglishCourseCategoryName=(self.var_english_name.get() or "").strip()
        )

        try:
            new_id = self.bll.register_course_category(obj)
            if new_id <= 0:
                messagebox.showerror("Error", "Failed to register category.", parent=self._msg_parent())
                return

            messagebox.showinfo("Saved", f"Category registered successfully. ID={new_id}", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()

        except Exception as e:
            messagebox.showerror("Save Error", str(e), parent=self._msg_parent())

    def _update(self):
        cid = (self.category_id_var.get() or "").strip()
        if not cid:
            messagebox.showwarning("Update", "Select a row first.", parent=self._msg_parent())
            return

        if not self._validate_form():
            return

        try:
            obj = CourseCategory_Model_Class(
                ID=int(cid),
                CourseCategoryName=(self.var_name.get() or "").strip(),
                EnglishCourseCategoryName=(self.var_english_name.get() or "").strip()
            )
            self.bll.update_course_category(obj)
            messagebox.showinfo("Updated", "Category updated successfully.", parent=self._msg_parent())
            self._refresh_tree()

        except Exception as e:
            messagebox.showerror("Update Error", str(e), parent=self._msg_parent())

    def _delete(self):
        cid = (self.category_id_var.get() or "").strip()
        if not cid:
            messagebox.showwarning("Delete", "Select a row first.", parent=self._msg_parent())
            return

        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete Category ID={cid}?",
                                   parent=self._msg_parent()):
            return

        try:
            self.bll.delete_course_category(int(cid))
            messagebox.showinfo("Deleted", "Category deleted successfully.", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()

        except Exception as e:
            if "REFERENCE constraint" in str(e):
                msg = "Cannot delete this category because it is being used by one or more courses."
                messagebox.showerror("Dependency Error", msg, parent=self._msg_parent())
            else:
                messagebox.showerror("Delete Error", str(e), parent=self._msg_parent())

    # ---------- Tree/Search ----------
    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.bll.get_all_course_categories() or []

        for i, r in enumerate(rows, start=1):
            # r => (ID, CourseCategoryName, EnglishCourseCategoryName)
            values = (i, r[0], r[1], r[2])
            # استفاده از ID به عنوان iid برای کنترل بهتر
            self.tree.insert("", "end", iid=str(r[0]), values=values)

        if not (self.category_id_var.get() or "").strip():
            self._set_selection_state(False)

    def _search(self):
        q = (self.search_var.get() or "").strip()
        if not q:
            self._refresh_tree()
            return

        self.tree.delete(*self.tree.get_children())
        rows = self.bll.search_course_categories(q) or []

        for i, r in enumerate(rows, start=1):
            values = (i, r[0], r[1], r[2])
            self.tree.insert("", "end", iid=str(r[0]), values=values)

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_tree()

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            self.category_id_var.set("")
            self._set_selection_state(False)
            return

        item = self.tree.item(sel[0])
        vals = item.get("values", [])
        if not vals or len(vals) < 4:
            self._set_selection_state(False)
            return

        # vals => (Row, ID, Name, EnglishName)
        self.category_id_var.set(str(vals[1]))
        self.var_name.set(str(vals[2]))
        self.var_english_name.set(str(vals[3]))

        self._set_selection_state(True)

    # ===================== UI =====================
    def course_category_form_load(self):
        try:
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

            self.win.title("CourseCategory CRUD")
            self.win.configure(bg="#111111")

            self.win.update_idletasks()
            sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            W = max(1100, int(sw * 0.85))
            H = max(700, int(sh * 0.80))
            x = sw // 2 - W // 2
            y = sh // 2 - H // 2
            self.win.geometry(f"{W}x{H}+{x}+{y}")
            self.win.minsize(1100, 700)

            # vars
            self.search_var = tk.StringVar(master=self.win, value="")
            self.category_id_var = tk.StringVar(master=self.win, value="")
            self.var_name = tk.StringVar(master=self.win, value="")
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

            header = ttk.Frame(root, style="Root.TFrame")
            header.pack(fill="x", pady=(0, 10))

            fn = (self.user.firstname or "").strip()
            ln = (self.user.lastname or "").strip()

            ttk.Label(header, text="Course Category Management", style="Title.TLabel").pack(side="left")
            ttk.Label(header, text=f"User: {fn} {ln}".strip(), style="Info.TLabel").pack(side="left", padx=(12, 0))

            ttk.Separator(root, orient="horizontal").pack(fill="x", pady=(0, 10))

            paned = ttk.Panedwindow(root, orient="vertical")
            paned.pack(fill="both", expand=True)

            top_panel = ttk.Frame(paned, style="Panel.TFrame")
            bottom_panel = ttk.Frame(paned, style="Panel.TFrame")
            paned.add(top_panel, weight=2)
            paned.add(bottom_panel, weight=6)

            # toolbar
            toolbar = ttk.Frame(top_panel, style="Panel.TFrame")
            toolbar.pack(fill="x", padx=14, pady=(12, 6))

            ttk.Label(toolbar, text="Category ID:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(toolbar, textvariable=self.category_id_var, style="Value.TLabel").grid(
                row=0, column=1, padx=(8, 18), sticky="w"
            )

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

            # form fields (2 columns)
            fields = ttk.Frame(top_panel, style="Panel.TFrame")
            fields.pack(fill="both", expand=True, padx=14, pady=(6, 14))

            fields.columnconfigure(0, weight=1)
            fields.columnconfigure(1, weight=1)

            # left
            cell1 = ttk.Frame(fields, style="Panel.TFrame")
            cell1.grid(row=0, column=0, sticky="ew", padx=10, pady=6)
            ttk.Label(cell1, text="Course Category Name (Persian)", style="Form.TLabel").grid(row=0, column=0,
                                                                                              sticky="w")
            ttk.Entry(cell1, textvariable=self.var_name, style="Form.TEntry", width=40).grid(row=1, column=0,
                                                                                             sticky="w", pady=(4, 0))

            # right
            cell2 = ttk.Frame(fields, style="Panel.TFrame")
            cell2.grid(row=0, column=1, sticky="ew", padx=10, pady=6)
            ttk.Label(cell2, text="English Course Category Name", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Entry(cell2, textvariable=self.var_english_name, style="Form.TEntry", width=40).grid(row=1, column=0,
                                                                                                     sticky="w",
                                                                                                     pady=(4, 0))

            # bottom (search + tree)
            bottom_panel.pack_propagate(False)

            search = ttk.Frame(bottom_panel, style="Panel.TFrame")
            search.pack(fill="x", padx=14, pady=(12, 8))
            search.columnconfigure(1, weight=1)

            ttk.Label(search, text="Search Category:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ent_search = ttk.Entry(search, textvariable=self.search_var, style="Form.TEntry")
            ent_search.grid(row=0, column=1, sticky="ew", padx=(8, 10))

            ttk.Button(search, text="Search", style="Primary.TButton", command=self._search).grid(row=0, column=2,
                                                                                                  padx=(0, 8))
            ttk.Button(search, text="Clear", style="Primary.TButton", command=self._clear_search).grid(row=0, column=3,
                                                                                                       padx=(0, 8))

            ent_search.bind("<Return>", lambda e: self._search())

            tree_frame = ttk.Frame(bottom_panel, style="Panel.TFrame")
            tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
            tree_frame.rowconfigure(0, weight=1)
            tree_frame.columnconfigure(0, weight=1)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

            cols = ("Row", "ID", "CourseCategoryName", "EnglishCourseCategoryName")

            self.tree = ttk.Treeview(
                tree_frame, columns=cols, show="headings",
                yscrollcommand=vsb.set, xscrollcommand=hsb.set
            )
            vsb.config(command=self.tree.yview)
            hsb.config(command=self.tree.xview)

            self.tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")

            for col in cols:
                self.tree.heading(col, text=col)
                if col in ("Row", "ID"):
                    self.tree.column(col, width=80, anchor="center")
                else:
                    self.tree.column(col, width=350, anchor="w")

            self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

            self.context_menu = tk.Menu(self.win, tearoff=0, bg="#1a1a1a", fg="white", font=font_sm)
            self.context_menu.add_command(label="Update Record", command=self._update)
            self.context_menu.add_command(label="Delete Record", command=self._delete)

            # بایند کردن کلیک راست موس روی تری‌ویو (دکمه 3 موس در ویندوز)
            self.tree.bind("<Button-3>", self._show_context_menu)

            self._refresh_tree()
            self.win.after(60, lambda: paned.sashpos(0, int(H * 0.28)))

            if self._created_root:
                self.win.mainloop()

        except Exception as e:
            messagebox.showerror("CourseCategory Form Error", str(e), parent=self._msg_parent())