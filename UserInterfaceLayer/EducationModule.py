
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from Model.UserModel import User_Model_class
from Model.EducationModel import Education_Model_Class
from BusinessLogicLayer.Education_CRUD_BLL import Education_CRUD_BLL_Class


class EducationForm:
    def __init__(self, user_param: User_Model_class, master: tk.Misc = None):
        self.user = user_param
        self.master = master
        self.win = None
        self._created_root = False

        self.bll = Education_CRUD_BLL_Class()

        self.search_var = None
        self.id_var = None
        self.title_var = None
        self.english_var = None

        self.tree = None
        self.context_menu = None
        self.btn_save = None
        self.btn_update = None
        self.btn_delete = None

        self.columns = ["Row", "ID", "EducationTitle", "EnglishEducation"]

    # ---------------- helpers ----------------
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

    def _validate_form(self) -> bool:
        title = (self.title_var.get() or "").strip()
        eng = (self.english_var.get() or "").strip()

        if not title:
            messagebox.showerror("Validation", "EducationTitle is required.", parent=self._msg_parent())
            return False

        if not eng:
            messagebox.showerror("Validation", "EnglishEducation is required.", parent=self._msg_parent())
            return False

        if len(title) > 20:
            messagebox.showerror("Validation", "EducationTitle max length is 20.", parent=self._msg_parent())
            return False

        if len(eng) > 20:
            messagebox.showerror("Validation", "EnglishEducation max length is 20.", parent=self._msg_parent())
            return False

        return True

    # ---------- Context Menu ----------
    def _show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self._on_tree_select(None)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    # ---------------- DB/CRUD via BLL ----------------
    def _save(self):
        if not self._validate_form():
            return

        edu_obj = Education_Model_Class(
            education_title=(self.title_var.get() or "").strip(),
            english_education=(self.english_var.get() or "").strip()
        )

        try:
            new_id = self.bll.register_education(edu_obj)
            if new_id is None:
                messagebox.showerror("Save", "Insert failed (no ID returned).", parent=self._msg_parent())
                return

            self.id_var.set(str(new_id))
            messagebox.showinfo("Saved", f"Education saved successfully. ID={new_id}", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()

        except Exception as e:
            messagebox.showerror("Save Error", str(e), parent=self._msg_parent())

    def _update(self):
        sid = (self.id_var.get() or "").strip()
        if not sid:
            messagebox.showwarning("Update", "Select a row first.", parent=self._msg_parent())
            return

        try:
            edu_id = int(sid)
        except Exception:
            messagebox.showerror("Update", "Invalid ID.", parent=self._msg_parent())
            return

        if not self._validate_form():
            return

        edu_obj = Education_Model_Class(
            education_title=(self.title_var.get() or "").strip(),
            english_education=(self.english_var.get() or "").strip(),
            education_id=edu_id
        )

        try:
            ok = self.bll.update_education(edu_obj)
            if ok:
                messagebox.showinfo("Updated", "Education updated successfully.", parent=self._msg_parent())
                self._refresh_tree()
        except Exception as e:
            messagebox.showerror("Update Error", str(e), parent=self._msg_parent())

    def _delete(self):
        sid = (self.id_var.get() or "").strip()
        if not sid:
            messagebox.showwarning("Delete", "Select a row first.", parent=self._msg_parent())
            return

        try:
            edu_id = int(sid)
        except Exception:
            messagebox.showerror("Delete", "Invalid ID.", parent=self._msg_parent())
            return

        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete Education ID={edu_id} ?",
                                   parent=self._msg_parent()):
            return

        try:
            ok = self.bll.delete_education(edu_id)
            if ok:
                messagebox.showinfo("Deleted", "Education deleted successfully.", parent=self._msg_parent())
                self._clear_form()
                self._refresh_tree()
        except Exception as e:
            # هندل کردن ارور Foreign Key (اگر مدرک تحصیلی به شخصی متصل باشد)
            if "REFERENCE constraint" in str(e):
                msg = "Cannot delete this education level because it is assigned to one or more employees/teachers."
                messagebox.showerror("Dependency Error", msg, parent=self._msg_parent())
            else:
                messagebox.showerror("Delete Error", str(e), parent=self._msg_parent())

    def _clear_form(self):
        self.id_var.set("")
        self.title_var.set("")
        self.english_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self._set_selection_state(False)

    # ---------------- Tree/Search ----------------
    def _refresh_tree(self):
        try:
            rows = self.bll.get_all_educations()
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())
            return

        self.tree.delete(*self.tree.get_children())

        for idx, r in enumerate(rows, start=1):
            # r: (ID, EducationTitle, EnglishEducation)
            rid = "" if r[0] is None else str(r[0])
            title = "" if r[1] is None else str(r[1])
            eng = "" if r[2] is None else str(r[2])

            self.tree.insert("", "end", iid=rid, values=[idx, rid, title, eng])

        if not (self.id_var.get() or "").strip():
            self._set_selection_state(False)

    def _search(self):
        q = (self.search_var.get() or "").strip()
        if not q:
            self._refresh_tree()
            return

        try:
            rows = self.bll.search_educations(q)
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())
            return

        self.tree.delete(*self.tree.get_children())
        for idx, r in enumerate(rows, start=1):
            rid = "" if r[0] is None else str(r[0])
            title = "" if r[1] is None else str(r[1])
            eng = "" if r[2] is None else str(r[2])
            self.tree.insert("", "end", iid=rid, values=[idx, rid, title, eng])

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_tree()

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            self.id_var.set("")
            self._set_selection_state(False)
            return

        item = self.tree.item(sel[0])
        values = item.get("values", [])
        if not values or len(values) < 4:
            self._set_selection_state(False)
            return

        self.id_var.set(str(values[1]).strip())
        self.title_var.set(str(values[2]))
        self.english_var.set(str(values[3]))
        self._set_selection_state(True)

    # ===================== UI =====================
    def education_form_load(self):
        try:
            # window
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

            self.win.title("Education CRUD")
            self.win.configure(bg="#111111")

            self.win.update_idletasks()
            sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            W = max(1100, int(sw * 0.78))
            H = max(700, int(sh * 0.78))
            x = sw // 2 - W // 2
            y = sh // 2 - H // 2
            self.win.geometry(f"{W}x{H}+{x}+{y}")
            self.win.minsize(1100, 700)

            # vars
            self.search_var = tk.StringVar(master=self.win, value="")
            self.id_var = tk.StringVar(master=self.win, value="")
            self.title_var = tk.StringVar(master=self.win, value="")
            self.english_var = tk.StringVar(master=self.win, value="")

            # style (same theme)
            style = ttk.Style(self.win)
            try:
                style.theme_use("clam")
            except Exception:
                pass

            font_sm = ("Segoe UI", 10)
            font_sm_b = ("Segoe UI", 10, "bold")
            font_title = ("Segoe UI Black", 18)

            style.configure("Root.TFrame", background="#111111")
            style.configure("Panel.TFrame", background="#1a1a1a")
            style.configure("Title.TLabel", background="#111111", foreground="white", font=font_title)
            style.configure("Info.TLabel", background="#111111", foreground="#bdbdbd", font=font_sm)
            style.configure("Form.TLabel", background="#1a1a1a", foreground="#e6e6e6", font=font_sm_b)
            style.configure("Value.TLabel", background="#1a1a1a", foreground="white", font=font_sm_b)

            style.configure("Form.TEntry", fieldbackground="#242424", background="#242424",
                            foreground="white", padding=5, font=font_sm)

            style.configure("Primary.TButton", padding=(12, 7), font=font_sm_b)

            style.configure("Treeview", background="#1f1f1f", fieldbackground="#1f1f1f",
                            foreground="white", rowheight=26, borderwidth=0, font=font_sm)
            style.configure("Treeview.Heading", background="#2a2a2a", foreground="white", font=font_sm_b)
            style.map("Treeview", background=[("selected", "#3a3a3a")])

            # root
            root = ttk.Frame(self.win, style="Root.TFrame")
            root.pack(fill="both", expand=True, padx=16, pady=16)

            header = ttk.Frame(root, style="Root.TFrame")
            header.pack(fill="x", pady=(0, 10))

            fn = (self.user.firstname or "").strip()
            ln = (self.user.lastname or "").strip()

            ttk.Label(header, text="Education Management", style="Title.TLabel").pack(side="left")
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
            toolbar.pack(fill="x", padx=14, pady=(12, 6))

            ttk.Label(toolbar, text="ID:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(toolbar, textvariable=self.id_var, style="Value.TLabel").grid(row=0, column=1, padx=(8, 18),
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
            fields.pack(fill="both", expand=True, padx=14, pady=(6, 14))

            fields.columnconfigure(0, weight=1)
            fields.columnconfigure(1, weight=1)

            # Title
            cell1 = ttk.Frame(fields, style="Panel.TFrame")
            cell1.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            ttk.Label(cell1, text="Education Title (Persian)", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Entry(cell1, textvariable=self.title_var, style="Form.TEntry", width=35).grid(row=1, column=0,
                                                                                              sticky="w", pady=(6, 0))

            # English
            cell2 = ttk.Frame(fields, style="Panel.TFrame")
            cell2.grid(row=0, column=1, sticky="ew", padx=10, pady=8)
            ttk.Label(cell2, text="English Education", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Entry(cell2, textvariable=self.english_var, style="Form.TEntry", width=35).grid(row=1, column=0,
                                                                                                sticky="w", pady=(6, 0))

            # bottom panel
            bottom_panel.pack_propagate(False)

            search = ttk.Frame(bottom_panel, style="Panel.TFrame")
            search.pack(fill="x", padx=14, pady=(12, 8))
            search.columnconfigure(1, weight=1)

            ttk.Label(search, text="Search Education:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
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

            self.tree = ttk.Treeview(
                tree_frame, columns=self.columns, show="headings",
                yscrollcommand=vsb.set, xscrollcommand=hsb.set
            )
            vsb.config(command=self.tree.yview)
            hsb.config(command=self.tree.xview)

            self.tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")

            # headings + widths
            for col in self.columns:
                self.tree.heading(col, text=col)

            self.tree.column("Row", width=70, anchor="center")
            self.tree.column("ID", width=90, anchor="center")
            self.tree.column("EducationTitle", width=350, anchor="w")
            self.tree.column("EnglishEducation", width=350, anchor="w")

            self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

            # --- ایجاد منوی کلیک راست (Context Menu) ---
            self.context_menu = tk.Menu(self.win, tearoff=0, bg="#1a1a1a", fg="white", font=font_sm)
            self.context_menu.add_command(label="Update Record", command=self._update)
            self.context_menu.add_command(label="Delete Record", command=self._delete)
            self.tree.bind("<Button-3>", self._show_context_menu)

            self._refresh_tree()

            # split size
            self.win.after(50, lambda: paned.sashpos(0, int(H * 0.28)))

            if self._created_root:
                self.win.mainloop()

        except Exception as e:
            messagebox.showerror("Education Form Error", str(e), parent=self._msg_parent())