
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pyodbc
from datetime import datetime, date
from io import BytesIO
import csv

from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
from Model.UserModel import User_Model_class


class StudentForm:
    def __init__(self, user_param: User_Model_class, master: tk.Misc = None):
        self.user = user_param
        self.master = master
        self.win = None
        self._created_root = False

        # --- DB ---
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

        # --- vars/widgets ---
        self.search_var = None
        self.person_id_var = None
        self.vars = {}
        self.date_widgets = {}

        self.cmb_education = None

        self.btn_update = None
        self.btn_delete = None

        # photo
        self.photo_bytes = None
        self.photo_label = None
        self._photo_imgtk = None

        # lookups
        self.education_name_to_id = {}
        self.education_id_to_name = {}

        # tree/cache
        self.tree = None
        self._rows_cache_by_id = {}

        # validation guards
        self._guard = {
            "FirstName": False,
            "LastName": False,
            "EnglishFirstName": False,
            "EnglishLastName": False,
            "NationalCode": False,
            "Mobile": False,
        }

        # fields
        self.date_fields = {"Birthdate", "FirstRegisterdate"}

        # NOTE: Photo handled separately (top-right)
        self.form_fields = [
            ("FirstName", "First Name"),
            ("LastName", "Last Name"),
            ("Birthdate", "Birthdate"),
            ("MaritalStatus", "Marital Status"),
            ("NationalCode", "National Code"),
            ("Mobile", "Mobile"),
            ("Address", "Address"),
            ("Gender", "Gender"),
            ("EmailAddress", "Email Address"),
            ("Education", "Education"),
            ("FirstRegisterdate", "First Register Date"),
            ("EnglishFirstName", "English First Name"),
            ("EnglishLastName", "English Last Name"),
        ]

        # columns in tree
        self.columns = [
            "PersonID",
            "FirstName", "LastName", "Birthdate", "MaritalStatus",
            "NationalCode", "Mobile", "Address", "Gender", "EmailAddress",
            "EducationID", "Education",
            "FirstRegisterdate", "EnglishFirstName", "EnglishLastName",
            "HasPhoto",
        ]

    # =========================
    # DB helpers
    # =========================
    def _db_query(self, sql: str, params=()):
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                rows = cur.fetchall() if cur.description else []
                cols = [d[0] for d in cur.description] if cur.description else []
                return rows, cols
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self.win)
            return None, None

    def _db_exec(self, sql: str, params=()):
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                return True
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self.win)
            return False

    @staticmethod
    def _norm(name: str) -> str:
        return "".join(ch for ch in (name or "").strip().lower() if ch != "_")

    def _row_to_named_dict(self, row, colnames):
        d = {}
        for i, c in enumerate(colnames):
            d[self._norm(c)] = row[i]
        return d

    def _get_any(self, d: dict, *names, default=None):
        for n in names:
            k = self._norm(n)
            if k in d:
                return d[k]
        return default

    # =========================
    # Education list
    # =========================
    def _load_education_list(self):
        rows, cols = self._db_query("EXEC dbo.GetAllEducationList")
        if rows is None:
            self.education_name_to_id = {}
            self.education_id_to_name = {}
            return

        out = []
        if cols:
            for r in rows:
                rd = self._row_to_named_dict(r, cols)
                edu_id = self._get_any(rd, "ID")
                edu_name = self._get_any(rd, "EnglishEducation", "Education")
                if edu_id is None or edu_name is None:
                    continue
                name = str(edu_name).strip()
                if name:
                    out.append((int(edu_id), name))
        else:
            for r in rows:
                out.append((int(r[0]), str(r[1]).strip()))

        out.sort(key=lambda x: x[0])
        self.education_name_to_id = {name: eid for eid, name in out}
        self.education_id_to_name = {eid: name for name, eid in self.education_name_to_id.items()}

    # =========================
    # Student rows mapping
    # =========================
    def _students_from_rows(self, rows, cols):
        out = []
        for r in rows:
            if cols:
                rd = self._row_to_named_dict(r, cols)
                d = {
                    "PersonID": self._get_any(rd, "PersonID", "ID"),
                    "FirstName": self._get_any(rd, "FirstName"),
                    "LastName": self._get_any(rd, "LastName"),
                    "Birthdate": self._get_any(rd, "Birthdate"),
                    "MaritalStatus": self._get_any(rd, "MaritalStatus"),
                    "NationalCode": self._get_any(rd, "NationalCode"),
                    "Mobile": self._get_any(rd, "Mobile"),
                    "Address": self._get_any(rd, "Address"),
                    "Gender": self._get_any(rd, "Gender"),
                    "EmailAddress": self._get_any(rd, "EmailAddress"),
                    "EducationID": self._get_any(rd, "EducationID", "EducationId"),
                    "Education": self._get_any(rd, "Education", "EnglishEducation"),
                    "FirstRegisterdate": self._get_any(rd, "FirstRegisterdate", "FirstRegisterDate"),
                    "EnglishFirstName": self._get_any(rd, "EnglishFirstName"),
                    "EnglishLastName": self._get_any(rd, "EnglishLastName"),
                    "Photo": self._get_any(rd, "Photo"),
                }
            else:
                d = {
                    "PersonID": r[0],
                    "FirstName": r[1],
                    "LastName": r[2],
                    "Birthdate": r[3],
                    "MaritalStatus": r[4],
                    "NationalCode": r[5],
                    "Mobile": r[6],
                    "Address": r[7],
                    "Gender": r[8],
                    "EmailAddress": r[9],
                    "EducationID": r[10],
                    "Education": r[11],
                    "FirstRegisterdate": r[12],
                    "EnglishFirstName": r[13],
                    "EnglishLastName": r[14],
                    "Photo": r[15],
                }

            if not d.get("Education"):
                try:
                    eid = d.get("EducationID")
                    d["Education"] = self.education_id_to_name.get(int(eid), "") if eid is not None else ""
                except Exception:
                    d["Education"] = ""

            photo = d.get("Photo")
            if photo is None:
                d["HasPhoto"] = "No"
            else:
                try:
                    if isinstance(photo, memoryview):
                        photo = photo.tobytes()
                    elif isinstance(photo, bytearray):
                        photo = bytes(photo)
                except Exception:
                    pass
                d["Photo"] = photo
                d["HasPhoto"] = "Yes"

            out.append(d)
        return out

    def _fetch_all_students(self):
        rows, cols = self._db_query("EXEC dbo.GetAllStudents")
        if rows is None:
            return []
        return self._students_from_rows(rows, cols)

    def _search_students_db(self, q: str):
        rows, cols = self._db_query("EXEC dbo.SearchStudents ?", (q,))
        if rows is None:
            return []
        return self._students_from_rows(rows, cols)

    # =========================
    # parse / validation helpers
    # =========================
    def _parse_date(self, s: str):
        s = (s or "").strip()
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _filter_alpha_space_max(self, key: str, max_len: int):
        if self._guard.get(key):
            return
        self._guard[key] = True
        try:
            s = (self.vars[key].get() or "")[:max_len]
            s2 = "".join(ch for ch in s if (ch.isalpha() or ch == " "))
            if s2 != self.vars[key].get():
                self.vars[key].set(s2)
        finally:
            self._guard[key] = False

    def _filter_digits_max(self, key: str, max_len: int):
        if self._guard.get(key):
            return
        self._guard[key] = True
        try:
            s = self.vars[key].get() or ""
            s2 = "".join(ch for ch in s if ch.isdigit())[:max_len]
            if s2 != s:
                self.vars[key].set(s2)
        finally:
            self._guard[key] = False

    def _validate_form(self, data: dict) -> bool:
        if not data["FirstName"] or not data["LastName"]:
            messagebox.showerror("Validation", "FirstName and LastName are required.", parent=self.win)
            return False

        if len(data["NationalCode"]) != 10:
            messagebox.showerror("Validation", "NationalCode must be exactly 10 digits.", parent=self.win)
            return False

        if len(data["Mobile"]) != 11:
            messagebox.showerror("Validation", "Mobile must be exactly 11 digits.", parent=self.win)
            return False

        for df in self.date_fields:
            if self._parse_date(data[df]) is None:
                messagebox.showerror("Validation", f"{df} must be a valid date (YYYY-MM-DD).", parent=self.win)
                return False

        if data["MaritalStatus"] not in ("Single", "Married"):
            messagebox.showerror("Validation", "MaritalStatus must be Single or Married.", parent=self.win)
            return False

        if data["Gender"] not in ("Male", "Female"):
            messagebox.showerror("Validation", "Gender must be Male or Female.", parent=self.win)
            return False

        if data["Education"] not in self.education_name_to_id:
            messagebox.showerror("Validation", "Please select Education.", parent=self.win)
            return False

        if not data["EnglishFirstName"] or not data["EnglishLastName"]:
            messagebox.showerror("Validation", "EnglishFirstName and EnglishLastName are required.", parent=self.win)
            return False

        return True

    # =========================
    # Selection state
    # =========================
    def _set_selection_state(self, has_selection: bool):
        state = "normal" if has_selection else "disabled"
        if self.btn_update:
            self.btn_update.config(state=state)
        if self.btn_delete:
            self.btn_delete.config(state=state)

    # =========================
    # Photo UI helpers
    # =========================
    def _set_photo_preview(self, photo_bytes):
        self.photo_bytes = photo_bytes
        if self.photo_label is None:
            return

        if not photo_bytes:
            self._photo_imgtk = None
            self.photo_label.configure(image="", text="No Photo")
            return

        try:
            img = Image.open(BytesIO(photo_bytes)).convert("RGB")
            img.thumbnail((220, 220))
            imgtk = ImageTk.PhotoImage(img)
            self._photo_imgtk = imgtk
            self.photo_label.configure(image=imgtk, text="")
        except Exception:
            self._photo_imgtk = None
            self.photo_label.configure(image="", text="Invalid Photo")

    def _choose_photo(self):
        path = filedialog.askopenfilename(
            parent=self.win,
            title="Choose Photo",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                b = f.read()
            self._set_photo_preview(b)
        except Exception as e:
            messagebox.showerror("Photo Error", str(e), parent=self.win)

    def _remove_photo(self):
        self._set_photo_preview(None)

    # =========================
    # UI
    # =========================
    def student_form_load(self):
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

            self.win.title("Student CRUD")
            self.win.configure(bg="#111111")

            # size
            self.win.update_idletasks()
            sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            W = max(1280, int(sw * 0.92))
            H = max(860, int(sh * 0.88))
            x = sw // 2 - W // 2
            y = sh // 2 - H // 2
            self.win.geometry(f"{W}x{H}+{x}+{y}")
            self.win.minsize(1280, 860)

            # vars
            self.search_var = tk.StringVar(master=self.win, value="")
            self.person_id_var = tk.StringVar(master=self.win, value="")
            for key, _ in self.form_fields:
                self.vars[key] = tk.StringVar(master=self.win, value="")

            # defaults
            self.vars["MaritalStatus"].set("Single")
            self.vars["Gender"].set("Male")

            # filters
            self.vars["FirstName"].trace_add("write", lambda *_: self._filter_alpha_space_max("FirstName", 20))
            self.vars["LastName"].trace_add("write", lambda *_: self._filter_alpha_space_max("LastName", 50))
            self.vars["EnglishFirstName"].trace_add("write",
                                                    lambda *_: self._filter_alpha_space_max("EnglishFirstName", 50))
            self.vars["EnglishLastName"].trace_add("write",
                                                   lambda *_: self._filter_alpha_space_max("EnglishLastName", 50))
            self.vars["NationalCode"].trace_add("write", lambda *_: self._filter_digits_max("NationalCode", 10))
            self.vars["Mobile"].trace_add("write", lambda *_: self._filter_digits_max("Mobile", 11))

            self._load_education_list()

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

            style.configure("Form.TEntry",
                            fieldbackground="#242424", background="#242424",
                            foreground="white", padding=4, font=font_sm)

            style.configure("Primary.TButton", padding=(10, 7), font=font_sm_b)

            style.configure("Dark.TRadiobutton", background="#1a1a1a", foreground="white", font=font_sm_b)

            style.configure("Treeview",
                            background="#1f1f1f", fieldbackground="#1f1f1f",
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

            ttk.Label(header, text="Student CRUD", style="Title.TLabel").pack(side="left")
            ttk.Label(header, text=f"User: {fn} {ln}".strip(), style="Info.TLabel").pack(side="left", padx=(12, 0))

            ttk.Separator(root, orient="horizontal").pack(fill="x", pady=(0, 10))

            paned = ttk.Panedwindow(root, orient="vertical")
            paned.pack(fill="both", expand=True)

            top_panel = ttk.Frame(paned, style="Panel.TFrame")
            bottom_panel = ttk.Frame(paned, style="Panel.TFrame")
            paned.add(top_panel, weight=3)
            paned.add(bottom_panel, weight=6)

            # ---------- toolbar ----------
            toolbar = ttk.Frame(top_panel, style="Panel.TFrame")
            toolbar.pack(fill="x", padx=14, pady=(12, 6))

            ttk.Label(toolbar, text="PersonID:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(toolbar, textvariable=self.person_id_var, style="Value.TLabel").grid(row=0, column=1,
                                                                                           padx=(8, 18), sticky="w")

            ttk.Button(toolbar, text="Save", style="Primary.TButton", command=self._save).grid(row=0, column=2,
                                                                                               padx=(0, 8))

            self.btn_update = ttk.Button(toolbar, text="Update", style="Primary.TButton", command=self._update)
            self.btn_update.grid(row=0, column=3, padx=(0, 8))

            self.btn_delete = ttk.Button(toolbar, text="Delete", style="Primary.TButton", command=self._delete)
            self.btn_delete.grid(row=0, column=4, padx=(0, 8))

            ttk.Button(toolbar, text="Clear", style="Primary.TButton", command=self._clear_form).grid(row=0, column=5,
                                                                                                      padx=(0, 8))
            ttk.Button(toolbar, text="Refresh", style="Primary.TButton", command=self._refresh_tree).grid(row=0,
                                                                                                          column=6,
                                                                                                          padx=(0, 8))

            ttk.Button(toolbar, text="Excel Export", style="Primary.TButton", command=self._export_excel).grid(row=0,
                                                                                                               column=7,
                                                                                                               padx=(0,
                                                                                                                     8))
            ttk.Button(toolbar, text="ID Card (PDF)", style="Primary.TButton", command=self._generate_id_card).grid(
                row=0, column=8, padx=(0, 8))
            ttk.Button(toolbar, text="Close", style="Primary.TButton", command=self.win.destroy).grid(row=0, column=9)

            self._set_selection_state(False)

            # ---------- top content: fields (left) + photo (right) ----------
            content = ttk.Frame(top_panel, style="Panel.TFrame")
            content.pack(fill="both", expand=True, padx=14, pady=(6, 14))
            content.columnconfigure(0, weight=1)
            content.columnconfigure(1, weight=0)

            fields = ttk.Frame(content, style="Panel.TFrame")
            fields.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            for c in range(3):
                fields.columnconfigure(c, weight=1, uniform="F3")

            photo_box = ttk.Frame(content, style="Panel.TFrame")
            photo_box.grid(row=0, column=1, sticky="ne")
            photo_box.columnconfigure(0, weight=1)

            ttk.Label(photo_box, text="Photo", style="Form.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))

            self.photo_label = ttk.Label(photo_box, text="No Photo", style="Form.TLabel")
            self.photo_label.grid(row=1, column=0, sticky="n", pady=(0, 8))

            btns_photo = ttk.Frame(photo_box, style="Panel.TFrame")
            btns_photo.grid(row=2, column=0, sticky="ew")
            ttk.Button(btns_photo, text="Choose", style="Primary.TButton", command=self._choose_photo).pack(side="left",
                                                                                                            padx=(0, 8))
            ttk.Button(btns_photo, text="Remove", style="Primary.TButton", command=self._remove_photo).pack(side="left")

            def make_cell(parent, key, title):
                cell = ttk.Frame(parent, style="Panel.TFrame")
                ttk.Label(cell, text=title, style="Form.TLabel").grid(row=0, column=0, sticky="w")
                cell.columnconfigure(0, weight=1)
                return cell

            for idx, (key, title) in enumerate(self.form_fields):
                r = idx // 3
                c = idx % 3

                cell = make_cell(fields, key, title)
                cell.grid(row=r, column=c, sticky="ew", padx=8, pady=5)

                if key in self.date_fields:
                    de = DateEntry(cell, textvariable=self.vars[key], date_pattern="yyyy-mm-dd")
                    de.grid(row=1, column=0, sticky="ew", pady=(3, 0))
                    self.date_widgets[key] = de

                elif key == "MaritalStatus":
                    rb = ttk.Frame(cell, style="Panel.TFrame")
                    rb.grid(row=1, column=0, sticky="w", pady=(6, 0))
                    ttk.Radiobutton(
                        rb, text="Single", value="Single",
                        variable=self.vars["MaritalStatus"],
                        style="Dark.TRadiobutton"
                    ).grid(row=0, column=0, padx=(0, 12))
                    ttk.Radiobutton(
                        rb, text="Married", value="Married",
                        variable=self.vars["MaritalStatus"],
                        style="Dark.TRadiobutton"
                    ).grid(row=0, column=1)

                elif key == "Gender":
                    rb = ttk.Frame(cell, style="Panel.TFrame")
                    rb.grid(row=1, column=0, sticky="w", pady=(6, 0))
                    ttk.Radiobutton(
                        rb, text="Male", value="Male",
                        variable=self.vars["Gender"],
                        style="Dark.TRadiobutton"
                    ).grid(row=0, column=0, padx=(0, 12))
                    ttk.Radiobutton(
                        rb, text="Female", value="Female",
                        variable=self.vars["Gender"],
                        style="Dark.TRadiobutton"
                    ).grid(row=0, column=1)

                elif key == "Education":
                    self.cmb_education = ttk.Combobox(
                        cell,
                        textvariable=self.vars["Education"],
                        state="readonly",
                        values=list(self.education_name_to_id.keys())
                    )
                    self.cmb_education.grid(row=1, column=0, sticky="ew", pady=(3, 0))

                else:
                    ttk.Entry(cell, textvariable=self.vars[key], style="Form.TEntry").grid(
                        row=1, column=0, sticky="ew", pady=(3, 0)
                    )

            self._set_photo_preview(None)

            # ---------- bottom: search + tree ----------
            bottom_panel.pack_propagate(False)

            search = ttk.Frame(bottom_panel, style="Panel.TFrame")
            search.pack(fill="x", padx=14, pady=(12, 8))
            search.columnconfigure(1, weight=1)

            ttk.Label(search, text="Search:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
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

            for col in self.columns:
                self.tree.heading(col, text=col)

                if col in ("PersonID", "EducationID"):
                    self.tree.column(col, width=90, anchor="center")
                elif col in ("Birthdate", "FirstRegisterdate"):
                    self.tree.column(col, width=120, anchor="center")
                elif col in ("NationalCode", "Mobile"):
                    self.tree.column(col, width=140, anchor="center")
                elif col in ("HasPhoto",):
                    self.tree.column(col, width=90, anchor="center")
                else:
                    self.tree.column(col, width=170, anchor="w")

            self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

            self._refresh_tree()
            self.win.after(60, lambda: paned.sashpos(0, int(H * 0.44)))

            if self._created_root:
                self.win.mainloop()

        except Exception as e:
            try:
                messagebox.showerror("Student Form Error", str(e), parent=self.win)
            except Exception:
                print("Student Form Error:", e)

    # =========================
    # CRUD (SP calls)
    # =========================
    def _get_form_data(self):
        return {k: (self.vars[k].get() or "").strip() for k, _ in self.form_fields}

    def _save(self):
        data = self._get_form_data()
        if not self._validate_form(data):
            return

        edu_id = self.education_name_to_id[data["Education"]]

        photo_param = None
        if self.photo_bytes:
            photo_param = pyodbc.Binary(self.photo_bytes)

        params = (
            data["FirstName"],
            data["LastName"],
            self._parse_date(data["Birthdate"]),
            data["MaritalStatus"],
            data["NationalCode"],
            data["Mobile"],
            data["Address"] if data["Address"] else None,
            data["Gender"],
            data["EmailAddress"] if data["EmailAddress"] else None,
            int(edu_id),
            self._parse_date(data["FirstRegisterdate"]),
            data["EnglishFirstName"],
            data["EnglishLastName"],
            photo_param,
        )

        qmarks = ",".join(["?"] * len(params))
        rows, _ = self._db_query(f"EXEC dbo.InsertStudent {qmarks}", params)
        if rows is None or not rows:
            return

        new_id = rows[0][0]
        self.person_id_var.set(str(new_id))
        self._set_selection_state(True)

        messagebox.showinfo("Saved", f"Saved successfully. PersonID={new_id}", parent=self.win)
        self._refresh_tree()

    def _update(self):
        pid = (self.person_id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Update", "Select a row first.", parent=self.win)
            return
        try:
            person_id = int(pid)
        except Exception:
            messagebox.showerror("Update", "Invalid PersonID.", parent=self.win)
            return

        data = self._get_form_data()
        if not self._validate_form(data):
            return

        edu_id = self.education_name_to_id[data["Education"]]

        photo_param = None
        if self.photo_bytes:
            photo_param = pyodbc.Binary(self.photo_bytes)

        params = (
            person_id,
            data["FirstName"],
            data["LastName"],
            self._parse_date(data["Birthdate"]),
            data["MaritalStatus"],
            data["NationalCode"],
            data["Mobile"],
            data["Address"] if data["Address"] else None,
            data["Gender"],
            data["EmailAddress"] if data["EmailAddress"] else None,
            int(edu_id),
            self._parse_date(data["FirstRegisterdate"]),
            data["EnglishFirstName"],
            data["EnglishLastName"],
            photo_param,
        )

        qmarks = ",".join(["?"] * len(params))
        ok = self._db_exec(f"EXEC dbo.UpdateStudent {qmarks}", params)
        if not ok:
            return

        messagebox.showinfo("Updated", "Updated successfully.", parent=self.win)
        self._refresh_tree()

    def _delete(self):
        pid = (self.person_id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Delete", "Select a row first.", parent=self.win)
            return
        try:
            person_id = int(pid)
        except Exception:
            messagebox.showerror("Delete", "Invalid PersonID.", parent=self.win)
            return

        if not messagebox.askyesno("Confirm", f"Delete PersonID={person_id}?", parent=self.win):
            return

        ok = self._db_exec("EXEC dbo.DeleteStudent ?", (person_id,))
        if not ok:
            return

        messagebox.showinfo("Deleted", "Deleted successfully.", parent=self.win)
        self._clear_form()
        self._refresh_tree()

    def _clear_form(self):
        for k in self.vars:
            self.vars[k].set("")
        self.vars["MaritalStatus"].set("Single")
        self.vars["Gender"].set("Male")
        self.person_id_var.set("")
        if self.cmb_education:
            self.cmb_education.set("")
        self._set_photo_preview(None)
        self._set_selection_state(False)

    # =========================
    # Tree/Search
    # =========================
    def _refresh_tree(self):
        data = self._fetch_all_students()
        self._rows_cache_by_id = {}

        self.tree.delete(*self.tree.get_children())
        for d in data:
            pid = d.get("PersonID")
            if pid is not None:
                self._rows_cache_by_id[int(pid)] = d

            values = []
            for col in self.columns:
                v = d.get(col, "")
                if isinstance(v, (datetime, date)):
                    v = v.isoformat()
                if col == "Photo":
                    v = ""
                values.append("" if v is None else str(v))
            self.tree.insert("", "end", values=values)

        if not (self.person_id_var.get() or "").strip():
            self._set_selection_state(False)

    def _search(self):
        q = (self.search_var.get() or "").strip()
        if not q:
            self._refresh_tree()
            return

        data = self._search_students_db(q)

        self.tree.delete(*self.tree.get_children())
        for d in data:
            values = []
            for col in self.columns:
                v = d.get(col, "")
                if isinstance(v, (datetime, date)):
                    v = v.isoformat()
                values.append("" if v is None else str(v))
            self.tree.insert("", "end", values=values)

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_tree()

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            self.person_id_var.set("")
            self._set_selection_state(False)
            return

        item = self.tree.item(sel[0])
        values = item.get("values", [])
        if not values:
            self.person_id_var.set("")
            self._set_selection_state(False)
            return

        mapped = dict(zip(self.columns, values))
        pid_str = "" if mapped.get("PersonID") is None else str(mapped.get("PersonID")).strip()
        self.person_id_var.set(pid_str)
        has_sel = bool(pid_str)
        self._set_selection_state(has_sel)

        row = None
        try:
            if pid_str:
                row = self._rows_cache_by_id.get(int(pid_str))
        except Exception:
            row = None

        for key, _title in self.form_fields:
            if key == "Education":
                edu_name = ""
                if row is not None:
                    edu_name = row.get("Education") or ""
                else:
                    edu_name = mapped.get("Education") or ""
                edu_name = "" if edu_name is None else str(edu_name)
                self.vars["Education"].set(edu_name)
                if self.cmb_education:
                    self.cmb_education.set(edu_name)

            elif key in self.date_fields:
                val = ""
                if row is not None:
                    val = row.get(key) or ""
                else:
                    val = mapped.get(key) or ""
                s = "" if val is None else (val.isoformat() if isinstance(val, (date, datetime)) else str(val))
                self.vars[key].set(s)
                if key in self.date_widgets:
                    de = self.date_widgets[key]
                    try:
                        dt = datetime.strptime(s, "%Y-%m-%d").date()
                        de.set_date(dt)
                    except Exception:
                        pass

            elif key == "MaritalStatus":
                ms = ""
                if row is not None:
                    ms = row.get("MaritalStatus") or "Single"
                else:
                    ms = mapped.get("MaritalStatus") or "Single"
                ms = str(ms).strip().lower()
                self.vars["MaritalStatus"].set("Married" if ms == "married" else "Single")

            elif key == "Gender":
                g = ""
                if row is not None:
                    g = row.get("Gender") or "Male"
                else:
                    g = mapped.get("Gender") or "Male"
                g = str(g).strip().lower()
                self.vars["Gender"].set("Female" if g == "female" else "Male")

            else:
                val = ""
                if row is not None:
                    val = row.get(key) or ""
                else:
                    val = mapped.get(key) or ""
                self.vars[key].set("" if val is None else str(val))

        if row is not None:
            self._set_photo_preview(row.get("Photo"))
        else:
            self._set_photo_preview(None)

    # =========================
    # New Features: Excel & PDF
    # =========================
    def _export_excel(self):
        if not self.tree.get_children():
            messagebox.showinfo("Export", "No data to export.", parent=self.win)
            return

        path = filedialog.asksaveasfilename(
            parent=self.win,
            title="Save as Excel (CSV)",
            defaultextension=".csv",
            filetypes=[("CSV/Excel Files", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(self.columns)
                for item_id in self.tree.get_children():
                    row_data = self.tree.item(item_id)['values']
                    writer.writerow(row_data)

            messagebox.showinfo("Success", f"Data exported successfully to:\n{path}", parent=self.win)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{e}", parent=self.win)

    def _generate_id_card(self):
        pid = (self.person_id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Select Student", "Please select a student from the list first.", parent=self.win)
            return

        try:
            row = self._rows_cache_by_id.get(int(pid))
            if not row:
                return

            card_w, card_h = 600, 350
            img = Image.new('RGB', (card_w, card_h), color="#ffffff")
            draw = ImageDraw.Draw(img)


            draw.rectangle([0, 0, card_w, 80], fill="#520034")

            try:
                font_title = ImageFont.truetype("arialbd.ttf", 34)
                font_text = ImageFont.truetype("arial.ttf", 22)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except IOError:
                font_title = font_text = font_small = ImageFont.load_default()

            draw.text((20, 20), "STUDENT ID CARD", fill="white", font=font_title)
            draw.text((450, 35), "Sematec LMS", fill="#dcdde1", font=font_small)

            # اطلاعات دانشجو
            eng_fname = row.get("EnglishFirstName") or row.get("FirstName", "")
            eng_lname = row.get("EnglishLastName") or row.get("LastName", "")
            full_name = f"{eng_fname} {eng_lname}".strip().upper()

            draw.text((30, 110), "Name:", fill="#520034", font=font_small)
            draw.text((30, 130), full_name, fill="black", font=font_text)

            draw.text((30, 180), "Student ID:", fill="#520034", font=font_small)
            draw.text((30, 200), str(pid), fill="black", font=font_text)

            draw.text((200, 180), "National Code:", fill="#520034", font=font_small)
            draw.text((200, 200), str(row.get("NationalCode", "")), fill="black", font=font_text)

            draw.text((30, 250), "Degree / Education:", fill="#520034", font=font_small)
            draw.text((30, 270), str(row.get("Education", "")), fill="black", font=font_text)

            # پردازش حرفه‌ای عکس با ImageOps.fit
            photo_bytes = row.get("Photo")
            photo_x, photo_y = 420, 110
            photo_w, photo_h = 140, 180

            if photo_bytes:
                try:
                    p_img = Image.open(BytesIO(photo_bytes)).convert("RGB")
                    p_img = ImageOps.fit(p_img, (photo_w, photo_h), method=Image.LANCZOS)
                    img.paste(p_img, (photo_x, photo_y))
                except Exception as ex:
                    print("Error processing photo:", ex)

            draw.rectangle([photo_x, photo_y, photo_x + photo_w, photo_y + photo_h], outline="#520034", width=3)

            # فوتر
            draw.rectangle([0, card_h - 30, card_w, card_h], fill="#3b0153")
            draw.text((20, card_h - 22), f"Issue Date: {datetime.now().strftime('%Y-%m-%d')}", fill="white",
                      font=font_small)

            path = filedialog.asksaveasfilename(
                parent=self.win,
                title="Save ID Card",
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"ID_Card_{pid}.pdf"
            )
            if path:
                img.save(path, "PDF", resolution=100.0)
                messagebox.showinfo("Success", f"ID Card generated and saved successfully!\n{path}", parent=self.win)

        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to generate ID Card:\n{e}", parent=self.win)