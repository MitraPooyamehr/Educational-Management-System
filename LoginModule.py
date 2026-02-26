from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msg
import pyodbc
from PIL import Image, ImageTk

from UserInterfaceLayer.MainModule import MainForm
from Model.UserModel import User_Model_class

# ---------------- Settings ----------------
APP_WIDTH, APP_HEIGHT = 900, 550

PRIMARY_PURPLE = "#520034"
CARD_BG        = "#3b0153"
CARD_BG_FAKE   = "#030005"

show_photo = None
hide_photo = None

# ---------------- Main window ----------------
login_form = Tk()
login_form.title('Login Form')
login_form.geometry(f'{APP_WIDTH}x{APP_HEIGHT}')
login_form.resizable(0, 0)

try:
    login_form.iconbitmap('images/login.ico')
except Exception:
    pass

# center window
login_form.update_idletasks()
screen_w = login_form.winfo_screenwidth()
screen_h = login_form.winfo_screenheight()
x = int(screen_w / 2 - APP_WIDTH / 2)
y = int(screen_h / 2 - APP_HEIGHT / 2)
login_form.geometry(f'+{x}+{y}')

# ---------------- Background image ----------------
bg_image = Image.open("Images/2.png")
bg_image = bg_image.resize((APP_WIDTH, APP_HEIGHT), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = Label(login_form, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ---------------- ttk style ----------------
style = ttk.Style(login_form)
try:
    style.theme_use("clam")
except TclError:
    pass

style.configure(
    "Title.TLabel",
    foreground="white",
    background=CARD_BG_FAKE,
    font=("Segoe UI", 22, "bold")
)
style.configure(
    "Subtitle.TLabel",
    foreground="#dcdde1",
    background=CARD_BG_FAKE,
    font=("Segoe UI", 10)
)
style.configure(
    "FieldLabel.TLabel",
    foreground="#520034",
    background=CARD_BG_FAKE,
    font=("Segoe UI", 11, "bold")
)
style.configure(
    "Custom.TEntry",
    foreground="white",
    fieldbackground="#220229",
    background="#520034",
    padding=6,
    borderwidth=0
)
style.configure(
    "Login.TButton",
    background=PRIMARY_PURPLE,
    foreground="white",
    padding=(20, 8),
    font=("Segoe UI", 11, "bold"),
    borderwidth=0
)
style.map(
    "Login.TButton",
    background=[("active", "#7B6CFF")],
    foreground=[("active", "black")]
)
style.configure(
    "Link.TLabel",
    foreground="#dcdde1",
    background=CARD_BG_FAKE,
    font=("Segoe UI", 9, "underline")
)

# ---------------- Left panel ----------------
left_card = Frame(login_form, bg=CARD_BG_FAKE, bd=0)
left_card.place(relx=0.05, rely=0.12, relwidth=0.4, relheight=0.76)

inner = Frame(left_card, bg=CARD_BG_FAKE)
inner.pack(expand=True, fill="both", padx=30, pady=25)

# ---------------- Avatar ----------------
avatar_img = Image.open("Images/6.png")
avatar_img = avatar_img.resize((85, 80), Image.LANCZOS)
avatar_photo = ImageTk.PhotoImage(avatar_img)

avatar_label = Label(inner, image=avatar_photo, bg=CARD_BG_FAKE)
avatar_label.image = avatar_photo
avatar_label.pack(pady=(0, 20))

# ---------------- Username field ----------------
frame_user = Frame(inner, bg=CARD_BG_FAKE)
frame_user.pack(fill="x", pady=(5, 10))

lbl_username = Label(frame_user, text='UserName: ', bg=CARD_BG_FAKE, fg="#520034",
                     font=("Segoe UI", 11, "bold"))
lbl_username.pack(anchor="w", pady=(0, 2))

txt_username = StringVar(master=login_form, value="")
ent_username = ttk.Entry(frame_user, width=40, textvariable=txt_username, style="Custom.TEntry")
ent_username.pack(fill="x", pady=(3, 0), padx=(0, 35))

# ---------------- Password field + show/hide ----------------
frame_pass = Frame(inner, bg=CARD_BG_FAKE)
frame_pass.pack(fill="x", pady=(10, 15))

lbl_password = Label(frame_pass, text='Password: ', bg=CARD_BG_FAKE, fg="#520034",
                     font=("Segoe UI", 11, "bold"))
lbl_password.pack(anchor="w", pady=(0, 2))

txt_password = StringVar(master=login_form, value="")
ent_password = ttk.Entry(frame_pass, width=40, textvariable=txt_password, show='*', style="Custom.TEntry")
ent_password.pack(fill="x", pady=(3, 0), padx=(0, 35))

# --- load show/hide images
try:
    img_show = Image.open("Images/7.png").resize((20, 25), Image.LANCZOS)
    show_photo = ImageTk.PhotoImage(img_show)

    img_hide = Image.open("Images/8.png").resize((20, 25), Image.LANCZOS)
    hide_photo = ImageTk.PhotoImage(img_hide)
except Exception:
    show_photo = None
    hide_photo = None


def show_hide_command():
    if ent_password.cget('show') == '*':
        ent_password.config(show='')
        if hide_photo is not None:
            btn_show_hide.config(image=hide_photo, text='')
        else:
            btn_show_hide.config(text='Hide')
    else:
        ent_password.config(show='*')
        if show_photo is not None:
            btn_show_hide.config(image=show_photo, text='')
        else:
            btn_show_hide.config(text='Show')


btn_show_hide = Button(
    frame_pass,
    image=show_photo if show_photo is not None else None,
    text='' if show_photo is not None else '🙉',
    font='18',
    relief='groove',
    bg=CARD_BG_FAKE,
    fg="white",
    activebackground=CARD_BG_FAKE,
    activeforeground="white",
    bd=0,
    cursor='hand2',
    command=show_hide_command
)
btn_show_hide.place(relx=1.0, rely=0.5, x=-5, anchor='e')


# ---------------- Login command (FIXED) ----------------
def login_command():
    username = (txt_username.get() or "").strip()
    password = (txt_password.get() or "").strip()

    if not username or not password:
        msg.showwarning("Validation", "Please enter username and password.")
        return

    connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=your_server_here;Database=SematecLearningManagementSystem;UID=sa;PWD=your_password_here"

    command_text = "exec dbo.GetUseNamePassword ?,?"

    try:
        with pyodbc.connect(connection_string) as connection:
            cursor = connection.cursor()
            cursor.execute(command_text, (username, password))
            rows = cursor.fetchall()
    except Exception as e:
        msg.showerror('error!', f'Database error:\n{e}')
        return

    if len(rows) <= 0:
        msg.showerror('error!', 'UserName or Password is incorrect!')
        return

    # ساخت user object
    user_object = User_Model_class(
        username, password,
        rows[0][3], rows[0][4],
        rows[0][5], rows[0][6]
    )

    # -------------------------------------------
    login_form.withdraw()

    # -------------------------------------------
    main_form_object = MainForm(user_object, master=login_form)
    main_form_object.main_form_load()


# ---------------- Login button ----------------
btn_login = Button(
    inner,
    text='Login',
    width=36,
    command=login_command,
    bg=PRIMARY_PURPLE,
    fg="white",
    activebackground="#7B6CFF",
    activeforeground="black",
    relief="groove"
)
btn_login.pack(pady=(20, 10), anchor='w')

# Enter = login
login_form.bind('<Return>', lambda e: login_command())

login_form.mainloop()