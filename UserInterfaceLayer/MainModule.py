import tkinter as tk
from tkinter import Canvas, messagebox
from PIL import Image, ImageTk
from Model.UserModel import User_Model_class


class MainForm:
    def __init__(self, user_param: User_Model_class, master: tk.Tk):
        self.user = user_param
        self.master = master
        self.win = None
        self._images = []
        self._children = []

    # ---------- helpers ----------
    def _round_rect(self, c: Canvas, x1, y1, x2, y2, r=22, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return c.create_polygon(points, smooth=True, **kwargs)

    def _lighten(self, hex_color: str, amount: float = 0.08) -> str:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = int(r + (255 - r) * amount)
        g = int(g + (255 - g) * amount)
        b = int(b + (255 - b) * amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _make_card_button_style2(
        self,
        c: Canvas,
        x, y,
        card_w, card_h,
        text,
        icon_path,
        card_color,
        command,
        text_position="top"
    ):
        tag = f"btn_{text}".replace(" ", "_").replace("\n", "_")

        card_id = self._round_rect(
            c, x, y, x + card_w, y + card_h,
            r=26,
            fill=card_color,
            outline=""
        )
        c.addtag_withtag(tag, card_id)

        label_font = ("Segoe UI", 10, "bold")
        line_w = 2
        line_len = int(card_w * 0.62)

        if text_position == "top":
            label_y = y + 18
            underline_y = y + 34
            icon_cy = y + (card_h * 0.60)
        else:
            label_y = y + card_h - 18
            underline_y = y + card_h - 34
            icon_cy = y + (card_h * 0.42)

        text_id = c.create_text(
            x + card_w / 2,
            label_y,
            text=text,
            fill="white",
            font=label_font,
            justify="center"
        )
        c.addtag_withtag(tag, text_id)

        line_x1 = x + (card_w - line_len) / 2
        line_x2 = line_x1 + line_len
        line_id = c.create_line(
            line_x1, underline_y, line_x2, underline_y,
            fill="white",
            width=line_w
        )
        c.addtag_withtag(tag, line_id)

        try:
            icon_img = Image.open(icon_path).convert("RGBA")
            icon_img = icon_img.resize((62, 62), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
            self._images.append(icon_photo)

            icon_id = c.create_image(
                x + card_w / 2,
                icon_cy,
                image=icon_photo
            )
            c.addtag_withtag(tag, icon_id)
        except Exception:
            pass

        def on_click(_e):
            command()

        def on_enter(_e):
            c.itemconfig(card_id, fill=self._lighten(card_color, 0.10))
            c.config(cursor="hand2")

        def on_leave(_e):
            c.itemconfig(card_id, fill=card_color)
            c.config(cursor="")

        c.tag_bind(tag, "<Button-1>", on_click)
        c.tag_bind(tag, "<Enter>", on_enter)
        c.tag_bind(tag, "<Leave>", on_leave)

    # ---------- safe child opener ----------
    def _open_child_form(self, form_class, open_method_name: str):
        child = None
        try:
            child = form_class(self.user, master=self.win)
            self._children.append(child)

            open_method = getattr(child, open_method_name)
            open_method()

            if getattr(child, "win", None) is None or not child.win.winfo_exists():
                raise RuntimeError("Child window was not created.")

            self.win.withdraw()

            child.win.deiconify()
            child.win.lift()
            child.win.focus_force()
            try:
                child.win.attributes("-topmost", True)
                child.win.after(150, lambda: child.win.attributes("-topmost", False))
            except Exception:
                pass

            self.win.wait_window(child.win)

        except Exception as e:
            try:
                if self.win is not None and self.win.winfo_exists():
                    self.win.deiconify()
                    self.win.lift()
                    self.win.focus_force()
            except Exception:
                pass
            messagebox.showerror("Form Error", str(e), parent=self.win)

        finally:
            if self.win is not None and self.win.winfo_exists():
                self.win.deiconify()
                self.win.lift()
                self.win.focus_force()

    # ---------- main ----------
    def main_form_load(self):
        self.win = tk.Toplevel(self.master)
        self.win.title("Main Form")

        W, H = 950, 550
        self.win.resizable(False, False)

        self.win.update_idletasks()
        x = self.win.winfo_screenwidth() // 2 - W // 2
        y = self.win.winfo_screenheight() // 2 - H // 2
        self.win.geometry(f"{W}x{H}+{x}+{y}")

        self.win.protocol("WM_DELETE_WINDOW", self.master.destroy)

        canvas = Canvas(self.win, width=W, height=H, bd=0, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        try:
            bg_image = Image.open("Images/9.jpg")
            bg_image = bg_image.resize((W, H), Image.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg_image)
            self._images.append(bg_photo)
            canvas.create_image(0, 0, image=bg_photo, anchor="nw")
        except Exception:
            pass

        fn = (getattr(self.user, "firstname", "") or "").strip()
        ln = (getattr(self.user, "lastname", "") or "").strip()
        welcome = f"WELCOME {fn} {ln}".strip()

        canvas.create_text(
            65, 70,
            text=welcome,
            anchor="w",
            fill="white",
            font=("Segoe UI Black", 22)
        )

        # ---------------- commands ----------------
        def student_crud_load():
            from UserInterfaceLayer.StudentModule import StudentForm
            self._open_child_form(StudentForm, "student_form_load")

        def employee_crud_load():
            from UserInterfaceLayer.EmployeeModule import EmployeeForm
            self._open_child_form(EmployeeForm, "employee_form_load")

        def teacher_crud_load():
            from UserInterfaceLayer.TeacherModule import TeacherForm
            self._open_child_form(TeacherForm, "teacher_form_load")

        def course_crud_load():
            from UserInterfaceLayer.CourseModule import CourseForm
            self._open_child_form(CourseForm, "course_form_load")

        def course_category_crud_load():
            from UserInterfaceLayer.CourseCategoryModule import CourseCategoryForm
            self._open_child_form(CourseCategoryForm, "course_category_form_load")

        def department_crud_load():
            from UserInterfaceLayer.DepartmentModule import DepartmentForm
            self._open_child_form(DepartmentForm, "department_form_load")

        def education_crud_load():
            try:
                from UserInterfaceLayer.EducationModule import EducationForm
                self._open_child_form(EducationForm, "education_form_load")
            except Exception as e:
                messagebox.showerror("Education Error", str(e), parent=self.win)

        def job_crud_load():
            try:
                from UserInterfaceLayer.JobModule import JobForm
                self._open_child_form(JobForm, "job_form_load")
            except Exception as e:
                messagebox.showerror("Job Error", str(e), parent=self.win)

        def certificate_crud_load():
            from UserInterfaceLayer.CertificationModule import CertificationForm
            self._open_child_form(CertificationForm, "certification_form_load")

        def score_crud_load():
            from UserInterfaceLayer.ScoreModule import ScoreForm
            self._open_child_form(ScoreForm, "score_form_load")

        # ---------------- Admin Checker ----------------
        def require_admin(func):
            def wrapper():
                is_admin = getattr(self.user, "isAdmin", False)
                if is_admin in [True, 1, "1", "True"]:
                    func()
                else:
                    messagebox.showwarning(
                        "Access Denied",
                        "You do not have Administrator privileges to access this section.",
                        parent=self.win
                    )
            return wrapper

        # ---------------- Items List (اصلاح شده) ----------------
        items = [
            ("Student CRUD", "Images/20.png", student_crud_load, "#330000", "top"),
            ("Teacher CRUD", "Images/21.png", require_admin(teacher_crud_load), "#3c0623", "top"),
            ("Employee CRUD", "Images/22.png", require_admin(employee_crud_load), "#2f0a31", "top"),
            ("Course CRUD", "Images/23.png", course_crud_load, "#2a023a", "top"),
            ("Course Category\nCRUD", "Images/24.png", course_category_crud_load, "#3d0357", "top"),

            ("Department CRUD", "Images/25.png", require_admin(department_crud_load), "#1f0343", "bottom"),
            ("Education CRUD", "Images/26.png", education_crud_load, "#150e6c", "bottom"),
            ("Job CRUD", "Images/27.png", require_admin(job_crud_load), "#34045a", "bottom"),
            ("Certificate CRUD", "Images/28.png", certificate_crud_load, "#610660", "bottom"),
            ("Score CRUD", "Images/29.png", score_crud_load, "#831553", "bottom"),
        ]

        card_w, card_h = 135, 120
        gap_x, gap_y = 38, 46

        total_w = (5 * card_w) + (4 * gap_x)
        start_x = (W - total_w) / 2
        start_y = 145

        for i, (text, icon, cmd, color, pos) in enumerate(items):
            rr = i // 5
            cc = i % 5
            x0 = start_x + cc * (card_w + gap_x)
            y0 = start_y + rr * (card_h + gap_y)

            self._make_card_button_style2(
                canvas,
                x0, y0,
                card_w, card_h,
                text=text,
                icon_path=icon,
                card_color=color,
                command=cmd,
                text_position=pos
            )
