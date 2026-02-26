
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import date

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

from Model.UserModel import User_Model_class
from Model.ScoreModel import Score_Model_Class
from BusinessLogicLayer.Score_CRUD_BLL import Score_CRUD_BLL_Class


class ScoreForm:
    def __init__(self, user_param: User_Model_class, master: tk.Misc = None):
        self.user = user_param
        self.master = master
        self.win = None
        self._created_root = False

        self.bll = Score_CRUD_BLL_Class()

        self.search_var = None

        self.var_student = None
        self.var_course = None
        self.var_teacher = None
        self.var_term = None
        self.var_score = None

        self.cmb_student = None
        self.cmb_course = None
        self.cmb_teacher = None

        self.student_label_to_id = {}
        self.teacher_label_to_id = {}
        self.course_label_to_id = {}

        self.student_id_to_label = {}
        self.teacher_id_to_label = {}
        self.course_id_to_label = {}

        self.btn_save = None
        self.btn_update = None
        self.btn_delete = None
        self.btn_issue_cert = None

        self.tree = None
        self.context_menu = None

        self.selected_key = None

    # ---------------- UI helpers ----------------
    def _msg_parent(self):
        return self.win if self.win and self.win.winfo_exists() else None

    @staticmethod
    def _safe_int(s: str):
        s = (s or "").strip()
        if not s.isdigit():
            return None
        return int(s)

    def _set_selection_state(self, has_selection: bool):
        state = "normal" if has_selection else "disabled"
        if self.btn_update: self.btn_update.config(state=state)
        if self.btn_delete: self.btn_delete.config(state=state)
        if self.btn_issue_cert: self.btn_issue_cert.config(state=state)

        cmb_state = "disabled" if has_selection else "readonly"
        if self.cmb_student: self.cmb_student.config(state=cmb_state)
        if self.cmb_course: self.cmb_course.config(state=cmb_state)
        if self.cmb_teacher: self.cmb_teacher.config(state=cmb_state)

        if self.btn_save:
            self.btn_save.config(state="disabled" if has_selection else "normal")

    # ---------------- Context Menu ----------------
    def _show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self._on_tree_select(None)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    # ---------------- Generate Certificate (NEW) ----------------
    def _issue_certificate(self):
        if not self.selected_key:
            messagebox.showwarning("Warning", "Please select a student score first.", parent=self._msg_parent())
            return

        score_val = self._safe_int(self.var_score.get())
        if score_val is None or score_val < 60:  # فرض: نمره قبولی 60 است
            messagebox.showerror("Not Qualified",
                                 f"Student score is {score_val}. Minimum passing score is 60.\nCertificate cannot be issued.",
                                 parent=self._msg_parent())
            return

        student_name = self.var_student.get().split(" - ")[
            1] if " - " in self.var_student.get() else self.var_student.get()
        course_name = self.var_course.get().split(" - ")[1] if " - " in self.var_course.get() else self.var_course.get()
        teacher_name = self.var_teacher.get().split(" - ")[
            1] if " - " in self.var_teacher.get() else self.var_teacher.get()

        try:
            filename = f"Certificate_{student_name}_{course_name}.pdf"
            filename = "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_"))

            c = canvas.Canvas(filename, pagesize=landscape(A4))
            width, height = landscape(A4)

            c.setStrokeColorRGB(0.2, 0.4, 0.6)
            c.setLineWidth(10)
            c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

            c.setStrokeColorRGB(0.8, 0.6, 0.2)
            c.setLineWidth(3)
            c.rect(0.6 * inch, 0.6 * inch, width - 1.2 * inch, height - 1.2 * inch)

            c.setFont("Helvetica-Bold", 36)
            c.setFillColorRGB(0.1, 0.3, 0.5)
            c.drawCentredString(width / 2, height - 2 * inch, "CERTIFICATE OF COMPLETION")

            c.setFont("Helvetica", 14)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, height - 3 * inch, "This is to certify that")

            c.setFont("Helvetica-Bold", 28)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.drawCentredString(width / 2, height - 3.8 * inch, student_name.upper())

            c.setFont("Helvetica", 14)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, height - 4.6 * inch, "has successfully completed the course")

            c.setFont("Helvetica-Bold", 20)
            c.setFillColorRGB(0.1, 0.4, 0.2)
            c.drawCentredString(width / 2, height - 5.2 * inch, course_name)

            c.setFont("Helvetica", 12)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, height - 6 * inch, f"Final Score: {score_val} / 100")
            c.drawCentredString(width / 2, height - 6.3 * inch, f"Instructor: {teacher_name}")

            c.setFont("Helvetica", 12)
            c.drawString(1.5 * inch, 1.5 * inch, f"Date: {date.today().strftime('%Y-%m-%d')}")
            c.line(1.5 * inch, 1.4 * inch, 3.5 * inch, 1.4 * inch)

            c.drawString(width - 4 * inch, 1.5 * inch, "Authorized Signature:")
            c.line(width - 4 * inch, 1.4 * inch, width - 1.5 * inch, 1.4 * inch)

            c.showPage()
            c.save()

            messagebox.showinfo("Success", f"Certificate Generated Successfully:\n{filename}",
                                parent=self._msg_parent())
            try:
                os.startfile(os.path.normpath(filename))
            except:
                pass

        except Exception as e:
            messagebox.showerror("PDF Error", f"Could not generate certificate.\n{str(e)}", parent=self._msg_parent())

    # ---------------- load combo data ----------------
    def _load_students(self):
        rows, cols = self.bll.get_students_list()
        out = []
        for r in rows:
            sid = int(r[0])
            name = str(r[1]).strip()
            label = f"{sid} - {name}"
            out.append((sid, label))
        out.sort(key=lambda x: x[0])

        self.student_label_to_id = {lbl: sid for sid, lbl in out}
        self.student_id_to_label = {sid: lbl for sid, lbl in out}

    def _load_teachers(self):
        rows, cols = self.bll.get_teachers_list()
        out = []
        for r in rows:
            tid = int(r[0])
            name = str(r[1]).strip()
            label = f"{tid} - {name}"
            out.append((tid, label))
        out.sort(key=lambda x: x[0])

        self.teacher_label_to_id = {lbl: tid for tid, lbl in out}
        self.teacher_id_to_label = {tid: lbl for tid, lbl in out}

    def _load_courses(self):
        rows, cols = self.bll.get_courses_list()
        out = []
        for r in rows:
            cid = int(r[0])
            name = str(r[1]).strip()
            label = f"{cid} - {name}"
            out.append((cid, label))
        out.sort(key=lambda x: x[0])

        self.course_label_to_id = {lbl: cid for cid, lbl in out}
        self.course_id_to_label = {cid: lbl for cid, lbl in out}

    # ---------------- fetch rows ----------------
    def _fetch_all_scores(self):
        rows, cols = self.bll.get_all_scores()
        out = []
        for r in rows:
            d = {
                "StudentID": int(r[0]),
                "StudentName": str(r[1]),
                "CourseID": int(r[2]),
                "CourseName": str(r[3]),
                "TeacherID": int(r[4]),
                "TeacherName": str(r[5]),
                "TermNumber": int(r[6]),
                "Score": int(r[7]),
            }
            out.append(d)
        return out

    def _search_scores(self, q: str):
        rows, cols = self.bll.search_scores(q)
        out = []
        for r in rows:
            d = {
                "StudentID": int(r[0]),
                "StudentName": str(r[1]),
                "CourseID": int(r[2]),
                "CourseName": str(r[3]),
                "TeacherID": int(r[4]),
                "TeacherName": str(r[5]),
                "TermNumber": int(r[6]),
                "Score": int(r[7]),
            }
            out.append(d)
        return out

    # ---------------- validate ----------------
    def _validate_form(self):
        if not self.var_student.get().strip():
            messagebox.showerror("Validation", "Please select Student.", parent=self._msg_parent())
            return False
        if not self.var_course.get().strip():
            messagebox.showerror("Validation", "Please select Course.", parent=self._msg_parent())
            return False
        if not self.var_teacher.get().strip():
            messagebox.showerror("Validation", "Please select Teacher.", parent=self._msg_parent())
            return False

        term = self._safe_int(self.var_term.get())
        if term is None or term <= 0:
            messagebox.showerror("Validation", "TermNumber must be a positive number.", parent=self._msg_parent())
            return False

        score = self._safe_int(self.var_score.get())
        if score is None or score < 0 or score > 100:  # در آموزش معمولا تا 100 است
            messagebox.showerror("Validation", "Score must be number between 0 and 100.", parent=self._msg_parent())
            return False

        if self.var_student.get() not in self.student_label_to_id:
            messagebox.showerror("Validation", "Invalid Student selection.", parent=self._msg_parent())
            return False
        if self.var_course.get() not in self.course_label_to_id:
            messagebox.showerror("Validation", "Invalid Course selection.", parent=self._msg_parent())
            return False
        if self.var_teacher.get() not in self.teacher_label_to_id:
            messagebox.showerror("Validation", "Invalid Teacher selection.", parent=self._msg_parent())
            return False

        return True

    # ===================== UI main =====================
    def score_form_load(self):
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

        self.win.title("Score Management")
        self.win.configure(bg="#111111")

        self.win.update_idletasks()
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        W = max(1200, int(sw * 0.88))
        H = max(760, int(sh * 0.82))
        x = sw // 2 - W // 2
        y = sh // 2 - H // 2
        self.win.geometry(f"{W}x{H}+{x}+{y}")
        self.win.minsize(1200, 760)

        # vars
        self.search_var = tk.StringVar(master=self.win, value="")

        self.var_student = tk.StringVar(master=self.win, value="")
        self.var_course = tk.StringVar(master=self.win, value="")
        self.var_teacher = tk.StringVar(master=self.win, value="")
        self.var_term = tk.StringVar(master=self.win, value="")
        self.var_score = tk.StringVar(master=self.win, value="")

        # load combos
        self._load_students()
        self._load_courses()
        self._load_teachers()

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

        fn = (getattr(self.user, "firstname", "") or "").strip()
        ln = (getattr(self.user, "lastname", "") or "").strip()

        ttk.Label(header, text="Student Scores", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text=f"User: {fn} {ln}".strip(), style="Info.TLabel").pack(side="left", padx=(12, 0))

        ttk.Separator(root, orient="horizontal").pack(fill="x", pady=(0, 10))

        paned = ttk.Panedwindow(root, orient="vertical")
        paned.pack(fill="both", expand=True)

        top_panel = ttk.Frame(paned, style="Panel.TFrame")
        bottom_panel = ttk.Frame(paned, style="Panel.TFrame")
        paned.add(top_panel, weight=3)
        paned.add(bottom_panel, weight=6)

        # toolbar
        toolbar = ttk.Frame(top_panel, style="Panel.TFrame")
        toolbar.pack(fill="x", padx=14, pady=(12, 6))

        self.btn_save = ttk.Button(toolbar, text="Save", style="Primary.TButton", command=self._save)
        self.btn_save.grid(row=0, column=0, padx=(0, 8))

        self.btn_update = ttk.Button(toolbar, text="Update", style="Primary.TButton", command=self._update)
        self.btn_update.grid(row=0, column=1, padx=(0, 8))

        self.btn_delete = ttk.Button(toolbar, text="Delete", style="Primary.TButton", command=self._delete)
        self.btn_delete.grid(row=0, column=2, padx=(0, 8))

        ttk.Button(toolbar, text="Clear", style="Primary.TButton", command=self._clear_form).grid(row=0, column=3,
                                                                                                  padx=(0, 8))
        ttk.Button(toolbar, text="Refresh", style="Primary.TButton", command=self._refresh_tree).grid(row=0, column=4,
                                                                                                      padx=(0, 8))

        self.btn_issue_cert = ttk.Button(toolbar, text="Issue Certificate", style="Primary.TButton",
                                         command=self._issue_certificate)
        self.btn_issue_cert.grid(row=0, column=5, padx=(0, 8))

        ttk.Button(toolbar, text="Close", style="Primary.TButton", command=self.win.destroy).grid(row=0, column=6,
                                                                                                  padx=(0, 8))

        self._set_selection_state(False)

        # form fields
        fields = ttk.Frame(top_panel, style="Panel.TFrame")
        fields.pack(fill="both", expand=True, padx=14, pady=(6, 14))

        for c in range(3):
            fields.columnconfigure(c, weight=1)

        form_items = [
            ("Student", self._make_student_widget),
            ("Course", self._make_course_widget),
            ("Teacher", self._make_teacher_widget),
            ("Term Number", self._make_term_widget),
            ("Score (0-100)", self._make_score_widget),
        ]

        for i, (title, widget_fn) in enumerate(form_items):
            r = i // 3
            c = i % 3
            cell = ttk.Frame(fields, style="Panel.TFrame")
            cell.grid(row=r, column=c, sticky="ew", padx=10, pady=6)
            ttk.Label(cell, text=title, style="Form.TLabel").grid(row=0, column=0, sticky="w")
            widget_fn(cell)

        # bottom: search + tree
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
        ent_search.bind("<Return>", lambda _e: self._search())

        tree_frame = ttk.Frame(bottom_panel, style="Panel.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ["Row", "Student", "Course", "Teacher", "TermNumber", "Score", "Status"]
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        for col in columns:
            self.tree.heading(col, text=col)
            if col in ("Row", "TermNumber", "Score", "Status"):
                self.tree.column(col, width=90, anchor="center")
            else:
                self.tree.column(col, width=220, anchor="w")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # کلیک راست
        self.context_menu = tk.Menu(self.win, tearoff=0, bg="#1a1a1a", fg="white", font=font_sm)
        self.context_menu.add_command(label="Update Score", command=self._update)
        self.context_menu.add_command(label="Delete Record", command=self._delete)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Issue Certificate", command=self._issue_certificate)
        self.tree.bind("<Button-3>", self._show_context_menu)

        self._refresh_tree()
        self.win.after(60, lambda: paned.sashpos(0, int(H * 0.40)))

        if self._created_root:
            self.win.mainloop()

    # ---------- widget builders ----------
    def _make_student_widget(self, parent):
        self.cmb_student = ttk.Combobox(
            parent,
            textvariable=self.var_student,
            state="readonly",
            values=list(self.student_label_to_id.keys()),
            width=30
        )
        self.cmb_student.grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _make_course_widget(self, parent):
        self.cmb_course = ttk.Combobox(
            parent,
            textvariable=self.var_course,
            state="readonly",
            values=list(self.course_label_to_id.keys()),
            width=30
        )
        self.cmb_course.grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _make_teacher_widget(self, parent):
        self.cmb_teacher = ttk.Combobox(
            parent,
            textvariable=self.var_teacher,
            state="readonly",
            values=list(self.teacher_label_to_id.keys()),
            width=30
        )
        self.cmb_teacher.grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _make_term_widget(self, parent):
        ttk.Entry(parent, textvariable=self.var_term, style="Form.TEntry", width=32).grid(row=1, column=0, sticky="w",
                                                                                          pady=(4, 0))

    def _make_score_widget(self, parent):
        ttk.Entry(parent, textvariable=self.var_score, style="Form.TEntry", width=32).grid(row=1, column=0, sticky="w",
                                                                                           pady=(4, 0))

    # ===================== CRUD =====================
    def _save(self):
        if not self._validate_form():
            return

        student_id = self.student_label_to_id[self.var_student.get()]
        course_id = self.course_label_to_id[self.var_course.get()]
        teacher_id = self.teacher_label_to_id[self.var_teacher.get()]
        term_number = int(self.var_term.get())
        score = int(self.var_score.get())

        obj = Score_Model_Class(student_id, course_id, teacher_id, term_number, score)

        try:
            self.bll.insert_score(obj)
            messagebox.showinfo("Saved", "Score saved successfully.", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())

    def _update(self):
        if not self.selected_key:
            messagebox.showwarning("Update", "Select a row first.", parent=self._msg_parent())
            return

        score_val = self._safe_int(self.var_score.get())
        if score_val is None or score_val < 0 or score_val > 100:
            messagebox.showerror("Validation", "Score must be number between 0 and 100.", parent=self._msg_parent())
            return

        student_id, course_id, teacher_id, term_number = self.selected_key

        obj = Score_Model_Class(student_id, course_id, teacher_id, term_number, score_val)

        try:
            self.bll.update_score(obj)
            messagebox.showinfo("Updated", "Score updated successfully.", parent=self._msg_parent())
            self._refresh_tree()
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())

    def _delete(self):
        if not self.selected_key:
            messagebox.showwarning("Delete", "Select a row first.", parent=self._msg_parent())
            return

        student_id, course_id, teacher_id, term_number = self.selected_key

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this score record?",
                                   parent=self._msg_parent()):
            return

        try:
            self.bll.delete_score(student_id, course_id, teacher_id, term_number)
            messagebox.showinfo("Deleted", "Deleted successfully.", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self._msg_parent())

    def _clear_form(self):
        self.var_student.set("")
        self.var_course.set("")
        self.var_teacher.set("")
        self.var_term.set("")
        self.var_score.set("")
        self.selected_key = None

        if self.cmb_student: self.cmb_student.config(state="readonly")
        if self.cmb_course: self.cmb_course.config(state="readonly")
        if self.cmb_teacher: self.cmb_teacher.config(state="readonly")

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

        self._set_selection_state(False)

    # ===================== Tree/Search =====================
    def _refresh_tree(self):
        data = self._fetch_all_scores()
        self.tree.delete(*self.tree.get_children())

        for i, d in enumerate(data, start=1):
            iid = f"{d['StudentID']}|{d['CourseID']}|{d['TeacherID']}|{d['TermNumber']}"

            score_val = d["Score"]
            status = "Pass" if score_val >= 60 else "Fail"

            values = [
                i,
                f"{d['StudentName']}",
                f"{d['CourseName']}",
                f"{d['TeacherName']}",
                d["TermNumber"],
                score_val,
                status
            ]
            self.tree.insert("", "end", iid=iid, values=values)

        if not self.selected_key:
            self._set_selection_state(False)

    def _search(self):
        q = (self.search_var.get() or "").strip()
        if not q:
            self._refresh_tree()
            return

        data = self._search_scores(q)
        self.tree.delete(*self.tree.get_children())

        for i, d in enumerate(data, start=1):
            iid = f"{d['StudentID']}|{d['CourseID']}|{d['TeacherID']}|{d['TermNumber']}"

            score_val = d["Score"]
            status = "Pass" if score_val >= 60 else "Fail"

            values = [
                i,
                f"{d['StudentName']}",
                f"{d['CourseName']}",
                f"{d['TeacherName']}",
                d["TermNumber"],
                score_val,
                status
            ]
            self.tree.insert("", "end", iid=iid, values=values)

        self._set_selection_state(False)
        self.selected_key = None

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_tree()

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            self.selected_key = None
            self._set_selection_state(False)
            return

        iid = sel[0]
        try:
            sid, cid, tid, term = iid.split("|")
            sid, cid, tid, term = int(sid), int(cid), int(tid), int(term)
            self.selected_key = (sid, cid, tid, term)
        except Exception:
            self.selected_key = None
            self._set_selection_state(False)
            return

        self.var_student.set(self.student_id_to_label.get(sid, ""))
        self.var_course.set(self.course_id_to_label.get(cid, ""))
        self.var_teacher.set(self.teacher_id_to_label.get(tid, ""))
        self.var_term.set(str(term))

        item = self.tree.item(iid)
        vals = item.get("values", [])
        if len(vals) >= 6:
            self.var_score.set(str(vals[5]))

        self._set_selection_state(True)