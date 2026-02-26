
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pyodbc
from datetime import datetime, date
import os
import io
import csv  # برای خروجی سریع CSV / Excel

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageTk

from Model.UserModel import User_Model_class


class EmployeeForm:
    def __init__(self, user_param: User_Model_class, master: tk.Misc = None):
        self.user = user_param
        self.master = master
        self.win = None
        self._created_root = False

        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_here;"
            "Database=SematecLearningManagementSystem;"
            "UID=sa;"
            "PWD=your_password_here"
        )

        self.search_var = None
        self.person_id_var = None
        self.vars = {}
        self.date_widgets = {}

        self.cmb_education = None
        self.cmb_job = None
        self.cmb_department = None
        self.cmb_manager = None

        self.btn_update = None
        self.btn_delete = None
        self.btn_print_contract = None
        self.btn_export_excel = None

        # mappings
        self.education_name_to_id = {}
        self.education_id_to_name = {}

        self.job_name_to_id = {}
        self.job_id_to_name = {}

        self.department_name_to_id = {}
        self.department_id_to_name = {}

        self.manager_name_to_id = {}
        self.manager_id_to_name = {}

        self.date_fields = {"Birthdate", "Startdate", "Hiredate"}

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

            ("Manager", "Manager"),
            ("TotalChildren", "Total Children"),
            ("Startdate", "Startdate"),
            ("InsuranceNumber", "Insurance Number"),
            ("AccountNumber", "Account Number"),
            ("Hiredate", "Hiredate"),

            ("Department", "Department"),
            ("Job", "Job"),
            ("PhotoPath", "Photo"),
        ]

        self.tree_columns = [
            "Row",
            "FirstName", "LastName", "Birthdate", "MaritalStatus",
            "NationalCode", "Mobile", "Address", "Gender", "EmailAddress",
            "Education", "Manager",
            "TotalChildren", "Startdate",
            "InsuranceNumber", "AccountNumber", "Hiredate",
            "Department", "JobTitle"
        ]

        self.tree = None
        self.context_menu = None
        self._cache_by_personid = {}

        self._guard = {
            "FirstName": False, "LastName": False, "NationalCode": False,
            "Mobile": False, "InsuranceNumber": False, "AccountNumber": False
        }

        # photo variables
        self.photo_label = None
        self.photo_image = None
        self.current_photo_bytes = None

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

    # ---------------- load lists ----------------
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

    def _load_job_list(self):
        rows, cols = self._db_query("SELECT ID, JobTitle FROM dbo.Job ORDER BY ID")
        if rows is None:
            self.job_name_to_id = {}
            self.job_id_to_name = {}
            return
        out = []
        if cols:
            for r in rows:
                rd = self._row_to_named_dict(r, cols)
                jid = self._get_any(rd, "ID")
                title = self._get_any(rd, "JobTitle")
                if jid is None or title is None:
                    continue
                t = str(title).strip()
                if t:
                    out.append((int(jid), t))
        else:
            for r in rows:
                out.append((int(r[0]), str(r[1]).strip()))
        out.sort(key=lambda x: x[0])
        self.job_name_to_id = {title: jid for jid, title in out}
        self.job_id_to_name = {jid: title for title, jid in self.job_name_to_id.items()}

    def _load_department_list(self):
        rows, cols = self._db_query("SELECT ID, EnglishDepartmentName FROM dbo.Department ORDER BY ID")
        if rows is None:
            self.department_name_to_id = {}
            self.department_id_to_name = {}
            return
        out = []
        if cols:
            for r in rows:
                rd = self._row_to_named_dict(r, cols)
                did = self._get_any(rd, "ID")
                name = self._get_any(rd, "EnglishDepartmentName", "DepartmentName")
                if did is None or name is None:
                    continue
                name = str(name).strip()
                if name:
                    out.append((int(did), name))
        else:
            for r in rows:
                out.append((int(r[0]), str(r[1]).strip()))
        out.sort(key=lambda x: x[0])
        self.department_name_to_id = {name: did for did, name in out}
        self.department_id_to_name = {did: name for name, did in self.department_name_to_id.items()}

    def _load_manager_list(self):
        sql = """
        SELECT p.ID, p.FirstName, p.LastName
        FROM dbo.Employee e
        INNER JOIN dbo.Person p ON p.ID = e.PersonID
        ORDER BY p.FirstName, p.LastName
        """
        rows, cols = self._db_query(sql)
        if rows is None:
            self.manager_name_to_id = {}
            self.manager_id_to_name = {}
            return
        out = []
        if cols:
            for r in rows:
                rd = self._row_to_named_dict(r, cols)
                pid = self._get_any(rd, "ID", "PersonID")
                fn = self._get_any(rd, "FirstName")
                ln = self._get_any(rd, "LastName")
                if pid is None:
                    continue
                full = f"{str(fn or '').strip()} {str(ln or '').strip()}".strip()
                if full:
                    out.append((int(pid), full))
        else:
            for r in rows:
                pid = int(r[0])
                full = f"{str(r[1]).strip()} {str(r[2]).strip()}".strip()
                if full:
                    out.append((pid, full))
        out.sort(key=lambda x: x[1].lower())
        self.manager_name_to_id = {name: pid for pid, name in out}
        self.manager_id_to_name = {pid: name for name, pid in self.manager_name_to_id.items()}

    # ---------------- fetch employees ----------------
    def _normalize_photo_from_db(self, value):
        """Make sure photo coming from pyodbc is bytes or None."""
        if value is None:
            return None
        try:
            if isinstance(value, memoryview):
                return value.tobytes()
            if isinstance(value, (bytes, bytearray)):
                return bytes(value)
            return bytes(value)
        except Exception:
            return None

    def _employees_from_rows(self, rows, cols):
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
                    "EducationID": self._get_any(rd, "EducationID"),
                    "ManagerID": self._get_any(rd, "ManagerID"),
                    "TotalChildren": self._get_any(rd, "TotalChildren"),
                    "Startdate": self._get_any(rd, "Startdate"),
                    "InsuranceNumber": self._get_any(rd, "InsuranceNumber"),
                    "AccountNumber": self._get_any(rd, "AccountNumber"),
                    "Hiredate": self._get_any(rd, "Hiredate"),
                    "DepartmentID": self._get_any(rd, "DepartmentID"),
                    "JobID": self._get_any(rd, "JobID"),
                }
                photo_raw = self._get_any(
                    rd,
                    "Photo",
                    "EmployeePhoto",
                    "PhotoData",
                    "Image"
                )
                d["Photo"] = self._normalize_photo_from_db(photo_raw)
            else:
                d = {
                    "PersonID": r[0], "FirstName": r[1], "LastName": r[2], "Birthdate": r[3],
                    "MaritalStatus": r[4], "NationalCode": r[5], "Mobile": r[6], "Address": r[7],
                    "Gender": r[8], "EmailAddress": r[9], "EducationID": r[10], "ManagerID": r[11],
                    "TotalChildren": r[12], "Startdate": r[13], "InsuranceNumber": r[14],
                    "AccountNumber": r[15], "Hiredate": r[16], "DepartmentID": r[17], "JobID": r[18],
                }
                try:
                    d["Photo"] = self._normalize_photo_from_db(r[19])
                except Exception:
                    d["Photo"] = None

            try:
                eid = d.get("EducationID")
                d["Education"] = self.education_id_to_name.get(int(eid), "") if eid is not None else ""
            except Exception:
                d["Education"] = ""

            try:
                jid = d.get("JobID")
                d["JobTitle"] = self.job_id_to_name.get(int(jid), "") if jid is not None else ""
            except Exception:
                d["JobTitle"] = ""

            try:
                did = d.get("DepartmentID")
                d["Department"] = self.department_id_to_name.get(int(did), "") if did is not None else ""
            except Exception:
                d["Department"] = ""

            try:
                mid = d.get("ManagerID")
                d["Manager"] = self.manager_id_to_name.get(int(mid), "") if mid is not None else ""
            except Exception:
                d["Manager"] = ""

            out.append(d)
        return out

    def _fetch_all_employees(self):
        rows, cols = self._db_query("EXEC dbo.GetAllEmployees")
        if rows is None:
            return []
        return self._employees_from_rows(rows, cols)

    def _search_employees_db(self, q: str):
        rows, cols = self._db_query("EXEC dbo.SearchEmployees ?", (q,))
        if rows is None:
            return []
        return self._employees_from_rows(rows, cols)

    # ---------------- parse/validate ----------------
    def _parse_date(self, s: str):
        s = (s or "").strip()
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _parse_int(self, s: str, allow_none=True):
        s = (s or "").strip()
        if s == "":
            return None if allow_none else 0
        if not s.isdigit():
            return None
        return int(s)

    def _filter_alpha_max(self, key: str, max_len: int):
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
        p = self._msg_parent()
        if not data["FirstName"] or not data["LastName"]:
            messagebox.showerror("Validation", "FirstName and LastName are required.", parent=p)
            return False
        if len(data["NationalCode"]) != 10:
            messagebox.showerror("Validation", "NationalCode must be exactly 10 digits.", parent=p)
            return False
        if len(data["Mobile"]) != 11:
            messagebox.showerror("Validation", "Mobile must be exactly 11 digits.", parent=p)
            return False
        if len(data["InsuranceNumber"]) != 7:
            messagebox.showerror("Validation", "InsuranceNumber must be exactly 7 digits.", parent=p)
            return False
        if len(data["AccountNumber"]) != 16:
            messagebox.showerror("Validation", "AccountNumber must be exactly 16 digits.", parent=p)
            return False
        for df in self.date_fields:
            if self._parse_date(data[df]) is None:
                messagebox.showerror("Validation", f"{df} must be valid (YYYY-MM-DD).", parent=p)
                return False
        if data["MaritalStatus"] not in ("Single", "Married"):
            messagebox.showerror("Validation", "MaritalStatus must be Single or Married.", parent=p)
            return False
        if data["Gender"] not in ("Male", "Female"):
            messagebox.showerror("Validation", "Gender must be Male or Female.", parent=p)
            return False
        if data["Education"] not in self.education_name_to_id:
            messagebox.showerror("Validation", "Please select Education.", parent=p)
            return False
        if data["Job"] not in self.job_name_to_id:
            messagebox.showerror("Validation", "Please select Job.", parent=p)
            return False
        if data["Department"] not in self.department_name_to_id:
            messagebox.showerror("Validation", "Please select Department.", parent=p)
            return False
        if self._parse_int(data["TotalChildren"], allow_none=False) is None:
            messagebox.showerror("Validation", "TotalChildren must be numeric.", parent=p)
            return False
        return True

    def _set_selection_state(self, has_selection: bool):
        state = "normal" if has_selection else "disabled"
        if self.btn_update:
            self.btn_update.config(state=state)
        if self.btn_delete:
            self.btn_delete.config(state=state)
        if self.btn_print_contract:
            self.btn_print_contract.config(state=state)

    # ---------------- PHOTO logic ----------------
    def _browse_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")],
            parent=self._msg_parent(),
        )
        if file_path:
            self.vars["PhotoPath"].set(file_path)
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                self.current_photo_bytes = bytes(data)
                self._update_photo_preview_from_bytes(self.current_photo_bytes)
            except Exception as e:
                messagebox.showerror("File Error", str(e), parent=self._msg_parent())

    def _clear_photo(self):
        self.vars["PhotoPath"].set("")
        self.current_photo_bytes = None
        self._update_photo_preview_from_bytes(None)

    def _update_photo_preview_from_bytes(self, photo_bytes):
        """ آپدیت عکس با رفع مشکل ابعاد مینیاتوری """
        if not self.photo_label:
            return

        if not photo_bytes:
            self.photo_image = None
            # وقتی عکسی نیست، سایز لیبل بر اساس تعداد کاراکتر متنی خواهد بود
            self.photo_label.config(image="", text="No Photo", width=18, height=9)
            return

        try:
            if isinstance(photo_bytes, memoryview):
                photo_bytes = photo_bytes.tobytes()
            elif not isinstance(photo_bytes, (bytes, bytearray)):
                photo_bytes = bytes(photo_bytes)

            img = Image.open(io.BytesIO(photo_bytes))

            # تغییر سایز تصویر به 140x150 پیکسل
            img.thumbnail((140, 150), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(img)

            # نکته طلایی: وقتی تصویر ست می‌شود، مقادیر width و height به پیکسل تفسیر می‌شوند
            # پس برای جلوگیری از کوچک شدن کادر، سایز پیکسلی به آن می‌دهیم
            self.photo_label.config(image=self.photo_image, text="", width=140, height=150)

            # نگه داشتن رفرنس برای جلوگیری از حذف توسط Garbage Collector
            self.photo_label.image = self.photo_image

        except Exception as e:
            self.photo_image = None
            self.photo_label.config(image="", text="Photo error", width=18, height=9)
            print("Preview Error:", e)

    # ---------------- CONTRACT PDF ----------------
    def _print_contract(self):
        pid = (self.person_id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Contract", "Please select an employee first.", parent=self._msg_parent())
            return
        person_id = int(pid)
        data = self._cache_by_personid.get(person_id)
        if not data:
            return

        try:
            filename = f"Employee_Contract_{data['FirstName']}_{data['LastName']}.pdf"
            filename = "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_"))

            c_pdf = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            margin = 40

            c_pdf.setFont("Helvetica-Bold", 18)
            c_pdf.drawCentredString(width / 2, height - margin, "EMPLOYMENT AGREEMENT")

            photo_bytes = self.current_photo_bytes
            if not photo_bytes:
                photo_bytes = self._normalize_photo_from_db(data.get("Photo"))

            if photo_bytes:
                try:
                    if isinstance(photo_bytes, memoryview):
                        photo_bytes = photo_bytes.tobytes()
                    elif not isinstance(photo_bytes, (bytes, bytearray)):
                        photo_bytes = bytes(photo_bytes)

                    pil_img = Image.open(io.BytesIO(photo_bytes))
                    if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
                        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                        if pil_img.mode == "P":
                            pil_img = pil_img.convert("RGBA")
                        bg.paste(pil_img, mask=pil_img.split()[3])
                        pil_img = bg
                    elif pil_img.mode != "RGB":
                        pil_img = pil_img.convert("RGB")

                    img_reader = ImageReader(pil_img)
                    img_w, img_h = 100, 120
                    c_pdf.drawImage(
                        img_reader,
                        width - margin - img_w,
                        height - margin - img_h - 20,
                        width=img_w,
                        height=img_h,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
                except Exception as e:
                    print("Could not embed image in PDF:", e)

            y = height - margin - 80
            c_pdf.setFont("Helvetica", 10)
            c_pdf.drawString(margin, y, f"Date: {date.today().strftime('%Y-%m-%d')}")
            y -= 30

            text = c_pdf.beginText(margin, y)
            text.setFont("Helvetica", 11)

            text.textLine(f"This agreement is made between the Company and {data['FirstName']} {data['LastName']}.")
            text.textLine("")
            text.textLine("Employee Details:")
            text.textLine(f"  - National Code: {data['NationalCode']}")
            text.textLine(f"  - Mobile: {data['Mobile']}")
            text.textLine(f"  - Department: {data['Department']}")
            text.textLine(f"  - Job Title: {data['JobTitle']}")
            text.textLine(f"  - Insurance No: {data['InsuranceNumber']}")
            text.textLine(f"  - Hire Date: {data['Hiredate']}")
            text.textLine("")
            text.textLine("Terms and Conditions:")
            text.textLine("  1. The employee agrees to perform the duties of the specified Job Title.")
            text.textLine("  2. The company agrees to pay the salary according to HR policies.")
            text.textLine("  3. Working hours and leave are determined by the Department manager.")
            text.textLine("")
            text.textLine("This contract is legally binding upon signature.")
            c_pdf.drawText(text)

            sig_y = 120
            c_pdf.setFont("Helvetica", 11)
            c_pdf.drawString(margin, sig_y, "Company Signature:")
            c_pdf.line(margin, sig_y - 5, margin + 200, sig_y - 5)

            c_pdf.drawString(width / 2, sig_y, "Employee Signature:")
            c_pdf.line(width / 2, sig_y - 5, width / 2 + 200, sig_y - 5)

            c_pdf.showPage()
            c_pdf.save()

            messagebox.showinfo("Contract", f"PDF contract generated:\n{filename}", parent=self._msg_parent())
            try:
                os.startfile(os.path.normpath(filename))
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Contract Error", str(e), parent=self._msg_parent())

    # ---------------- EXPORT EXCEL ----------------
    def _export_excel(self):
        if not self.tree:
            return
        row_ids = self.tree.get_children()
        if not row_ids:
            messagebox.showwarning("Export", "There is no data to export.", parent=self._msg_parent())
            return

        file_path = filedialog.asksaveasfilename(
            parent=self._msg_parent(),
            title="Export to Excel",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Workbook", "*.xlsx"),
                ("CSV (Excel)", "*.csv"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(".csv"):
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(self.tree_columns)
                    for iid in row_ids:
                        vals = list(self.tree.item(iid, "values"))
                        writer.writerow(vals)
            else:
                try:
                    from openpyxl import Workbook
                except ImportError:
                    messagebox.showerror(
                        "Export",
                        "openpyxl is not installed.\n"
                        "Install it with 'pip install openpyxl' or save as CSV.",
                        parent=self._msg_parent(),
                    )
                    return

                wb = Workbook()
                ws = wb.active
                ws.title = "Employees"
                ws.append(self.tree_columns)
                for iid in row_ids:
                    vals = list(self.tree.item(iid, "values"))
                    ws.append(vals)
                wb.save(file_path)

            messagebox.showinfo("Export", f"Data exported to:\n{file_path}", parent=self._msg_parent())
            try:
                os.startfile(os.path.normpath(file_path))
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Export Error", str(e), parent=self._msg_parent())

    # ===================== Context Menu =====================
    def _show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self._on_tree_select(None)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    # ===================== UI Build =====================
    def employee_form_load(self):
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

            self.win.title("Employee CRUD")
            self.win.configure(bg="#111111")
            self.win.update_idletasks()
            sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            W, H = max(1300, int(sw * 0.95)), max(860, int(sh * 0.9))
            x, y = sw // 2 - W // 2, sh // 2 - H // 2
            self.win.geometry(f"{W}x{H}+{x}+{y}")
            self.win.minsize(1280, 860)

            self.search_var = tk.StringVar(master=self.win, value="")
            self.person_id_var = tk.StringVar(master=self.win, value="")
            for key, _ in self.form_fields:
                self.vars[key] = tk.StringVar(master=self.win, value="")

            self.vars["MaritalStatus"].set("Single")
            self.vars["Gender"].set("Male")

            self.vars["FirstName"].trace_add("write", lambda *_: self._filter_alpha_max("FirstName", 20))
            self.vars["LastName"].trace_add("write", lambda *_: self._filter_alpha_max("LastName", 50))
            self.vars["NationalCode"].trace_add("write", lambda *_: self._filter_digits_max("NationalCode", 10))
            self.vars["Mobile"].trace_add("write", lambda *_: self._filter_digits_max("Mobile", 11))
            self.vars["InsuranceNumber"].trace_add("write", lambda *_: self._filter_digits_max("InsuranceNumber", 7))
            self.vars["AccountNumber"].trace_add("write", lambda *_: self._filter_digits_max("AccountNumber", 16))

            self._load_education_list()
            self._load_job_list()
            self._load_department_list()
            self._load_manager_list()

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
            style.configure("Photo.TFrame", background="#2a2a2a")
            style.configure("Title.TLabel", background="#111111", foreground="white", font=font_title)
            style.configure("Info.TLabel", background="#111111", foreground="#bdbdbd", font=font_sm)
            style.configure("Form.TLabel", background="#1a1a1a", foreground="#e6e6e6", font=font_sm_b)
            style.configure("Value.TLabel", background="#1a1a1a", foreground="white", font=font_sm_b)
            style.configure(
                "Form.TEntry",
                fieldbackground="#242424",
                background="#242424",
                foreground="white",
                padding=4,
                font=font_sm,
            )
            style.configure("Primary.TButton", padding=(10, 7), font=font_sm_b)
            style.configure("Small.TButton", padding=(4, 2), font=("Segoe UI", 8))
            style.configure("Dark.TRadiobutton", background="#1a1a1a", foreground="white", font=font_sm_b)
            style.configure(
                "Treeview",
                background="#1f1f1f",
                fieldbackground="#1f1f1f",
                foreground="white",
                rowheight=24,
                borderwidth=0,
                font=font_sm,
            )
            style.configure("Treeview.Heading", background="#2a2a2a", foreground="white", font=font_sm_b)
            style.map("Treeview", background=[("selected", "#3a3a3a")])

            root = ttk.Frame(self.win, style="Root.TFrame")
            root.pack(fill="both", expand=True, padx=16, pady=16)

            header = ttk.Frame(root, style="Root.TFrame")
            header.pack(fill="x", pady=(0, 10))

            fn = (self.user.firstname or "").strip()
            ln = (self.user.lastname or "").strip()
            ttk.Label(header, text="Employee Management", style="Title.TLabel").pack(side="left")
            ttk.Label(header, text=f"User: {fn} {ln}".strip(), style="Info.TLabel").pack(side="left", padx=(12, 0))
            ttk.Separator(root, orient="horizontal").pack(fill="x", pady=(0, 10))

            top_h = max(440, int(H * 0.46))
            top_panel = ttk.Frame(root, style="Panel.TFrame", height=top_h)
            top_panel.pack(fill="x")
            top_panel.pack_propagate(False)

            bottom_panel = ttk.Frame(root, style="Panel.TFrame")
            bottom_panel.pack(fill="both", expand=True, pady=(10, 0))

            toolbar = ttk.Frame(top_panel, style="Panel.TFrame")
            toolbar.pack(fill="x", padx=14, pady=(12, 6))

            ttk.Label(toolbar, text="PersonID:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(toolbar, textvariable=self.person_id_var, style="Value.TLabel").grid(
                row=0, column=1, padx=(8, 18), sticky="w"
            )

            ttk.Button(toolbar, text="Save", style="Primary.TButton", command=self._save).grid(
                row=0, column=2, padx=(0, 8)
            )
            self.btn_update = ttk.Button(toolbar, text="Update", style="Primary.TButton", command=self._update)
            self.btn_update.grid(row=0, column=3, padx=(0, 8))
            self.btn_delete = ttk.Button(toolbar, text="Delete", style="Primary.TButton", command=self._delete)
            self.btn_delete.grid(row=0, column=4, padx=(0, 8))
            ttk.Button(toolbar, text="Clear", style="Primary.TButton", command=self._clear_form).grid(
                row=0, column=5, padx=(0, 8)
            )
            ttk.Button(toolbar, text="Refresh", style="Primary.TButton", command=self._refresh_tree).grid(
                row=0, column=6, padx=(0, 8)
            )

            self.btn_export_excel = ttk.Button(
                toolbar, text="Export Excel", style="Primary.TButton", command=self._export_excel
            )
            self.btn_export_excel.grid(row=0, column=7, padx=(0, 8))

            self.btn_print_contract = ttk.Button(
                toolbar, text="Print Contract", style="Primary.TButton", command=self._print_contract
            )
            self.btn_print_contract.grid(row=0, column=8, padx=(0, 8))

            ttk.Button(toolbar, text="Close", style="Primary.TButton", command=self.win.destroy).grid(
                row=0, column=9
            )

            self._set_selection_state(False)

            form_container = ttk.Frame(top_panel, style="Panel.TFrame")
            form_container.pack(fill="both", expand=True, padx=14, pady=(6, 14))

            fields = ttk.Frame(form_container, style="Panel.TFrame")
            fields.pack(side="left", fill="both", expand=True)

            photo_frame = ttk.Frame(form_container, style="Photo.TFrame", padding=10)
            photo_frame.pack(side="right", fill="y", padx=(20, 0))

            ttk.Label(
                photo_frame, text="Employee Photo", background="#2a2a2a",
                foreground="white", font=font_sm_b
            ).pack(pady=(0, 10))

            # تغییر کلیدی در مقداردهی اولیه لیبل عکس
            self.photo_label = tk.Label(
                photo_frame, text="No Photo", bg="#1a1a1a",
                fg="#888888", width=18, height=9, font=("Segoe UI", 10)
            )
            self.photo_label.pack(pady=(0, 10))

            btn_photo_frame = ttk.Frame(photo_frame, style="Photo.TFrame")
            btn_photo_frame.pack()
            ttk.Button(btn_photo_frame, text="Select", style="Small.TButton", command=self._browse_photo).pack(
                side="left", padx=2
            )
            ttk.Button(btn_photo_frame, text="Remove", style="Small.TButton", command=self._clear_photo).pack(
                side="left", padx=2
            )

            cols_count = 3
            for c in range(cols_count):
                fields.columnconfigure(c, weight=1)

            display_fields = [f for f in self.form_fields if f[0] != "PhotoPath"]

            for idx, (key, title) in enumerate(display_fields):
                r = idx // cols_count
                c = idx % cols_count
                cell = ttk.Frame(fields, style="Panel.TFrame")
                cell.grid(row=r, column=c, sticky="ew", padx=10, pady=6)
                ttk.Label(cell, text=title, style="Form.TLabel").grid(row=0, column=0, sticky="w")

                if key in self.date_fields:
                    de = DateEntry(cell, textvariable=self.vars[key], date_pattern="yyyy-mm-dd", width=22)
                    de.grid(row=1, column=0, sticky="w", pady=(4, 0))
                    self.date_widgets[key] = de
                elif key == "MaritalStatus":
                    rb = ttk.Frame(cell, style="Panel.TFrame")
                    rb.grid(row=1, column=0, sticky="w", pady=(6, 0))
                    ttk.Radiobutton(
                        rb, text="Single", value="Single",
                        variable=self.vars["MaritalStatus"], style="Dark.TRadiobutton"
                    ).grid(row=0, column=0, padx=(0, 16))
                    ttk.Radiobutton(
                        rb, text="Married", value="Married",
                        variable=self.vars["MaritalStatus"], style="Dark.TRadiobutton"
                    ).grid(row=0, column=1)
                elif key == "Gender":
                    rb = ttk.Frame(cell, style="Panel.TFrame")
                    rb.grid(row=1, column=0, sticky="w", pady=(6, 0))
                    ttk.Radiobutton(
                        rb, text="Male", value="Male",
                        variable=self.vars["Gender"], style="Dark.TRadiobutton"
                    ).grid(row=0, column=0, padx=(0, 16))
                    ttk.Radiobutton(
                        rb, text="Female", value="Female",
                        variable=self.vars["Gender"], style="Dark.TRadiobutton"
                    ).grid(row=0, column=1)
                elif key == "Education":
                    self.cmb_education = ttk.Combobox(
                        cell, textvariable=self.vars["Education"],
                        state="readonly", values=list(self.education_name_to_id.keys()), width=28
                    )
                    self.cmb_education.grid(row=1, column=0, sticky="w", pady=(4, 0))
                elif key == "Job":
                    self.cmb_job = ttk.Combobox(
                        cell, textvariable=self.vars["Job"],
                        state="readonly", values=list(self.job_name_to_id.keys()), width=28
                    )
                    self.cmb_job.grid(row=1, column=0, sticky="w", pady=(4, 0))
                elif key == "Department":
                    self.cmb_department = ttk.Combobox(
                        cell, textvariable=self.vars["Department"],
                        state="readonly", values=list(self.department_name_to_id.keys()), width=28
                    )
                    self.cmb_department.grid(row=1, column=0, sticky="w", pady=(4, 0))
                elif key == "Manager":
                    values = [""] + list(self.manager_name_to_id.keys())
                    self.cmb_manager = ttk.Combobox(
                        cell, textvariable=self.vars["Manager"],
                        state="readonly", values=values, width=28
                    )
                    self.cmb_manager.grid(row=1, column=0, sticky="w", pady=(4, 0))
                else:
                    ttk.Entry(cell, textvariable=self.vars[key], style="Form.TEntry", width=30).grid(
                        row=1, column=0, sticky="w", pady=(4, 0)
                    )

            search = ttk.Frame(bottom_panel, style="Panel.TFrame")
            search.pack(fill="x", padx=14, pady=(12, 8))
            search.columnconfigure(1, weight=1)

            ttk.Label(search, text="Search:", style="Form.TLabel").grid(row=0, column=0, sticky="w")
            ent_search = ttk.Entry(search, textvariable=self.search_var, style="Form.TEntry")
            ent_search.grid(row=0, column=1, sticky="ew", padx=(8, 10))
            ttk.Button(search, text="Search", style="Primary.TButton", command=self._search).grid(
                row=0, column=2, padx=(0, 8)
            )
            ttk.Button(search, text="Clear", style="Primary.TButton", command=self._clear_search).grid(
                row=0, column=3, padx=(0, 8)
            )
            ent_search.bind("<Return>", lambda e: self._search())

            tree_frame = ttk.Frame(bottom_panel, style="Panel.TFrame")
            tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
            tree_frame.rowconfigure(0, weight=1)
            tree_frame.columnconfigure(0, weight=1)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

            self.tree = ttk.Treeview(
                tree_frame, columns=self.tree_columns,
                show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set
            )
            vsb.config(command=self.tree.yview)
            hsb.config(command=self.tree.xview)
            self.tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")

            for col in self.tree_columns:
                self.tree.heading(col, text=col)
                if col == "Row":
                    self.tree.column(col, width=60, anchor="center", stretch=False)
                elif col in ("Birthdate", "Startdate", "Hiredate"):
                    self.tree.column(col, width=110, anchor="center")
                elif col in ("NationalCode", "Mobile", "InsuranceNumber", "AccountNumber"):
                    self.tree.column(col, width=150, anchor="center")
                elif col in ("MaritalStatus", "Gender"):
                    self.tree.column(col, width=110, anchor="center")
                elif col in ("Education", "Department", "Manager", "JobTitle"):
                    self.tree.column(col, width=180, anchor="w")
                else:
                    self.tree.column(col, width=200, anchor="w")

            self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

            self.context_menu = tk.Menu(self.win, tearoff=0, bg="#1a1a1a", fg="white", font=font_sm)
            self.context_menu.add_command(label="Update Employee", command=self._update)
            self.context_menu.add_command(label="Delete Employee", command=self._delete)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Print Contract", command=self._print_contract)
            self.tree.bind("<Button-3>", self._show_context_menu)

            self._refresh_tree()
            if self._created_root:
                self.win.mainloop()

        except Exception as e:
            messagebox.showerror("Employee Form Error", str(e), parent=self._msg_parent())

    # ---------------- CRUD ----------------
    def _get_form_data(self):
        return {k: (self.vars[k].get() or "").strip() for k, _ in self.form_fields}

    def _save(self):
        data = self._get_form_data()
        if not self._validate_form(data):
            return

        edu_id = int(self.education_name_to_id[data["Education"]])
        job_id = int(self.job_name_to_id[data["Job"]])
        dept_id = int(self.department_name_to_id[data["Department"]])

        manager_id = None
        if data["Manager"].strip():
            manager_id = int(self.manager_name_to_id.get(data["Manager"]))

        total_children = self._parse_int(data["TotalChildren"], allow_none=False)

        photo_param = None
        if self.current_photo_bytes:
            photo_param = pyodbc.Binary(self.current_photo_bytes)

        params = (
            data["FirstName"], data["LastName"], self._parse_date(data["Birthdate"]),
            data["MaritalStatus"], data["NationalCode"], data["Mobile"],
            data["Address"] if data["Address"] else None, data["Gender"],
            data["EmailAddress"] if data["EmailAddress"] else None,
            edu_id, manager_id, int(total_children),
            self._parse_date(data["Startdate"]), data["InsuranceNumber"], data["AccountNumber"],
            self._parse_date(data["Hiredate"]), dept_id, job_id,
            photo_param,
        )

        qmarks = ",".join(["?"] * len(params))
        rows, _ = self._db_query(f"EXEC dbo.InsertEmployee {qmarks}", params)
        if rows is None or not rows:
            return

        new_id = rows[0][0]
        self.person_id_var.set(str(new_id))
        self._set_selection_state(True)
        messagebox.showinfo("Saved", f"Saved successfully. PersonID={new_id}", parent=self._msg_parent())
        self._refresh_tree()

    def _update(self):
        pid = (self.person_id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Update", "Select a row first.", parent=self._msg_parent())
            return
        try:
            person_id = int(pid)
        except Exception:
            return

        data = self._get_form_data()
        if not self._validate_form(data):
            return

        edu_id = int(self.education_name_to_id[data["Education"]])
        job_id = int(self.job_name_to_id[data["Job"]])
        dept_id = int(self.department_name_to_id[data["Department"]])

        manager_id = None
        if data["Manager"].strip():
            manager_id = int(self.manager_name_to_id.get(data["Manager"]))

        total_children = self._parse_int(data["TotalChildren"], allow_none=False)

        photo_param = None
        if self.current_photo_bytes:
            photo_param = pyodbc.Binary(self.current_photo_bytes)

        params = (
            person_id,
            data["FirstName"], data["LastName"], self._parse_date(data["Birthdate"]),
            data["MaritalStatus"], data["NationalCode"], data["Mobile"],
            data["Address"] if data["Address"] else None, data["Gender"],
            data["EmailAddress"] if data["EmailAddress"] else None,
            edu_id, manager_id, int(total_children),
            self._parse_date(data["Startdate"]), data["InsuranceNumber"], data["AccountNumber"],
            self._parse_date(data["Hiredate"]), dept_id, job_id,
            photo_param,
        )

        qmarks = ",".join(["?"] * len(params))
        if self._db_exec(f"EXEC dbo.UpdateEmployee {qmarks}", params):
            messagebox.showinfo("Updated", "Updated successfully.", parent=self._msg_parent())
            self._refresh_tree()

    def _delete(self):
        pid = (self.person_id_var.get() or "").strip()
        if not pid:
            messagebox.showwarning("Delete", "Select a row first.", parent=self._msg_parent())
            return
        try:
            person_id = int(pid)
        except Exception:
            return

        if not messagebox.askyesno("Confirm", f"Delete PersonID={person_id}?", parent=self._msg_parent()):
            return
        if self._db_exec("EXEC dbo.DeleteEmployee ?", (person_id,)):
            messagebox.showinfo("Deleted", "Deleted successfully.", parent=self._msg_parent())
            self._clear_form()
            self._refresh_tree()

    def _clear_form(self):
        for k in self.vars:
            self.vars[k].set("")
        self.vars["MaritalStatus"].set("Single")
        self.vars["Gender"].set("Male")
        if self.cmb_education:
            self.cmb_education.set("")
        if self.cmb_job:
            self.cmb_job.set("")
        if self.cmb_department:
            self.cmb_department.set("")
        if self.cmb_manager:
            self.cmb_manager.set("")
        self.person_id_var.set("")
        self._clear_photo()
        self._set_selection_state(False)

    # ---------------- Tree/Search ----------------
    def _refresh_tree(self):
        data = self._fetch_all_employees()
        self._cache_by_personid = {}
        self.tree.delete(*self.tree.get_children())

        for idx, d in enumerate(data, start=1):
            pid = d.get("PersonID")
            if pid is None:
                continue
            try:
                pid_int = int(pid)
                self._cache_by_personid[pid_int] = d
                iid = str(pid_int)
            except Exception:
                continue

            values = []
            for col in self.tree_columns:
                if col == "Row":
                    values.append(str(idx))
                else:
                    v = d.get(col, "")
                    if isinstance(v, (datetime, date)):
                        v = v.isoformat()
                    values.append("" if v is None else str(v))
            self.tree.insert("", "end", iid=iid, values=values)

        if not (self.person_id_var.get() or "").strip():
            self._set_selection_state(False)

    def _search(self):
        q = (self.search_var.get() or "").strip()
        if not q:
            self._refresh_tree()
            return
        data = self._search_employees_db(q)
        self._cache_by_personid = {}
        self.tree.delete(*self.tree.get_children())

        for idx, d in enumerate(data, start=1):
            pid = d.get("PersonID")
            if pid is None:
                continue
            try:
                pid_int = int(pid)
                self._cache_by_personid[pid_int] = d
                iid = str(pid_int)
            except Exception:
                continue

            values = []
            for col in self.tree_columns:
                if col == "Row":
                    values.append(str(idx))
                else:
                    v = d.get(col, "")
                    if isinstance(v, (datetime, date)):
                        v = v.isoformat()
                    values.append("" if v is None else str(v))
            self.tree.insert("", "end", iid=iid, values=values)

    def _clear_search(self):
        self.search_var.set("")
        self._refresh_tree()

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            self.person_id_var.set("")
            self._set_selection_state(False)
            return

        try:
            person_id = int(sel[0])
        except Exception:
            self.person_id_var.set("")
            self._set_selection_state(False)
            return

        d = self._cache_by_personid.get(person_id)
        if not d:
            return

        self.person_id_var.set(str(person_id))
        self._set_selection_state(True)

        self.vars["FirstName"].set("" if d.get("FirstName") is None else str(d.get("FirstName")))
        self.vars["LastName"].set("" if d.get("LastName") is None else str(d.get("LastName")))

        for df in self.date_fields:
            s = "" if d.get(df) is None else str(d.get(df))
            self.vars[df].set(s)
            if df in self.date_widgets:
                try:
                    dt = datetime.strptime(s, "%Y-%m-%d").date()
                    self.date_widgets[df].set_date(dt)
                except Exception:
                    pass

        ms = "Single" if d.get("MaritalStatus") is None else str(d.get("MaritalStatus")).strip().lower()
        self.vars["MaritalStatus"].set("Married" if ms == "married" else "Single")
        g = "Male" if d.get("Gender") is None else str(d.get("Gender")).strip().lower()
        self.vars["Gender"].set("Female" if g == "female" else "Male")

        self.vars["NationalCode"].set("" if d.get("NationalCode") is None else str(d.get("NationalCode")))
        self.vars["Mobile"].set("" if d.get("Mobile") is None else str(d.get("Mobile")))
        self.vars["Address"].set("" if d.get("Address") is None else str(d.get("Address")))
        self.vars["EmailAddress"].set("" if d.get("EmailAddress") is None else str(d.get("EmailAddress")))
        self.vars["TotalChildren"].set("" if d.get("TotalChildren") is None else str(d.get("TotalChildren")))
        self.vars["InsuranceNumber"].set("" if d.get("InsuranceNumber") is None else str(d.get("InsuranceNumber")))
        self.vars["AccountNumber"].set("" if d.get("AccountNumber") is None else str(d.get("AccountNumber")))

        self.vars["Education"].set("" if d.get("Education") is None else str(d.get("Education")))
        if self.cmb_education:
            self.cmb_education.set(self.vars["Education"].get())

        self.vars["Job"].set("" if d.get("JobTitle") is None else str(d.get("JobTitle")))
        if self.cmb_job:
            self.cmb_job.set(self.vars["Job"].get())

        self.vars["Department"].set("" if d.get("Department") is None else str(d.get("Department")))
        if self.cmb_department:
            self.cmb_department.set(self.vars["Department"].get())

        self.vars["Manager"].set("" if d.get("Manager") is None else str(d.get("Manager")))
        if self.cmb_manager:
            self.cmb_manager.set(self.vars["Manager"].get())

        # load photo from cache
        self.vars["PhotoPath"].set("")
        db_photo = d.get("Photo")
        self.current_photo_bytes = self._normalize_photo_from_db(db_photo)
        self._update_photo_preview_from_bytes(self.current_photo_bytes)