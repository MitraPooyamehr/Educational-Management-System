
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyodbc

from Model.UserModel import User_Model_class


class CourseForm:
    def __init__(self, user_param: User_Model_class, master: tk.Misc = None):
        self.user = user_param
        self.master = master
        self.win = None
        self._created_root = False

        # ✅ IMPORTANT: ODBC Driver 17
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

        # top vars
        self.search_var = None
        self.course_id_var = None

        self.vars = {}
        self.cmb_category = None
        self.cmb_prereq = None
        self.cmb_status = None

        self.btn_update = None
        self.btn_delete = None
        self.btn_download = None

        # Text widgets
        self.txt_description = None
        self.txt_syllabus = None

        # file bytes
        self.syllabus_file_path = None
        self.syllabus_file_bytes = None
        self.lbl_file_name = None

        # combos mapping
        self.category_name_to_id = {}
        self.category_id_to_name = {}

        self.course_name_to_id = {}
        self.course_id_to_name = {}

        # Tree
        self.tree = None
        self.context_menu = None
        self.columns = [
            "Row",
            "CourseCode",
            "CourseName",
            "EnglishCourseName",
            "Duration",
            "Cost",
            "Status",
            "Category",
            "Prerequisite"
        ]

        # cache
        self._rows_cache = {}

        self._guard = {
            "CourseCode": False,
            "Duration": False,
            "Cost": False
        }

    # ---------------- helpers ----------------
    @staticmethod
    def _norm_name(name: str) -> str:
        return "".join(ch for ch in (name or "").strip().lower() if ch != "_")

    def _row_to_named_dict(self, row, colnames):
        d = {}
        for i, c in enumerate(colnames):
            d[self._norm_name(c)] = row[i]
        return d

    def _get_any(self, d: dict, *names, default=None):
        for n in names:
            k = self._norm_name(n)
            if k in d:
                return d[k]
        return default

    def _msg_parent(self):
        return self.win if (self.win is not None and self.win.winfo_exists()) else None

    # ---------------- DB ----------------
    def _db_query(self, sql: str, params=()):
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                rows = cur.fetchall() if cur.description else []
                cols = [d[0] for d in cur.description] if cur.description else []
                return rows, cols
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())
            return None, None

    def _db_exec(self, sql: str, params=()):
        try:
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                return True
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())
            return False

    # ---------------- combo loaders ----------------
    def _load_category_list(self):
        rows, cols = self._db_query("SELECT * FROM dbo.CourseCategory ORDER BY ID")
        if rows is None:
            self.category_name_to_id = {}
            self.category_id_to_name = {}
            return

        out = []
        if cols:
            for r in rows:
                rd = self._row_to_named_dict(r, cols)
                cid = self._get_any(rd, "ID")
                name = self._get_any(rd, "EnglishCourseCategoryName", "EnglishCategoryName", "CourseCategoryName",
                                     "CategoryName")
                if cid is None or name is None: continue
                n = str(name).strip()
                if n: out.append((int(cid), n))
        else:
            for r in rows:
                out.append((int(r[0]), str(r[1]).strip()))

        out.sort(key=lambda x: x[0])
        self.category_name_to_id = {name: cid for cid, name in out}
        self.category_id_to_name = {cid: name for name, cid in self.category_name_to_id.items()}

    def _load_course_list_for_prereq(self):
        rows, cols = self._db_query("SELECT ID, CourseName FROM dbo.Course ORDER BY ID")
        if rows is None:
            self.course_name_to_id = {}
            self.course_id_to_name = {}
            return

        out = [(0, "None")]
        for r in rows:
            out.append((int(r[0]), str(r[1]).strip()))

        self.course_name_to_id = {name: cid for cid, name in out}
        self.course_id_to_name = {cid: name for name, cid in self.course_name_to_id.items()}

    # ---------------- parsing / filters ----------------
    def _parse_int(self, s: str, allow_none=True):
        s = (s or "").strip()
        if s == "": return None if allow_none else 0
        if not s.isdigit(): return None
        return int(s)

    def _filter_digits_max(self, key: str, max_len: int):
        if self._guard.get(key): return
        self._guard[key] = True
        try:
            s = self.vars[key].get() or ""
            s2 = "".join(ch for ch in s if ch.isdigit())[:max_len]
            if s2 != s: self.vars[key].set(s2)
        finally:
            self._guard[key] = False

    def _get_text(self, widget: tk.Text) -> str:
        return (widget.get("1.0", "end").strip() if widget else "")

    def _set_text(self, widget: tk.Text, value: str):
        if not widget: return
        widget.delete("1.0", "end")
        widget.insert("1.0", value or "")

    # ---------------- validation ----------------
    def _validate_form(self, data: dict) -> bool:
        if self._parse_int(data["CourseCode"], allow_none=False) is None:
            messagebox.showerror("Validation", "CourseCode must be numeric.", parent=self._msg_parent())
            return False
        if not data["CourseName"]:
            messagebox.showerror("Validation", "CourseName is required.", parent=self._msg_parent())
            return False
        if not data["EnglishCourseName"]:
            messagebox.showerror("Validation", "EnglishCourseName is required.", parent=self._msg_parent())
            return False
        dur = self._parse_int(data["Duration"], allow_none=False)
        if dur is None or dur < 1 or dur > 255:
            messagebox.showerror("Validation", "Duration must be between 1 and 255.", parent=self._msg_parent())
            return False
        cost = self._parse_int(data["Cost"], allow_none=False)
        if cost is None or cost < 0:
            messagebox.showerror("Validation", "Cost must be numeric >= 0.", parent=self._msg_parent())
            return False
        if data["Status"] not in ("Active", "Inactive"):
            messagebox.showerror("Validation", "Status must be Active or Inactive.", parent=self._msg_parent())
            return False
        if data["CourseCategory"] not in self.category_name_to_id:
            messagebox.showerror("Validation", "Please select CourseCategory.", parent=self._msg_parent())
            return False
        if self.syllabus_file_bytes is None:
            messagebox.showerror("Validation", "Please choose Syllabus File (required).", parent=self._msg_parent())
            return False
        return True

    def _set_selection_state(self, has_selection: bool):
        st = ("normal" if has_selection else "disabled")
        if self.btn_update: self.btn_update.config(state=st)
        if self.btn_delete: self.btn_delete.config(state=st)

        file_exists_state = "normal" if (has_selection and self.syllabus_file_bytes) else "disabled"
        if self.btn_download: self.btn_download.config(state=file_exists_state)

    # ---------------- file ----------------
    def _choose_file(self):
        path = filedialog.askopenfilename(
            title="Choose Syllabus File",
            filetypes=[("All Files", "*.*"), ("PDF", "*.pdf"), ("Word", "*.docx;*.doc")]
        )
        if not path: return
        try:
            with open(path, "rb") as f:
                self.syllabus_file_bytes = f.read()
            self.syllabus_file_path = path
            name = os.path.basename(path)
            if self.lbl_file_name: self.lbl_file_name.config(text=name)

            # آپدیت وضعیت دکمه دانلود
            if self.btn_download and self.course_id_var.get():
                self.btn_download.config(state="normal")
        except Exception as e:
            messagebox.showerror("File Error", str(e), parent=self._msg_parent())

    def _remove_file(self):
        self.syllabus_file_path = None
        self.syllabus_file_bytes = None
        if self.lbl_file_name:
            self.lbl_file_name.config(text="No file selected")
        if self.btn_download:
            self.btn_download.config(state="disabled")

    def _download_file(self):
        if not self.syllabus_file_bytes:
            messagebox.showwarning("Download", "No file bytes available to download.", parent=self._msg_parent())
            return

        path = filedialog.asksaveasfilename(
            title="Save Syllabus File",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Word", "*.docx"), ("All Files", "*.*")],
            parent=self._msg_parent()
        )
        if not path: return
        try:
            with open(path, "wb") as f:
                f.write(self.syllabus_file_bytes)
            messagebox.showinfo("Success", "File downloaded successfully.", parent=self._msg_parent())
            os.startfile(os.path.dirname(path))
        except Exception as e:
            messagebox.showerror("Download Error", str(e), parent=self._msg_parent())

    # ---------------- fetch rows ----------------
    def _fetch_all_courses(self):
        rows, cols = self._db_query("EXEC dbo.GetAllCourses")
        if rows is None:
            sql = """
                SELECT c.ID, c.CourseCode, c.CourseName, c.EnglishCourseName, c.Description,
                       c.Duration, c.Syllabus, c.Cost, c.Status, c.CourseCategoryID,
                       cc.EnglishCourseCategoryName, c.PrerequisitCourseID, pc.CourseName AS PrereqName
                FROM dbo.Course c
                LEFT JOIN dbo.CourseCategory cc ON cc.ID = c.CourseCategoryID
                LEFT JOIN dbo.Course pc ON pc.ID = c.PrerequisitCourseID
                ORDER BY c.ID
            """
            rows, cols = self._db_query(sql)
            if rows is None: return []

        out = []
        for r in rows:
            if cols:
                rd = self._row_to_named_dict(r, cols)
                course_id = self._get_any(rd, "ID", "CourseID")
                d = {
                    "ID": course_id, "CourseCode": self._get_any(rd, "CourseCode"),
                    "CourseName": self._get_any(rd, "CourseName"),
                    "EnglishCourseName": self._get_any(rd, "EnglishCourseName"),
                    "Description": self._get_any(rd, "Description"), "Duration": self._get_any(rd, "Duration"),
                    "Syllabus": self._get_any(rd, "Syllabus"), "Cost": self._get_any(rd, "Cost"),
                    "Status": self._get_any(rd, "Status"), "CourseCategoryID": self._get_any(rd, "CourseCategoryID"),
                    "Category": self._get_any(rd, "CategoryName", "EnglishCourseCategoryName"),
                    "PrerequisitCourseID": self._get_any(rd, "PrerequisitCourseID"),
                    "Prerequisite": self._get_any(rd, "PrereqName"),
                }
            else:
                d = {
                    "ID": r[0], "CourseCode": r[1], "CourseName": r[2], "EnglishCourseName": r[3],
                    "Description": r[4], "Duration": r[5], "Syllabus": r[6], "Cost": r[7], "Status": r[8],
                    "CourseCategoryID": r[9], "Category": r[10] if len(r) > 10 else "",
                    "PrerequisitCourseID": r[11] if len(r) > 11 else None, "Prerequisite": r[12] if len(r) > 12 else "",
                }

            if not d.get("Category"):
                try:
                    d["Category"] = self.category_id_to_name.get(int(d.get("CourseCategoryID")), "")
                except:
                    d["Category"] = ""

            if not d.get("Prerequisite"):
                try:
                    d["Prerequisite"] = self.course_id_to_name.get(int(d.get("PrerequisitCourseID")), "") or "None"
                except:
                    d["Prerequisite"] = "None"
            out.append(d)
        return out

    def _search_courses_db(self, q: str):
        rows, cols = self._db_query("EXEC dbo.SearchCourses ?", (q,))
        if rows is None:
            sql = """
                SELECT c.ID, c.CourseCode, c.CourseName, c.EnglishCourseName, c.Description,
                       c.Duration, c.Syllabus, c.Cost, c.Status, c.CourseCategoryID,
                       cc.EnglishCourseCategoryName, c.PrerequisitCourseID, pc.CourseName AS PrereqName
                FROM dbo.Course c
                LEFT JOIN dbo.CourseCategory cc ON cc.ID = c.CourseCategoryID
                LEFT JOIN dbo.Course pc ON pc.ID = c.PrerequisitCourseID
                WHERE c.CourseName LIKE ? OR c.EnglishCourseName LIKE ? ORDER BY c.ID
            """
            like = f"%{q}%"
            rows, cols = self._db_query(sql, (like, like))
            if rows is None: return []

        tmp = []
        for r in rows:
            if cols:
                rd = self._row_to_named_dict(r, cols)
                course_id = self._get_any(rd, "ID", "CourseID")
                d = {
                    "ID": course_id, "CourseCode": self._get_any(rd, "CourseCode"),
                    "CourseName": self._get_any(rd, "CourseName"),
                    "EnglishCourseName": self._get_any(rd, "EnglishCourseName"),
                    "Description": self._get_any(rd, "Description"),
                    "Duration": self._get_any(rd, "Duration"), "Syllabus": self._get_any(rd, "Syllabus"),
                    "Cost": self._get_any(rd, "Cost"), "Status": self._get_any(rd, "Status"),
                    "CourseCategoryID": self._get_any(rd, "CourseCategoryID"),
                    "Category": self._get_any(rd, "CategoryName", "EnglishCourseCategoryName"),
                    "PrerequisitCourseID": self._get_any(rd, "PrerequisitCourseID"),
                    "Prerequisite": self._get_any(rd, "PrereqName"),
                }
            else:
                d = {
                    "ID": r[0], "CourseCode": r[1], "CourseName": r[2], "EnglishCourseName": r[3],
                    "Description": r[4], "Duration": r[5], "Syllabus": r[6], "Cost": r[7], "Status": r[8],
                    "CourseCategoryID": r[9], "Category": r[10] if len(r) > 10 else "",
                    "PrerequisitCourseID": r[11] if len(r) > 11 else None, "Prerequisite": r[12] if len(r) > 12 else "",
                }

            if not d.get("Category"):
                try:
                    d["Category"] = self.category_id_to_name.get(int(d.get("CourseCategoryID")), "")
                except:
                    d["Category"] = ""
            if not d.get("Prerequisite"):
                try:
                    d["Prerequisite"] = self.course_id_to_name.get(int(d.get("PrerequisitCourseID")), "") or "None"
                except:
                    d["Prerequisite"] = "None"
            tmp.append(d)
        return tmp

    # ---------------- UI ----------------
    def course_form_load(self):
        try:
            use_toplevel = False
            if self.master is not None:
                try:
                    use_toplevel = bool(self.master.winfo_exists())
                except:
                    use_toplevel = False

            if use_toplevel:
                self.win = tk.Toplevel(self.master)
                self._created_root = False
            else:
                self.win = tk.Tk()
                self._created_root = True

            self.win.title("Course CRUD")
            self.win.configure(bg="#111111")

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
            self.course_id_var = tk.StringVar(master=self.win, value="")

            # form vars
            self.vars["CourseCode"] = tk.StringVar(master=self.win, value="")
            self.vars["CourseName"] = tk.StringVar(master=self.win, value="")
            self.vars["EnglishCourseName"] = tk.StringVar(master=self.win, value="")
            self.vars["Duration"] = tk.StringVar(master=self.win, value="")
            self.vars["Cost"] = tk.StringVar(master=self.win, value="")
            self.vars["Status"] = tk.StringVar(master=self.win, value="Active")
            self.vars["CourseCategory"] = tk.StringVar(master=self.win, value="")
            self.vars["PrerequisiteCourse"] = tk.StringVar(master=self.win, value="None")

            # digit filters
            self.vars["CourseCode"].trace_add("write", lambda *_: self._filter_digits_max("CourseCode", 10))
            self.vars["Duration"].trace_add("write", lambda *_: self._filter_digits_max("Duration", 3))
            self.vars["Cost"].trace_add("write", lambda *_: self._filter_digits_max("Cost", 10))

            # load combos
            self._load_category_list()
            self._load_course_list_for_prereq()

            # style
            style = ttk.Style(self.win)
            try:
                style.theme_use("clam")
            except:
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
            style.configure("Form.TEntry", fieldbackground="#242424", background="#242424", foreground="white",
                            padding=4, font=font_sm)
            style.configure("Primary.TButton", padding=(10, 7), font=font_sm_b)
            style.configure("Treeview", background="#1f1f1f", fieldbackground="#1f1f1f", foreground="white",
                            rowheight=24, borderwidth=0, font=font_sm)
            style.configure("Treeview.Heading", background="#2a2a2a", foreground="white", font=font_sm_b)
            style.map("Treeview", background=[("selected", "#3a3a3a")])

            # root
            root = ttk.Frame(self.win, style="Root.TFrame")
            root.pack(fill="both", expand=True, padx=16, pady=16)

            header = ttk.Frame(root, style="Root.TFrame")
            header.pack(fill="x", pady=(0, 10))

            fn = (getattr(self.user, "firstname", "") or "").strip()
            ln = (getattr(self.user, "lastname", "") or "").strip()

            ttk.Label(header, text="Course CRUD", style="Title.TLabel").pack(side="left")
            ttk.Label(header, text=f"User: {fn} {ln}".strip(), style="Info.TLabel").pack(side="left", padx=(12, 0))
            ttk.Separator(root, orient="horizontal").pack(fill="x", pady=(0, 10))

            paned = ttk.Panedwindow(root, orient="vertical")
            paned.pack(fill="both", expand=True)
            top_panel = ttk.Frame(paned, style="Panel.TFrame")
            bottom_panel = ttk.Frame(paned, style="Panel.TFrame")
            paned.add(top_panel, weight=5)
            paned.add(bottom_panel, weight=7)

            # toolbar
            toolbar = ttk.Frame(top_panel, style="Panel.TFrame")
            toolbar.pack(fill="x", padx=14, pady=(12, 6))

            ttk.Label(toolbar, text="CourseID:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(toolbar, textvariable=self.course_id_var, style="Value.TLabel").grid(row=0, column=1,
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
            ttk.Button(toolbar, text="Close", style="Primary.TButton", command=self.win.destroy).grid(row=0, column=7)

            self._set_selection_state(False)

            # -------- form grid --------
            form = ttk.Frame(top_panel, style="Panel.TFrame")
            form.pack(fill="both", expand=True, padx=14, pady=(6, 14))

            for c in range(3): form.columnconfigure(c, weight=1)

            self._make_entry_cell(form, 0, 0, "Course Code", "CourseCode")
            self._make_entry_cell(form, 0, 1, "Course Name", "CourseName")
            self._make_entry_cell(form, 0, 2, "English Course Name", "EnglishCourseName")
            self._make_entry_cell(form, 1, 0, "Duration", "Duration")
            self._make_entry_cell(form, 1, 1, "Cost (Rials)", "Cost")

            cell_status = self._make_cell(form, 1, 2, "Status")
            self.cmb_status = ttk.Combobox(cell_status, textvariable=self.vars["Status"], state="readonly",
                                           values=["Active", "Inactive"], width=24)
            self.cmb_status.grid(row=1, column=0, sticky="w", pady=(3, 0))

            cell_cat = self._make_cell(form, 2, 0, "Course Category")
            self.cmb_category = ttk.Combobox(cell_cat, textvariable=self.vars["CourseCategory"], state="readonly",
                                             values=list(self.category_name_to_id.keys()), width=24)
            self.cmb_category.grid(row=1, column=0, sticky="w", pady=(3, 0))

            cell_pr = self._make_cell(form, 2, 1, "Prerequisite")
            self.cmb_prereq = ttk.Combobox(cell_pr, textvariable=self.vars["PrerequisiteCourse"], state="readonly",
                                           values=list(self.course_name_to_id.keys()), width=24)
            self.cmb_prereq.grid(row=1, column=0, sticky="w", pady=(3, 0))

            # File chooser UI
            cell_file = self._make_cell(form, 2, 2, "Syllabus File (Required)")
            btns = ttk.Frame(cell_file, style="Panel.TFrame")
            btns.grid(row=1, column=0, sticky="w", pady=(3, 0))

            ttk.Button(btns, text="Choose", style="Primary.TButton", command=self._choose_file).pack(side="left")
            ttk.Button(btns, text="Remove", style="Primary.TButton", command=self._remove_file).pack(side="left",
                                                                                                     padx=(8, 0))
            self.btn_download = ttk.Button(btns, text="Download", style="Primary.TButton", command=self._download_file)
            self.btn_download.pack(side="left", padx=(8, 0))

            self.lbl_file_name = ttk.Label(cell_file, text="No file selected", style="Info.TLabel")
            self.lbl_file_name.grid(row=2, column=0, sticky="w", pady=(6, 0))

            desc_cell = ttk.Frame(form, style="Panel.TFrame")
            desc_cell.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=(8, 4))
            ttk.Label(desc_cell, text="Description", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            self.txt_description = tk.Text(desc_cell, height=4, wrap="word", bg="#242424", fg="white",
                                           insertbackground="white")
            self.txt_description.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
            desc_cell.rowconfigure(1, weight=1);
            desc_cell.columnconfigure(0, weight=1)

            syl_cell = ttk.Frame(form, style="Panel.TFrame")
            syl_cell.grid(row=3, column=2, sticky="nsew", padx=10, pady=(8, 4))
            ttk.Label(syl_cell, text="Syllabus", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            self.txt_syllabus = tk.Text(syl_cell, height=4, wrap="word", bg="#242424", fg="white",
                                        insertbackground="white")
            self.txt_syllabus.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
            syl_cell.rowconfigure(1, weight=1);
            syl_cell.columnconfigure(0, weight=1)

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

            self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings", yscrollcommand=vsb.set,
                                     xscrollcommand=hsb.set)
            vsb.config(command=self.tree.yview)
            hsb.config(command=self.tree.xview)
            self.tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")

            for col in self.columns:
                self.tree.heading(col, text=col)
                if col == "Row":
                    self.tree.column(col, width=60, anchor="center")
                elif col in ("CourseCode", "Duration"):
                    self.tree.column(col, width=100, anchor="center")
                elif col == "Cost":
                    self.tree.column(col, width=120, anchor="center")
                elif col == "Status":
                    self.tree.column(col, width=100, anchor="center")
                else:
                    self.tree.column(col, width=200, anchor="w")

            self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

            # --- ایجاد منوی کلیک راست (Context Menu) ---
            self.context_menu = tk.Menu(self.win, tearoff=0, bg="#1a1a1a", fg="white", font=font_sm)
            self.context_menu.add_command(label="Update Record", command=self._update)
            self.context_menu.add_command(label="Delete Record", command=self._delete)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Download Syllabus File", command=self._download_file)

            self.tree.bind("<Button-3>", self._show_context_menu)

            self._refresh_tree()
            self.win.after(100, lambda: paned.sashpos(0, int(H * 0.52)))

            if self._created_root:
                self.win.mainloop()

        except Exception as e:
            messagebox.showerror("Course Form Error", str(e), parent=self._msg_parent())

    # ---------- small UI builders ----------
    def _make_cell(self, parent, r, c, title):
        cell = ttk.Frame(parent, style="Panel.TFrame")
        cell.grid(row=r, column=c, sticky="ew", padx=10, pady=4)
        ttk.Label(cell, text=title, style="Form.TLabel").grid(row=0, column=0, sticky="w")
        return cell

    def _make_entry_cell(self, parent, r, c, title, var_key):
        cell = self._make_cell(parent, r, c, title)
        ttk.Entry(cell, textvariable=self.vars[var_key], style="Form.TEntry", width=26).grid(row=1, column=0,
                                                                                             sticky="w", pady=(3, 0))

    # ---------------- Context Menu ----------------
    def _show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            # انتخاب کردن ردیفی که روش کلیک راست شده
            self.tree.selection_set(iid)
            self._on_tree_select(None)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    # ---------------- CRUD ----------------
    def _get_form_data(self):
        raw_cost = (self.vars["Cost"].get() or "").strip()
        clean_cost = raw_cost.replace(",", "")

        return {
            "CourseCode": (self.vars["CourseCode"].get() or "").strip(),
            "CourseName": (self.vars["CourseName"].get() or "").strip(),
            "EnglishCourseName": (self.vars["EnglishCourseName"].get() or "").strip(),
            "Duration": (self.vars["Duration"].get() or "").strip(),
            "Cost": clean_cost,
            "Status": (self.vars["Status"].get() or "").strip(),
            "CourseCategory": (self.vars["CourseCategory"].get() or "").strip(),
            "PrerequisiteCourse": (self.vars["PrerequisiteCourse"].get() or "").strip(),
            "Description": self._get_text(self.txt_description),
            "Syllabus": self._get_text(self.txt_syllabus),
        }

    def _save(self):
        data = self._get_form_data()
        if not self._validate_form(data): return

        cat_id = int(self.category_name_to_id[data["CourseCategory"]])
        prereq_id = int(self.course_name_to_id.get(data["PrerequisiteCourse"], 0))
        prereq_id = None if prereq_id == 0 else prereq_id

        params = (
            int(data["CourseCode"]), data["CourseName"], data["EnglishCourseName"],
            data["Description"], int(data["Duration"]), data["Syllabus"],
            int(data["Cost"]), pyodbc.Binary(self.syllabus_file_bytes),
            data["Status"], int(cat_id), prereq_id
        )

        qmarks = ",".join(["?"] * len(params))
        rows, _ = self._db_query(f"EXEC dbo.InsertCourse {qmarks}", params)
        if rows is None or not rows: return

        new_id = rows[0][0]
        self.course_id_var.set(str(new_id))
        self._set_selection_state(True)
        messagebox.showinfo("Saved", f"Saved successfully. CourseID={new_id}", parent=self._msg_parent())
        self._refresh_tree()

    def _update(self):
        cid = (self.course_id_var.get() or "").strip()
        if not cid:
            messagebox.showwarning("Update", "Select a row first.", parent=self._msg_parent())
            return
        try:
            course_id = int(cid)
        except:
            return

        data = self._get_form_data()
        if not self._validate_form(data): return

        cat_id = int(self.category_name_to_id[data["CourseCategory"]])
        prereq_id = int(self.course_name_to_id.get(data["PrerequisiteCourse"], 0))
        prereq_id = None if prereq_id == 0 else prereq_id

        params = (
            int(course_id), int(data["CourseCode"]), data["CourseName"], data["EnglishCourseName"],
            data["Description"], int(data["Duration"]), data["Syllabus"], int(data["Cost"]),
            pyodbc.Binary(self.syllabus_file_bytes), data["Status"], int(cat_id), prereq_id
        )

        qmarks = ",".join(["?"] * len(params))
        ok = self._db_exec(f"EXEC dbo.UpdateCourse {qmarks}", params)
        if not ok: return
        messagebox.showinfo("Updated", "Updated successfully.", parent=self._msg_parent())
        self._refresh_tree()

    def _delete(self):
        cid = (self.course_id_var.get() or "").strip()
        if not cid:
            messagebox.showwarning("Delete", "Select a row first.", parent=self._msg_parent())
            return
        try:
            course_id = int(cid)
        except:
            return

        if not messagebox.askyesno("Confirm", f"Delete CourseID={course_id}?", parent=self._msg_parent()): return
        ok = self._db_exec("EXEC dbo.DeleteCourse ?", (course_id,))
        if not ok: return

        messagebox.showinfo("Deleted", "Deleted successfully.", parent=self._msg_parent())
        self._clear_form()
        self._refresh_tree()

    def _clear_form(self):
        self.course_id_var.set("")
        self.vars["CourseCode"].set("")
        self.vars["CourseName"].set("")
        self.vars["EnglishCourseName"].set("")
        self.vars["Duration"].set("")
        self.vars["Cost"].set("")
        self.vars["Status"].set("Active")
        self.vars["CourseCategory"].set("")
        self.vars["PrerequisiteCourse"].set("None")

        self._set_text(self.txt_description, "")
        self._set_text(self.txt_syllabus, "")
        self._remove_file()
        self._set_selection_state(False)

    # ---------------- tree/search ----------------
    def _refresh_tree(self):
        data = self._fetch_all_courses()
        self.tree.delete(*self.tree.get_children())
        self._rows_cache = {}

        for idx, d in enumerate(data, start=1):
            course_id = d.get("ID")
            if course_id is None: continue
            self._rows_cache[int(course_id)] = d

            cost_val = d.get("Cost", "")
            try:
                cost_str = f"{int(cost_val):,}" if cost_val else ""
            except:
                cost_str = str(cost_val)

            values = [
                str(idx), str(d.get("CourseCode", "") or ""), str(d.get("CourseName", "") or ""),
                str(d.get("EnglishCourseName", "") or ""), str(d.get("Duration", "") or ""),
                cost_str,  # فرمت پولی
                str(d.get("Status", "") or ""), str(d.get("Category", "") or ""),
                str(d.get("Prerequisite", "") or "None"),
            ]
            self.tree.insert("", "end", iid=str(course_id), values=values)

        if not (self.course_id_var.get() or "").strip():
            self._set_selection_state(False)

    def _search(self):
        q = (self.search_var.get() or "").strip()
        if not q:
            self._refresh_tree()
            return
        data = self._search_courses_db(q)
        self.tree.delete(*self.tree.get_children())
        self._rows_cache = {}

        for idx, d in enumerate(data, start=1):
            course_id = d.get("ID")
            if course_id is None: continue
            self._rows_cache[int(course_id)] = d

            cost_val = d.get("Cost", "")
            try:
                cost_str = f"{int(cost_val):,}" if cost_val else ""
            except:
                cost_str = str(cost_val)

            values = [
                str(idx), str(d.get("CourseCode", "") or ""), str(d.get("CourseName", "") or ""),
                str(d.get("EnglishCourseName", "") or ""), str(d.get("Duration", "") or ""),
                cost_str, str(d.get("Status", "") or ""), str(d.get("Category", "") or ""),
                str(d.get("Prerequisite", "") or "None"),
            ]
            self.tree.insert("", "end", iid=str(course_id), values=values)

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_tree()

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            self.course_id_var.set("")
            self._set_selection_state(False)
            return

        iid = sel[0]
        try:
            course_id = int(iid)
        except:
            return

        d = self._rows_cache.get(course_id)
        if not d: return

        self.course_id_var.set(str(course_id))

        self.vars["CourseCode"].set("" if d.get("CourseCode") is None else str(d.get("CourseCode")))
        self.vars["CourseName"].set("" if d.get("CourseName") is None else str(d.get("CourseName")))
        self.vars["EnglishCourseName"].set(
            "" if d.get("EnglishCourseName") is None else str(d.get("EnglishCourseName")))
        self.vars["Duration"].set("" if d.get("Duration") is None else str(d.get("Duration")))

        self.vars["Cost"].set("" if d.get("Cost") is None else str(d.get("Cost")))

        self.vars["Status"].set("" if d.get("Status") is None else str(d.get("Status")))

        cat_name = "" if d.get("Category") is None else str(d.get("Category"))
        self.vars["CourseCategory"].set(cat_name)
        if self.cmb_category: self.cmb_category.set(cat_name)

        prereq_name = "" if d.get("Prerequisite") is None else str(d.get("Prerequisite"))
        if not prereq_name.strip(): prereq_name = "None"
        self.vars["PrerequisiteCourse"].set(prereq_name)
        if self.cmb_prereq: self.cmb_prereq.set(prereq_name)

        self._set_text(self.txt_description, d.get("Description") or "")
        self._set_text(self.txt_syllabus, d.get("Syllabus") or "")

        try:
            rows, _ = self._db_query("SELECT SyllabusFile FROM dbo.Course WHERE ID=?", (course_id,))
            if rows and rows[0][0]:
                self.syllabus_file_bytes = rows[0][0]
                self.lbl_file_name.config(text="[Attached in Database]")
            else:
                self.syllabus_file_bytes = None
                self.lbl_file_name.config(text="No file attached")
        except Exception:
            self.syllabus_file_bytes = None
            self.lbl_file_name.config(text="File info unavailable")

        self._set_selection_state(True)