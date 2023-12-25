import sqlite3
import customtkinter
import pygal
from datetime import datetime, timedelta, date
from PIL import Image
import webbrowser
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet as FER
import pyperclip
import traceback
from CTkMessagebox import CTkMessagebox
import pystray
import pickle

customtkinter.set_default_color_theme(".\\_internal\\src\\green.json")

app = customtkinter.CTk()
app.geometry('%dx%d+%d+%d' % (1600, 900, (app.winfo_screenwidth()/2) - (1600/2), (app.winfo_screenheight()/2) - (900/2)))
app.title("enigma:guard")
app.resizable("False", "False")
app.iconbitmap(".\\_internal\\assets\\enigma-guard.ico")

x = datetime.now()

total_encryptions = 0
total_decryptions = 0
total_encryptions_decryptions = 0

conn = sqlite3.connect("enigma_guard_data.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS enigma_guard_data 
          (
          title text,
          encryption_type text,
          cipher_text bool,
          iv bool,
          nonce bool,
          key bool,
          encryption_key integer,
          date text
          )""")
conn.commit()
conn.close()

def on_tab_pressed(event):
    return 'break'

def pygal_analytics_graph():
    def read_data(file_name):
        try:
            data = {}
            with open(file_name, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(':')
                    date = datetime.strptime(parts[0], '%Y-%m-%d')
                    value = int(parts[1])
                    data[date] = value
            return data
        except FileNotFoundError:
            return {}

    encryption_info = read_data('.\\_internal\\src\\encryption_info.txt')
    decryption_info = read_data('.\\_internal\\src\\decryption_info.txt')

    today = datetime.now().date()
    date_labels = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(4, -1, -1)]

    encryption_data = []
    for date_label in date_labels:
        date = datetime.strptime(date_label, '%Y-%m-%d')
        if date in encryption_info:
            encryption_data.append(encryption_info[date])
        else:
            encryption_data.append(0)

    decryption_data = []
    for date_label in date_labels:
        date = datetime.strptime(date_label, '%Y-%m-%d')
        if date in decryption_info:
            decryption_data.append(decryption_info[date])
        else:
            decryption_data.append(0)

    custom_style = pygal.style.Style(
        background='#000000',
        plot_background='#000000',
        colors=( '#838199', '#1FFFA9'),
        font_family='Armin Grotesk SemiBold',
        value_colors='#FFFFFF',
        foreground='#FFFFFF',
        foreground_subtle='#FFFFFF',
        foreground_strong='#FFFFFF',
        foreground_font_size=20,
        opacity='.7',
        value_font_size = 20.0,
        tooltip_font_size = 20.0,
        major_label_font_size = 20.0,
        label_font_size = 15.0,
    )

    line_chart = pygal.StackedLine(
        style=custom_style,
        show_legend=False,
        fill=True,
        interpolate='cubic',
        dots_size=5,
        max_scale=10
    )
    line_chart.x_labels = date_labels
    line_chart.add('Encryption', encryption_data)
    line_chart.add('Decryption', decryption_data)

    chart_filename = '.\\_internal\\assets\\encryption_decryption_chart.png'
    line_chart.render_to_png(chart_filename, width=1060,height=328)

    graph_image = customtkinter.CTkImage(light_image=Image.open(chart_filename),dark_image=Image.open(chart_filename),size = (1060,328))
    graph_label = customtkinter.CTkLabel(analytics_frame_win,image=graph_image,text="",width=1060,height=328)
    graph_label.place(x=447,y=446)


def analytics_win():
    if frame_main_win.winfo_ismapped():
        frame_main_win.pack_forget()
    elif encrypt_frame_win.winfo_ismapped():
        encrypt_frame_win.pack_forget()
    elif decrypt_frame_win.winfo_ismapped():
        decrypt_frame_win.pack_forget()
    elif keys_frame_win.winfo_ismapped():
        keys_frame_win.pack_forget()
    elif settings_frame_win.winfo_ismapped():
        settings_frame_win.pack_forget()
    analytics_frame_win.pack()
    pygal_analytics_graph()

def encrypt_win():
    if analytics_frame_win.winfo_ismapped():
        analytics_frame_win.pack_forget()
    elif decrypt_frame_win.winfo_ismapped():
        decrypt_frame_win.pack_forget()
    elif keys_frame_win.winfo_ismapped():
        keys_frame_win.pack_forget()
    elif settings_frame_win.winfo_ismapped():
        settings_frame_win.pack_forget()

    encrypt_frame_win.pack()


    encrypt_title_textbox_frame = customtkinter.CTkFrame(master = encrypt_frame_win,width=300,height=70,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    encrypt_title_textbox_frame.place(x=410,y=122)
    encrypt_title_textbox = customtkinter.CTkTextbox(encrypt_title_textbox_frame,width=270,height=34,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent",activate_scrollbars=False)
    def encrypt_title_textbox_text_length():

        current_text = encrypt_title_textbox.get("0.0", "end")
        max_characters = 16

        if len(current_text) > max_characters:
            truncated_text = current_text[:max_characters]
            encrypt_title_textbox.delete("1.0", "end")
            encrypt_title_textbox.insert("1.0", truncated_text)

        encrypt_title_textbox.after(100, encrypt_title_textbox_text_length)

    encrypt_title_textbox_text_length()
    encrypt_title_textbox.insert("0.0", "Title")
    encrypt_title_textbox.place(x=10,y=10)

    def encryption_title_textbox_clear_text(event):
        if encrypt_title_textbox.get("0.0", "end").strip() == "Title":
            encrypt_title_textbox.delete("0.0", "end")

    def reset_default_text(event):
        if not encrypt_title_textbox.get("0.0", "end").strip():
            encrypt_title_textbox.insert("0.0", "Title")

    encrypt_title_textbox.bind("<FocusIn>", encryption_title_textbox_clear_text)
    encrypt_title_textbox.bind("<FocusOut>", reset_default_text)
    encrypt_title_textbox.get("0.0", "end")
    encrypt_title_textbox.bind("<Tab>", on_tab_pressed)

    encryption_type_optionmenu_img_frame = customtkinter.CTkLabel(encrypt_frame_win,height=70,width=300,image=encryption_type_optionmenu_img,bg_color="#000000")
    encryption_type_optionmenu_img_frame.place(x=830,y=122)

    encryption_type_optionmenu = customtkinter.CTkOptionMenu(encrypt_frame_win, values=["Select method","Fernet","CBC", "CTR", "CFB", "OFB"],fg_color="#000000",width=294,height=64,dropdown_fg_color="#000000",font=armin_grotesk_ultra_bold,dropdown_font=armin_grotesk_ultra_bold,hover=False,button_color="#1FFFA9",corner_radius=3,dynamic_resizing=False,dropdown_text_color="#FFFFFF")
    encryption_type_optionmenu.set("Select method")
    encryption_type_optionmenu.place(x=845,y=125)
    
    key_textbox_frame = customtkinter.CTkFrame(master = encrypt_frame_win,width=300,height=70,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    key_textbox_frame.place(x=1256,y=122)
    key_textbox = customtkinter.CTkTextbox(key_textbox_frame,width=270,height=34,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent",activate_scrollbars=False,wrap=None)
    key_textbox.insert("0.0", "Key")
    key_textbox.configure(state="disabled")
    key_textbox.place(x=10,y=10)

    user_encrypt_text_textbox_frame = customtkinter.CTkFrame(master = encrypt_frame_win,width=1148,height=250,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    user_encrypt_text_textbox_frame.place(x=410,y=230)
    user_encrypt_text_textbox = customtkinter.CTkTextbox(user_encrypt_text_textbox_frame,width=1118,height=220,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent")
    user_encrypt_text_textbox.insert("0.0", "Enter text to encrypt")
    user_encrypt_text_textbox.place(x=10,y=10)
    
    def user_encrypt_text_textbox_clear_text(event):
        if user_encrypt_text_textbox.get("0.0", "end").strip() == "Enter text to encrypt":
            user_encrypt_text_textbox.delete("0.0", "end")

    def reset_user_encrypt_text_textbox_clear_text(event):
        if not user_encrypt_text_textbox.get("0.0", "end").strip():
            user_encrypt_text_textbox.insert("0.0", "Enter text to encrypt")

    user_encrypt_text_textbox.bind("<FocusIn>", user_encrypt_text_textbox_clear_text)
    user_encrypt_text_textbox.bind("<FocusOut>", reset_user_encrypt_text_textbox_clear_text) 
    user_encrypt_text_textbox.bind("<Tab>", on_tab_pressed)

    user_encrypted_text_textbox_frame = customtkinter.CTkFrame(master = encrypt_frame_win,width=1148,height=250,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    user_encrypted_text_textbox_frame.place(x=410,y=515)
    user_encrypted_text_textbox = customtkinter.CTkTextbox(user_encrypted_text_textbox_frame,width=1118,height=220,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent")
    user_encrypted_text_textbox.insert("0.0", "Encrypted text")
    user_encrypted_text_textbox.place(x=10,y=10)
    user_encrypted_text_textbox.configure(state="disabled")

        
    def fernet_encryption():
        message = user_encrypt_text_textbox.get('0.0', 'end')

        decoded_key = FER.generate_key().decode('utf-8')

        fernet = FER(decoded_key)
        key_textbox.configure(state="normal")
        key_textbox.delete("0.0", "end")
        key_text_11 = decoded_key[0:10]
        key_textbox.insert("0.0", key_text_11+"...")
        def encrypt_key_copy():
            pyperclip.copy(decoded_key)
        encrypt_copy_button = customtkinter.CTkButton(key_textbox_frame,width=23,height=26,image=encrypt_copy_button_img,hover=False,fg_color="#000000",text="",command=encrypt_key_copy)
    
        encrypt_copy_button.place(x=255,y=18)
        key_textbox.configure(state="disabled")
        ct = fernet.encrypt(message.encode())
        user_encrypted_text_textbox.configure(state="normal")
        user_encrypted_text_textbox.delete("0.0", "end")
        user_encrypted_text_textbox.insert("0.0", ct)
        user_encrypted_text_textbox.configure(state="disabled")
        title = encrypt_title_textbox.get('0.0', 'end').strip()
        conn = sqlite3.connect('enigma_guard_data.db')
        c = conn.cursor()
        encryption_type = "Fernet"
        c.execute("""CREATE TABLE IF NOT EXISTS enigma_guard_data 
          (
          title text,
          encryption_type text,
          cipher_text bool,
          iv bool,
          nonce bool,
          key bool,
          encryption_key integer,
          date text
          )""")
    
        c.execute("INSERT INTO enigma_guard_data VALUES (:title, :encryption_type, :cipher_text, :iv, :nonce, :key, :encryption_key, :date)", {'title': title,'encryption_type': encryption_type,'cipher_text': ct, 'iv': "Not present", 'nonce': "Not present", 'key': decoded_key, 'encryption_key': 1, 'date': x.strftime("%d"+ "/" +"%m"+ "/" +"%Y")})
        conn.commit()
        increment_encryptions()
        increment_encryptions_decryptions()
        increment_overall_encryptions()
        conn.close()

    def cbc():
        message = user_encrypt_text_textbox.get('0.0', 'end').encode('utf-8')

        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message, AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        key_textbox.configure(state="normal")
        key_textbox.delete("0.0", "end")
        decoded_key = b64encode(key).decode('utf-8')
        key_text_11 = decoded_key[0:10]
        key_textbox.insert("0.0", key_text_11 + "...")

        def encrypt_key_copy():
            pyperclip.copy(decoded_key)
        encrypt_copy_button = customtkinter.CTkButton(key_textbox_frame,width=23,height=26,image=encrypt_copy_button_img,hover=False,fg_color="#000000",text="",command=encrypt_key_copy)
    
        encrypt_copy_button.place(x=255,y=18)
        key_textbox.configure(state="disabled")

        ct = b64encode(ct_bytes).decode('utf-8')
        user_encrypted_text_textbox.configure(state="normal")
        user_encrypted_text_textbox.delete("0.0", "end")
        user_encrypted_text_textbox.insert("0.0", ct)
        user_encrypted_text_textbox.configure(state="disabled")

        title = encrypt_title_textbox.get('0.0', 'end').strip()
        conn = sqlite3.connect('enigma_guard_data.db')
        c = conn.cursor()
        encryption_type = "CBC"
        c.execute("""CREATE TABLE IF NOT EXISTS enigma_guard_data 
          (
          title text,
          encryption_type text,
          cipher_text bool,
          iv bool,
          nonce bool,
          key bool,
          encryption_code integer,
          date text
          )""")
    
        c.execute("INSERT INTO enigma_guard_data VALUES (:title, :encryption_type, :cipher_text, :iv, :nonce, :key, :encryption_code, :date)", {'title': title,'encryption_type': encryption_type,'cipher_text': ct, 'iv': iv, 'nonce': "Not present", 'encryption_code': 2, 'key': decoded_key, 'date': x.strftime("%d"+ "/" +"%m"+ "/" +"%Y")})
        conn.commit()
        increment_encryptions()
        increment_encryptions_decryptions()
        increment_overall_encryptions()
        conn.close()

    def ctr():
        message = user_encrypt_text_textbox.get('0.0', 'end').encode('utf-8')

        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CTR)
        ct_bytes = cipher.encrypt(pad(message, AES.block_size))
        nonce = b64encode(cipher.nonce).decode('utf-8')
        key_textbox.configure(state="normal")
        key_textbox.delete("0.0", "end")
        decoded_key = b64encode(key).decode('utf-8')
        key_text_11 = decoded_key[0:10]
        key_textbox.insert("0.0", key_text_11 + "...")

        def encrypt_key_copy():
            pyperclip.copy(decoded_key)
        encrypt_copy_button = customtkinter.CTkButton(key_textbox_frame,width=23,height=26,image=encrypt_copy_button_img,hover=False,fg_color="#000000",text="",command=encrypt_key_copy)
    
        encrypt_copy_button.place(x=255,y=18)
        key_textbox.configure(state="disabled")

        ct = b64encode(ct_bytes).decode('utf-8')
        user_encrypted_text_textbox.configure(state="normal")
        user_encrypted_text_textbox.delete("0.0", "end")
        user_encrypted_text_textbox.insert("0.0", ct)
        user_encrypted_text_textbox.configure(state="disabled")

        title = encrypt_title_textbox.get('0.0', 'end').strip()
        conn = sqlite3.connect('enigma_guard_data.db')
        c = conn.cursor()
        encryption_type = "CTR"
        c.execute("""CREATE TABLE IF NOT EXISTS enigma_guard_data 
          (
          title text,
          encryption_type text,
          cipher_text bool,
          iv bool,
          nonce bool,
          key bool,
          encryption_code integer,
          date text
          )""")
    
        c.execute("INSERT INTO enigma_guard_data VALUES (:title, :encryption_type, :cipher_text, :iv, :nonce, :key, :encryption_code, :date)", {'title': title,'encryption_type': encryption_type,'cipher_text': ct, 'iv': "Not present", 'nonce': nonce, 'key': decoded_key, 'encryption_code': 3, 'date': x.strftime("%d"+ "/" +"%m"+ "/" +"%Y")})
        conn.commit()
        increment_encryptions()
        increment_encryptions_decryptions()
        increment_overall_encryptions()
        conn.close()

    def cfb():
        message = user_encrypt_text_textbox.get('0.0', 'end').encode('utf-8')

        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CFB)
        ct_bytes = cipher.encrypt(pad(message, AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        key_textbox.configure(state="normal")
        key_textbox.delete("0.0", "end")
        decoded_key = b64encode(key).decode('utf-8')
        key_text_11 = decoded_key[0:10]
        key_textbox.insert("0.0", key_text_11 + "...")

        def encrypt_key_copy():
            pyperclip.copy(decoded_key)
        encrypt_copy_button = customtkinter.CTkButton(key_textbox_frame,width=23,height=26,image=encrypt_copy_button_img,hover=False,fg_color="#000000",text="",command=encrypt_key_copy)
    
        encrypt_copy_button.place(x=255,y=18)
        key_textbox.configure(state="disabled")

        ct = b64encode(ct_bytes).decode('utf-8')
        user_encrypted_text_textbox.configure(state="normal")
        user_encrypted_text_textbox.delete("0.0", "end")
        user_encrypted_text_textbox.insert("0.0", ct)
        user_encrypted_text_textbox.configure(state="disabled")

        title = encrypt_title_textbox.get('0.0', 'end').strip()
        conn = sqlite3.connect('enigma_guard_data.db')
        c = conn.cursor()
        encryption_type = "CFB"
        c.execute("""CREATE TABLE IF NOT EXISTS enigma_guard_data 
          (
          title text,
          encryption_type text,
          cipher_text bool,
          iv bool,
          nonce bool,
          key bool,
          encryption_code integer,
          date text
          )""")
    
        c.execute("INSERT INTO enigma_guard_data VALUES (:title, :encryption_type, :cipher_text, :iv, :nonce, :encryption_code, :key, :date)", {'title': title,'encryption_type': encryption_type,'cipher_text': ct, 'iv': iv, 'nonce': "Not present", 'key': decoded_key, 'encryption_code': 4, 'date': x.strftime("%d"+ "/" +"%m"+ "/" +"%Y")})
        conn.commit()
        increment_encryptions()
        increment_encryptions_decryptions()
        increment_overall_encryptions()
        conn.close()
        
    def ofb():
        message = user_encrypt_text_textbox.get('0.0', 'end').encode('utf-8')

        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_OFB)
        ct_bytes = cipher.encrypt(pad(message, AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        key_textbox.configure(state="normal")
        key_textbox.delete("0.0", "end")
        decoded_key = b64encode(key).decode('utf-8')
        key_text_11 = decoded_key[0:10]
        key_textbox.insert("0.0", key_text_11 + "...")

        def encrypt_key_copy():
            pyperclip.copy(decoded_key)
        encrypt_copy_button = customtkinter.CTkButton(key_textbox_frame,width=23,height=26,image=encrypt_copy_button_img,hover=False,fg_color="#000000",text="",command=encrypt_key_copy)
    
        encrypt_copy_button.place(x=255,y=18)
        key_textbox.configure(state="disabled")

        ct = b64encode(ct_bytes).decode('utf-8')
        user_encrypted_text_textbox.configure(state="normal")
        user_encrypted_text_textbox.delete("0.0", "end")
        user_encrypted_text_textbox.insert("0.0", ct)
        user_encrypted_text_textbox.configure(state="disabled")

        title = encrypt_title_textbox.get('0.0', 'end').strip()
        conn = sqlite3.connect('enigma_guard_data.db')
        c = conn.cursor()
        encryption_type = "OFB"
        c.execute("""CREATE TABLE IF NOT EXISTS enigma_guard_data 
          (
          title text,
          encryption_type text,
          cipher_text bool,
          iv bool,
          nonce bool,
          key bool,
          encryption_code integer,
          date text
          )""")
    
        c.execute("INSERT INTO enigma_guard_data VALUES (:title, :encryption_type, :cipher_text, :iv, :nonce, :key, :encryption_code, :date)", {'title': title,'encryption_type': encryption_type,'cipher_text': ct, 'iv': iv, 'nonce': "Not present", 'key': decoded_key, 'encryption_code': 5, 'date': x.strftime("%d"+ "/" +"%m"+ "/" +"%Y")})
        conn.commit()
        increment_encryptions()
        increment_encryptions_decryptions()
        increment_overall_encryptions()
        conn.close()

    def complete_encryption():
        title = encrypt_title_textbox.get('0.0','end').strip()
        conn  = sqlite3.connect("enigma_guard_data.db")
        cursor = conn.cursor()
        if encrypt_title_textbox.get('0.0','end').strip() == "Title" or encrypt_title_textbox.get('0.0', 'end').strip() == "":
            CTkMessagebox(title="Error: E003", message="Enter a title to initiate encryption", icon="cancel")
        elif title:
            cursor.execute("SELECT * FROM enigma_guard_data WHERE title=?", (title,))
            result = cursor.fetchone()
            conn.close()
            if result:
                CTkMessagebox(title="Error: E002", message="Title already exists in database", icon="cancel")
            else:
                if encryption_type_optionmenu.get() == "Fernet":
                    fernet_encryption()
                elif encryption_type_optionmenu.get() == "CBC":
                    cbc()
                elif encryption_type_optionmenu.get() == "CTR":
                    ctr()
                elif encryption_type_optionmenu.get() == "CFB":
                    cfb()
                elif encryption_type_optionmenu.get() == "OFB":
                    ofb()
                else:
                    CTkMessagebox(title="Error: E009", message="Select encryption method", icon="cancel")

    encrypt_button = customtkinter.CTkButton(encrypt_frame_win,width=300,height=70,text="",fg_color="#1FFFA9",text_color="#000000",font=armin_grotesk_ultra_bold,anchor='center',image=encrypt_button_img,hover=False,command=complete_encryption)
    encrypt_button.place(x=838,y=795)

def decrypt_win():
    if analytics_frame_win.winfo_ismapped():
        analytics_frame_win.pack_forget()
    elif encrypt_frame_win.winfo_ismapped():
        encrypt_frame_win.pack_forget()
    elif keys_frame_win.winfo_ismapped():
        keys_frame_win.pack_forget()
    elif settings_frame_win.winfo_ismapped():
        settings_frame_win.pack_forget()

    decrypt_frame_win.pack()

    conn = sqlite3.connect('enigma_guard_data.db')
    c = conn.cursor()

    c.execute("SELECT title FROM enigma_guard_data")
    titles = c.fetchall()
    conn.close()
    title_list = [title[0] for title in titles]

    def update_textbox(selected_title):
        conn = sqlite3.connect('enigma_guard_data.db')
        c = conn.cursor()
        c.execute("SELECT encryption_type, cipher_text FROM enigma_guard_data WHERE title=?", (selected_title,))
        result = c.fetchone()
        if result:
            decryption_type.configure(state="normal")
            decryption_type.delete('0.0','end')
            decryption_type.insert('0.0', result[0])
            decryption_type.configure(state="disabled")
            user_decrypt_text_textbox.configure(state='normal')
            user_decrypt_text_textbox.delete('0.0','end')
            user_decrypt_text_textbox.insert('0.0', result[1])
            user_decrypt_text_textbox.configure(state="disabled")

    def on_option_selected(event):
        selected_title = decryption_type_optionmenu.get()
        update_textbox(selected_title)

    decryption_type_optionmenu = customtkinter.CTkOptionMenu(decrypt_frame_win, values=["Title"] + title_list ,fg_color="#000000",width=294,height=64,dropdown_fg_color="#000000",font=armin_grotesk_ultra_bold,dropdown_font=armin_grotesk_ultra_bold,hover=False,button_color="#1FFFA9",corner_radius=3,dynamic_resizing=False,dropdown_text_color="#FFFFFF",command=on_option_selected)
    decryption_type_optionmenu.set("Title")
    decryption_type_optionmenu.place(x=428,y=125)

    decryption_type_frame = customtkinter.CTkFrame(master = decrypt_frame_win,width=300,height=70,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    decryption_type_frame.place(x=840,y=122)
    decryption_type = customtkinter.CTkTextbox(decryption_type_frame,width=270,height=34,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent",activate_scrollbars=False,wrap=None)
    decryption_type.insert("0.0", "Encryption type")
    decryption_type.configure(state="disabled")
    decryption_type.place(x=10,y=10)
    decryption_type_value = decryption_type.get('0.0','end')
    decrypt_key_textbox_frame = customtkinter.CTkFrame(master = decrypt_frame_win,width=300,height=70,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    decrypt_key_textbox_frame.place(x=1256,y=122)
    decrypt_key_textbox = customtkinter.CTkTextbox(decrypt_key_textbox_frame,width=270,height=34,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent",activate_scrollbars=False)
    decrypt_key_textbox.insert("0.0", "Key")
    decrypt_key_textbox.place(x=10,y=10)

    def decryption_title_textbox_clear_text(event):
        if decrypt_key_textbox.get("0.0", "end").strip() == "Key":
            decrypt_key_textbox.delete("0.0", "end")

    def reset_default_text(event):
        if not decrypt_key_textbox.get("0.0", "end").strip():
            decrypt_key_textbox.insert("0.0", "Key")

    decrypt_key_textbox.bind("<FocusIn>", decryption_title_textbox_clear_text)
    decrypt_key_textbox.bind("<FocusOut>", reset_default_text)
    decrypt_key_textbox.get("0.0", "end")
    decrypt_key_textbox.bind("<Tab>", on_tab_pressed)

    user_decrypt_text_textbox_frame = customtkinter.CTkFrame(master = decrypt_frame_win,width=1148,height=250,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    user_decrypt_text_textbox_frame.place(x=410,y=230)
    user_decrypt_text_textbox = customtkinter.CTkTextbox(user_decrypt_text_textbox_frame,width=1118,height=220,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent")
    user_decrypt_text_textbox.insert("0.0", "Encrypted text")
    user_decrypt_text_textbox.configure(state="disabled")
    user_decrypt_text_textbox.place(x=10,y=10)

    user_decrypted_text_textbox_frame = customtkinter.CTkFrame(master = decrypt_frame_win,width=1148,height=250,border_color="#1FFFA9",border_width=3,corner_radius=5,fg_color="#000000")
    user_decrypted_text_textbox_frame.place(x=410,y=515)
    user_decrypted_text_textbox = customtkinter.CTkTextbox(user_decrypted_text_textbox_frame,width=1118,height=220,text_color="#FFFFFF",font=armin_grotesk_ultra_bold,fg_color="transparent")
    user_decrypted_text_textbox.insert("0.0", "Decrypted text")
    user_decrypted_text_textbox.place(x=10,y=10)
    user_decrypted_text_textbox.configure(state="disabled")
    
    def retrieve_data_by_title(title):
        conn = sqlite3.connect('enigma_guard_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM enigma_guard_data WHERE title = ?', (title,))
        data = c.fetchall()
        if data:
            for row in data:
                decryption_key = decrypt_key_textbox.get('0.0','end')
                if row[6] == 1:
                    try:
                        fernet = FER(decryption_key)
                        decmessage = fernet.decrypt(row[2]).decode()
                        user_decrypted_text_textbox.configure(state='normal')
                        user_decrypted_text_textbox.delete('0.0','end')
                        user_decrypted_text_textbox.insert('0.0', decmessage)
                        user_decrypted_text_textbox.configure(state="disabled")
                        increment_encryptions()
                        increment_encryptions_decryptions()
                        increment_decryptions()
                        increment_overall_decryptions()
                    except:
                        CTkMessagebox(title="Error: E005", message="Incorrect decryption key", icon="cancel")
                elif row[6] == 2:
                    try:
                        iv = b64decode(row[3])
                        ct = b64decode(row[2])
                        key = b64decode(decryption_key)
                        cipher = AES.new(key, AES.MODE_CBC, iv)
                        decmessage = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
                        user_decrypted_text_textbox.configure(state='normal')
                        user_decrypted_text_textbox.delete('0.0','end')
                        user_decrypted_text_textbox.insert('0.0', decmessage)
                        user_decrypted_text_textbox.configure(state="disabled")
                        increment_encryptions()
                        increment_encryptions_decryptions()
                        increment_decryptions()
                        increment_overall_decryptions()
                    except (ValueError, KeyError):
                        CTkMessagebox(title="Error: E005", message="Incorrect decryption key", icon="cancel")
                elif row[6] == 3:
                    try:
                        nonce = b64decode(row[4])
                        ct = b64decode(row[2])
                        key = b64decode(decryption_key)
                        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
                        decmessage = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
                        user_decrypted_text_textbox.configure(state='normal')
                        user_decrypted_text_textbox.delete('0.0','end')
                        user_decrypted_text_textbox.insert('0.0', decmessage)
                        user_decrypted_text_textbox.configure(state="disabled")
                        increment_encryptions()
                        increment_encryptions_decryptions()
                        increment_decryptions()
                        increment_overall_decryptions()
                    except (ValueError, KeyError):
                        CTkMessagebox(title="Error: E005", message="Incorrect decryption key", icon="cancel")
                elif row[6] == 4:
                    try:
                        iv = b64decode(row[3])
                        ct = b64decode(row[2])
                        key = b64decode(decryption_key)
                        cipher = AES.new(key, AES.MODE_CFB, iv)
                        decmessage = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
                        user_decrypted_text_textbox.configure(state='normal')
                        user_decrypted_text_textbox.delete('0.0','end')
                        user_decrypted_text_textbox.insert('0.0', decmessage)
                        user_decrypted_text_textbox.configure(state="disabled")
                        increment_encryptions()
                        increment_encryptions_decryptions()
                        increment_decryptions()
                        increment_overall_decryptions()
                    except (ValueError, KeyError):
                        CTkMessagebox(title="Error: E005", message="Incorrect decryption key", icon="cancel")
                elif row[6] == 5:
                    try:
                        iv = b64decode(row[3])
                        ct = b64decode(row[2])
                        key = b64decode(decryption_key)
                        cipher = AES.new(key, AES.MODE_OFB, iv=iv)
                        decmessage = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
                        user_decrypted_text_textbox.configure(state='normal')
                        user_decrypted_text_textbox.delete('0.0','end')
                        user_decrypted_text_textbox.insert('0.0', decmessage)
                        user_decrypted_text_textbox.configure(state="disabled")
                        increment_encryptions()
                        increment_encryptions_decryptions()
                        increment_decryptions()
                        increment_overall_decryptions()
                    except (ValueError, KeyError):
                        CTkMessagebox(title="Error: E005", message="Incorrect decryption key", icon="cancel")
                else:
                    CTkMessagebox(title="Error: E003", message="Padding error, restart the application", icon="cancel")
        conn.close()
    
    def get_data():
        title_to_search = decryption_type_optionmenu.get()
        retrieve_data_by_title(title_to_search)

    decrypt_button = customtkinter.CTkButton(decrypt_frame_win, width=300, height=70, text="", fg_color="#1FFFA9", text_color="#000000", font=armin_grotesk_ultra_bold, anchor='center', image=decrypt_button_img, hover=False, command=get_data)
    decrypt_button.place(x=838, y=795)

def keys_win():
    if analytics_frame_win.winfo_ismapped():
        analytics_frame_win.pack_forget()
    elif encrypt_frame_win.winfo_ismapped():
        encrypt_frame_win.pack_forget()
    elif decrypt_frame_win.winfo_ismapped():
        decrypt_frame_win.pack_forget()
    elif settings_frame_win.winfo_ismapped():
        settings_frame_win.pack_forget()

    keys_frame_win.pack()

    def keys_label_win():
        global keys_label_frame_win   
        keys_label_frame_win = customtkinter.CTkScrollableFrame(keys_frame_win, width=1135, height=750, bg_color="black",fg_color="black",label_anchor="s",scrollbar_button_color="#1FFFA9")
        keys_label_frame_win.place(x=410,y=90)

    keys_label_win()

    conn = sqlite3.connect('enigma_guard_data.db')
    c = conn.cursor()
    c.execute("SELECT title, key, date FROM enigma_guard_data")
    data = c.fetchall()
    conn.close()

    def delete_row(title):
        conn = sqlite3.connect('enigma_guard_data.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM enigma_guard_data WHERE title = ?", (title,))
        conn.commit()
        conn.close()

    def fetch_data():
        conn = sqlite3.connect('enigma_guard_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, key, date FROM enigma_guard_data")
        data = cursor.fetchall()
        conn.close()
        return data
    
    def create_labels():
        data = fetch_data()
        label_widgets = []
        button_widgets = []
        def delete_wrapper(title, label, label2, button_label_2_copy, label3, row_delete_button, title_label):
            def delete_widgets():
                delete_row(title)
                label.destroy()
                label2.destroy()
                button_label_2_copy.destroy()
                label3.destroy()
                row_delete_button.destroy()
                title_label.destroy()
                keys_label_frame_win_refresh()
            return delete_widgets
        
        initial_y = 10
        label_height = 60
        y_offset = 40
        initial_y_for_secondary_label = 35
        initial_y_for_copy_button = 32

        def label_2_copy(key_to_copy):
            def copy_key():
                pyperclip.copy(key_to_copy)
            return copy_key

        for row in data:
            
            copy_func = label_2_copy(row[1])

            title_label = customtkinter.CTkLabel(keys_label_frame_win, width=1135, height=70, bg_color="#000000", fg_color="#000000", image=number_of_keys_img, text="")
            title_label.pack(pady=15)
            
            label = customtkinter.CTkLabel(keys_label_frame_win, text=row[0], font=armin_grotesk_ultra_bold, text_color="#FFFFFF", bg_color="#000000", fg_color="#000000")
            label.place(x=90, y=initial_y_for_secondary_label)

            label2 = customtkinter.CTkLabel(keys_label_frame_win, text=row[1][0:19]+"...", font=armin_grotesk_ultra_bold, text_color="#FFFFFF", bg_color="#000000", fg_color="#000000")
            label2.place(x=390, y=initial_y_for_secondary_label)

            button_label_2_copy = customtkinter.CTkButton(keys_label_frame_win, text="", bg_color="#000000", fg_color="#000000", hover=False, command=copy_func, image=encrypt_copy_button_img, width=30)
            button_label_2_copy.place(x=727, y=initial_y_for_copy_button)

            label3 = customtkinter.CTkLabel(keys_label_frame_win, text=row[2], font=armin_grotesk_ultra_bold, text_color="#FFFFFF", bg_color="#000000", fg_color="#000000")
            label3.place(x=879, y=initial_y_for_secondary_label)

            row_delete_button = customtkinter.CTkButton(keys_label_frame_win, text="", bg_color="#000000", fg_color="#000000", hover=False, image=delete_button_img, width=30)
            row_delete_button.place(x=1060, y=initial_y_for_copy_button)

            row_delete_button.configure(command=delete_wrapper(row[0], label, label2, button_label_2_copy, label3, row_delete_button,title_label))

            initial_y += y_offset + label_height
            initial_y_for_secondary_label += y_offset + label_height
            initial_y_for_copy_button += y_offset + label_height

            label_widgets.extend([title_label, label, label2, label3, button_label_2_copy, row_delete_button])
            button_widgets.append(button_label_2_copy)
        return label_widgets, button_widgets

    create_labels()
    def keys_label_frame_win_refresh():
        keys_label_frame_win.destroy()
        keys_label_win()
        create_labels()

def settings_win():
    if analytics_frame_win.winfo_ismapped():
        analytics_frame_win.pack_forget()
    elif encrypt_frame_win.winfo_ismapped():
        encrypt_frame_win.pack_forget()
    elif decrypt_frame_win.winfo_ismapped():
        decrypt_frame_win.pack_forget()
    elif keys_frame_win.winfo_ismapped():
        keys_frame_win.pack_forget()
    
    settings_frame_win.pack()


armin_grotesk = customtkinter.CTkFont(family="Armin Grotesk", size=24, weight="bold")
armin_grotesk_ultra_bold = customtkinter.CTkFont(family="Armin Grotesk UltraBold",size=24,weight="normal")
armin_grotesk_ultra_bold_30 = customtkinter.CTkFont(family="Armin Grotesk UltraBold",size=48,weight="normal")

analytics_tab_deselect_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\analytics_tab_deselect.png"),dark_image=Image.open(".\\_internal\\assets\\analytics_tab_deselect.png"),size=(324,74.77))
encrypt_tab_deselect_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\encrypt_tab_deselect.png"),dark_image=Image.open(".\\_internal\\assets\\encrypt_tab_deselect.png"),size=(324,74.77))
decrypt_tab_deselect_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\decrypt_tab_deselect.png"),dark_image=Image.open(".\\_internal\\assets\\decrypt_tab_deselect.png"),size=(324,74.77))
keys_tab_deselect_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\keys_tab_deselect.png"),dark_image=Image.open(".\\_internal\\assets\\keys_tab_deselect.png"),size=(324,74.77))
settings_tab_deselect_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\settings_tab_deselect.png"),dark_image=Image.open(".\\_internal\\assets\\settings_tab_deselect.png"),size=(324,74.77))
analytics_tab_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\analytics_tab.png"),dark_image=Image.open(".\\_internal\\assets\\analytics_tab.png"),size=(324,74.77))
encrypt_tab_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\encrypt_tab.png"),dark_image=Image.open(".\\_internal\\assets\\encrypt_tab.png"),size=(324,74.77))
decrypt_tab_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\decrypt_tab.png"),dark_image=Image.open(".\\_internal\\assets\\decrypt_tab.png"),size=(324,74.77))
keys_tab_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\keys_tab.png"),dark_image=Image.open(".\\_internal\\assets\\keys_tab.png"),size=(324,74.77))
settings_tab_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\settings_tab.png"),dark_image=Image.open(".\\_internal\\assets\\settings_tab.png"),size=(324,74.77))
encryption_type_optionmenu_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\encryption_type_optionmenu.png"),dark_image=Image.open(".\\_internal\\assets\\encryption_type_optionmenu.png"),size=(310,70))
decryption_type_optionmenu_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\decryption_type_optionmenu.png"),dark_image=Image.open(".\\_internal\\assets\\decryption_type_optionmenu.png"),size=(310,70))
encrypt_copy_button_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\copy_button.png"),dark_image=Image.open(".\\_internal\\assets\\copy_button.png"),size=(22.17,25.67))
encrypt_frame_win_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\encryption_main.png"), dark_image=Image.open(".\\_internal\\assets\\encryption_main.png"),size=(1600,900))
decrypt_frame_win_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\decryption_main.png"), dark_image=Image.open(".\\_internal\\assets\\decryption_main.png"),size=(1600,900))
analytics_frame_win_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\sec_win.png"), dark_image=Image.open(".\\_internal\\assets\\sec_win.png"),size=(1600,900))
bg_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\bg_image.png"), dark_image=Image.open(".\\_internal\\assets\\bg_image.png"), size=(1600, 900))
ashhad_github_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\github.png"),dark_image=Image.open(".\\_internal\\assets\\github.png"), size=(30, 30))
try_enigma_guard_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\try_enigma_guard.png"), dark_image=Image.open(".\\_internal\\assets\\try_enigma_guard.png"),size=(250,60))
encrypt_button_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\encrypt_button.png"),dark_image=Image.open(".\\_internal\\assets\\encrypt_button.png"),size=(300,70))
decrypt_button_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\decrypt_button.png"),dark_image=Image.open(".\\_internal\\assets\\decrypt_button.png"),size=(300,70))
key_frame_win_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\keys_main.png"), dark_image=Image.open(".\\_internal\\assets\\keys_main.png"), size=(1600,900))
setting_frame_win_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\settings_main.png"), dark_image=Image.open(".\\_internal\\assets\\settings_main.png"), size=(1600,900))
number_of_keys_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\number_of_keys.png"), dark_image=Image.open(".\\_internal\\assets\\number_of_keys.png"),size=(1135,70))
delete_button_img = customtkinter.CTkImage(light_image=Image.open(".\\_internal\\assets\\delete_button.jpg"), dark_image=Image.open(".\\_internal\\assets\\delete_button.jpg"),size=(23,25.88))
settings_minimize = customtkinter.CTkImage(light_image=Image.open('.\\_internal\\assets\\settings_minimize.png'),dark_image=Image.open('.\\_internal\\assets\\settings_minimize.png'),size=(1135,100))


frame_main_win = customtkinter.CTkLabel(app, width=1600, height=900, image=bg_img,text="")
frame_main_win.pack()
analytics_frame_win = customtkinter.CTkLabel(app, text="",image=analytics_frame_win_img)
encrypt_frame_win = customtkinter.CTkLabel(app, text="", image=encrypt_frame_win_img)
decrypt_frame_win = customtkinter.CTkLabel(app, text="",image=decrypt_frame_win_img)
keys_frame_win = customtkinter.CTkLabel(app, text="", image=key_frame_win_img)
settings_frame_win = customtkinter.CTkLabel(app, text="", image=setting_frame_win_img)

try_enigma_guard = customtkinter.CTkButton(frame_main_win, width=250,height=60,image=try_enigma_guard_img,text="",border_width=0,border_spacing=0,hover=False,border_color="#000000",bg_color="#000000",fg_color="#000000",command=analytics_win)
try_enigma_guard.place(x=202,y=584)

def ashhad_github_callback():
    webbrowser.open('https://github.com/Ashhad776')
    frame = customtkinter.CTkLabel(frame_main_win, width=1280, height=720, image=bg_img,text="")
    frame.pack()

ashhad_github = customtkinter.CTkButton(frame_main_win, width=30, height=30, image=ashhad_github_img,text="", bg_color="#000000", fg_color="#000000",hover=True,hover_color="#42414D",command=ashhad_github_callback)
ashhad_github.place(x=1515,y=27)

total_encryptions_decryptions_label = customtkinter.CTkLabel(analytics_frame_win, width=47,height=44,text="00",font=armin_grotesk_ultra_bold_30,bg_color="#000000",fg_color="#000000")
total_encryptions_decryptions_label.place(x=157,y=180)

total_app_time = customtkinter.CTkLabel(analytics_frame_win, text="00 hrs", font=armin_grotesk_ultra_bold_30, width=47,height=44,bg_color="#000000",fg_color="#000000")
total_app_time.place(x=1350 ,y=190)

active_keys = customtkinter.CTkLabel(analytics_frame_win, text="00", font=armin_grotesk_ultra_bold_30,width=47,height=44,bg_color="#000000",fg_color="#000000")
active_keys.place(x=1100,y=190)

#total encryptions keys analytics frame
total_encryptions_analytic_frame_label = customtkinter.CTkLabel(analytics_frame_win, text="00", font=armin_grotesk_ultra_bold_30,width=47,height=44,bg_color="#000000",fg_color="#000000")
total_encryptions_analytic_frame_label.place(x=524,y=190)

#total decryptions keys analytics frame
total_decryptions_analytic_frame_label = customtkinter.CTkLabel(analytics_frame_win, text="00", font=armin_grotesk_ultra_bold_30,width=47,height=44,bg_color="#000000",fg_color="#000000")
total_decryptions_analytic_frame_label.place(x=814,y=190)

def save_elapsed_time(elapsed_hours):
    with open(".\\_internal\\src\\elapsed_time.txt", "w") as file:
        file.write(str(elapsed_hours))
def load_elapsed_time():
    try:
        with open(".\\_internal\\src\\elapsed_time.txt", "r") as file:
            return float(file.read())
    except FileNotFoundError:
        return 0.0
start_time = datetime.now()

def update_time():
    global start_time
    current_time = datetime.now()
    elapsed_seconds_from_file = load_elapsed_time()
    elapsed_time = current_time - start_time + timedelta(seconds=elapsed_seconds_from_file)
    elapsed_seconds = elapsed_time.total_seconds()
    save_elapsed_time(elapsed_seconds)
    update_display(elapsed_seconds)
    start_time = current_time
    app.after(30, update_time)

def update_display(elapsed_seconds):
    hours = int(elapsed_seconds // 3600)
    formatted_time = f"{hours:02d}"
    total_app_time.configure(text=f"{formatted_time} hrs")

def save_data(data, filename):
    with open(filename, "w") as file:
        file.write(str(data))

def increment_encryptions():
    global total_encryptions
    today = date.today().isoformat()

    total_encryptions += 1

    encryption_data = read_encryption_info()

    encryption_data[today] = total_encryptions

    with open(".\\_internal\\src\\encryption_info.txt", "w") as file:
        for date_key, value in encryption_data.items():
            file.write(f"{date_key}:{value}\n")

def read_encryption_info():
    encryption_data = {}
    try:
        with open(".\\_internal\\src\\encryption_info.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(':')
                encryption_data[parts[0]] = int(parts[1])
    except FileNotFoundError:
        pass
    return encryption_data
    
def increment_decryptions():
    global total_decryptions
    today = date.today().isoformat()

    total_decryptions += 1

    decryption_data = read_decryption_info()

    decryption_data[today] = total_decryptions

    # Writing data to a text file
    with open(".\\_internal\\src\\decryption_info.txt", "w") as file:
        for date_key, value in decryption_data.items():
            file.write(f"{date_key}:{value}\n")

def read_decryption_info():
    decryption_data = {}
    try:
        with open(".\\_internal\\src\\decryption_info.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(':')
                decryption_data[parts[0]] = int(parts[1])
    except FileNotFoundError:
        pass
    return decryption_data


def increment_encryptions_decryptions():
    try:
        with open(".\\_internal\\src\\total_encryptions_decryption_count.pickle", "rb+") as file:
            try:
                count = pickle.load(file)
                count += 1
            except EOFError:
                count = 1
            
            file.seek(0)
            file.truncate()
            pickle.dump(count, file)
    except FileNotFoundError:
        with open(".\\_internal\\src\\total_encryptions_decryption_count.pickle", "wb") as file:
            count = 1
            pickle.dump(count, file)
            update_display(1)

def read_total_encryptions_decryptions():
    try:
        with open(".\\_internal\\src\\total_encryptions_decryption_count.pickle", "rb") as file:
            count = pickle.load(file)
    except FileNotFoundError:
        count = 0

    return count

def update_total_encryptions_decryptions_label(total_encryptions_decryptions_label):
    try:
        total_encryptions_decryptions_label.configure(text=read_total_encryptions_decryptions())
        analytics_frame_win.after(1000, update_total_encryptions_decryptions_label, total_encryptions_decryptions_label)
    except Exception as e:
        CTkMessagebox(title="Error: E011", message=f"Traceback error occured {e}", icon="cancel")
        traceback.print_exc()

def read_overall_decryptions():
    try:
        with open(".\\_internal\\src\\total_decryption_count.pickle", "rb") as file:
            count = pickle.load(file)
    except FileNotFoundError:
        count = 0

    return count

def increment_overall_decryptions():
    try:
        with open(".\\_internal\\src\\total_decryption_count.pickle", "rb+") as file:
            try:
                count = pickle.load(file)
                count += 1
            except EOFError:
                count = 1
            
            file.seek(0)
            file.truncate()
            pickle.dump(count, file)
    except FileNotFoundError:
        with open(".\\_internal\\src\\total_decryption_count.pickle", "wb") as file:
            count = 1
            pickle.dump(count, file)
            update_display(1)

def update_total_decryptions_analytic_frame_label(total_decryptions_analytic_frame_label):
    try:
        total_decryptions_analytic_frame_label.configure(text=read_overall_decryptions())
        analytics_frame_win.after(1000, update_total_decryptions_analytic_frame_label, total_decryptions_analytic_frame_label)
    except Exception as e:
        CTkMessagebox(title="Error: E011", message=f"Traceback error occured {e}", icon="cancel")
        traceback.print_exc()

def read_overall_encryptions():
    try:
        with open(".\\_internal\\src\\total_encryption_count.pickle", "rb") as file:
            count = pickle.load(file)
    except FileNotFoundError:
        count = 0

    return count

def increment_overall_encryptions():
    try:
        with open(".\\_internal\\src\\total_encryption_count.pickle", "rb+") as file:
            try:
                count = pickle.load(file)
                count += 1
            except EOFError:
                count = 1
            
            file.seek(0)
            file.truncate()
            pickle.dump(count, file)
    except FileNotFoundError:
        with open(".\\_internal\\src\\total_encryption_count.pickle", "wb") as file:
            count = 1
            pickle.dump(count, file)
            update_display(1)

def update_total_encryptions_analytic_frame_label(total_encryptions_analytic_frame_label):
    try:
        total_encryptions_analytic_frame_label.configure(text=read_overall_encryptions())
        analytics_frame_win.after(1000, update_total_encryptions_analytic_frame_label, total_encryptions_analytic_frame_label)
    except Exception as e:
        CTkMessagebox(title="Error: E011", message=f"Traceback error occured {e}", icon="cancel")
        traceback.print_exc()

def read_overall_decryptions():
    try:
        with open(".\\_internal\\src\\total_decryption_count.pickle", "rb") as file:
            count = pickle.load(file)
    except FileNotFoundError:
        count = 0

    return count

def increment_overall_decryptions():
    try:
        with open(".\\_internal\\src\\total_decryption_count.pickle", "rb+") as file:
            try:
                count = pickle.load(file)
                count += 1
            except EOFError:
                count = 1
            
            file.seek(0)
            file.truncate()
            pickle.dump(count, file)
    except FileNotFoundError:
        with open(".\\_internal\\src\\total_decryption_count.pickle", "wb") as file:
            count = 1
            pickle.dump(count, file)
            update_display(1)

def update_total_decryptions_analytic_frame_label(total_decryptions_analytic_frame_label):
    try:
        total_decryptions_analytic_frame_label.configure(text=read_overall_decryptions())
        analytics_frame_win.after(1000, update_total_decryptions_analytic_frame_label, total_decryptions_analytic_frame_label)
    except Exception as e:
        CTkMessagebox(title="Error: E011", message=f"Traceback error occured {e}", icon="cancel")
        traceback.print_exc()

def read_overall_keys(active_keys):
    conn = sqlite3.connect("enigma_guard_data.db")
    c = conn.cursor()
    c.execute("SELECT key FROM enigma_guard_data")
    keys = c.fetchall()
    conn.close()
    total_keys = len(keys)
    active_keys.configure(text=total_keys)
    analytics_frame_win.after(1000, read_overall_keys, active_keys)

read_overall_keys(active_keys)

def update_pygal_analytics_graph(pygal_analytics_graph):
    try:
        analytics_frame_win.after(1000, update_pygal_analytics_graph, pygal_analytics_graph)
    except Exception as e:
        CTkMessagebox(title="Error: E011", message=f"Traceback error occured {e}", icon="cancel")
        traceback.print_exc()

#analytic window
analytics_tab = customtkinter.CTkButton(analytics_frame_win, text="",image=analytics_tab_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False)
analytics_tab.place(x=17,y=330)

encrypt_deselect_tab = customtkinter.CTkButton(analytics_frame_win, text="",image=encrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=encrypt_win)
encrypt_deselect_tab.place(x=17,y=424) 
        
decrypt_deselect_tab = customtkinter.CTkButton(analytics_frame_win, text="",image=decrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=decrypt_win)
decrypt_deselect_tab.place(x=17,y=518)

keys_deselect_tab = customtkinter.CTkButton(analytics_frame_win, text="",image=keys_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=keys_win)
keys_deselect_tab.place(x=17,y=612)

settings_deselect_tab = customtkinter.CTkButton(analytics_frame_win, text="",image=settings_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=settings_win)
settings_deselect_tab.place(x=17,y=707)

#encrypt window
total_encryptions_decryptions_label2 = customtkinter.CTkLabel(encrypt_frame_win, width=47,height=44,text="00",font=armin_grotesk_ultra_bold_30,bg_color="#000000",fg_color="#000000")
total_encryptions_decryptions_label2.place(x=157,y=180)

analytics_deselect_tab = customtkinter.CTkButton(encrypt_frame_win, text="",image=analytics_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=analytics_win)
analytics_deselect_tab.place(x=17,y=330)

encrypt_tab = customtkinter.CTkButton(encrypt_frame_win, text="",image=encrypt_tab_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False)
encrypt_tab.place(x=17,y=424)

decrypt_deselect_tab = customtkinter.CTkButton(encrypt_frame_win, text="",image=decrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=decrypt_win)
decrypt_deselect_tab.place(x=17,y=518)

keys_deselect_tab = customtkinter.CTkButton(encrypt_frame_win, text="",image=keys_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=keys_win)
keys_deselect_tab.place(x=17,y=612)

settings_deselect_tab = customtkinter.CTkButton(encrypt_frame_win, text="",image=settings_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=settings_win)
settings_deselect_tab.place(x=17,y=707)

#decrypt window
total_encryptions_decryptions_label3 = customtkinter.CTkLabel(decrypt_frame_win, width=47,height=44,text="00",font=armin_grotesk_ultra_bold_30,bg_color="#000000",fg_color="#000000")
total_encryptions_decryptions_label3.place(x=157,y=180)

analytics_tab_deselect = customtkinter.CTkButton(decrypt_frame_win, text="",image=analytics_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=analytics_win)
analytics_tab_deselect.place(x=17,y=330)

encrypt_tab_deselect = customtkinter.CTkButton(decrypt_frame_win, text="",image=encrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=encrypt_win)
encrypt_tab_deselect.place(x=17,y=424)

decrypt_tab = customtkinter.CTkButton(decrypt_frame_win, text="",image=decrypt_tab_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False)
decrypt_tab.place(x=17,y=518)

keys_deselect_tab = customtkinter.CTkButton(decrypt_frame_win, text="",image=keys_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=keys_win)
keys_deselect_tab.place(x=17,y=612)

settings_deselect_tab = customtkinter.CTkButton(decrypt_frame_win, text="",image=settings_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=settings_win)
settings_deselect_tab.place(x=17,y=707)

decryption_type_optionmenu_img_frame = customtkinter.CTkLabel(decrypt_frame_win,height=70,width=300,image=decryption_type_optionmenu_img,bg_color="#000000")
decryption_type_optionmenu_img_frame.place(x=410,y=122)

#keys window
total_encryptions_decryptions_label4 = customtkinter.CTkLabel(keys_frame_win, width=47,height=44,text="00",font=armin_grotesk_ultra_bold_30,bg_color="#000000",fg_color="#000000")
total_encryptions_decryptions_label4.place(x=157,y=180)

analytics_tab_deselect = customtkinter.CTkButton(keys_frame_win, text="",image=analytics_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=analytics_win)
analytics_tab_deselect.place(x=17,y=330)

encrypt_tab_deselect = customtkinter.CTkButton(keys_frame_win, text="",image=encrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=encrypt_win)
encrypt_tab_deselect.place(x=17,y=424)

decrypt_tab_deselect = customtkinter.CTkButton(keys_frame_win, text="",image=decrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=decrypt_win)
decrypt_tab_deselect.place(x=17,y=518)

keys_tab = customtkinter.CTkButton(keys_frame_win, text="",image=keys_tab_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False)
keys_tab.place(x=17,y=612)

settings_deselect_tab = customtkinter.CTkButton(keys_frame_win, text="",image=settings_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=settings_win)
settings_deselect_tab.place(x=17,y=707)

#settings window
total_encryptions_decryptions_label5 = customtkinter.CTkLabel(settings_frame_win, width=47,height=44,text="00",font=armin_grotesk_ultra_bold_30,bg_color="#000000",fg_color="#000000")
total_encryptions_decryptions_label5.place(x=157,y=180)

analytics_tab_deselect = customtkinter.CTkButton(settings_frame_win, text="",image=analytics_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=analytics_win)
analytics_tab_deselect.place(x=17,y=330)

encrypt_tab_deselect = customtkinter.CTkButton(settings_frame_win, text="",image=encrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=encrypt_win)
encrypt_tab_deselect.place(x=17,y=424)

decrypt_tab_deselect = customtkinter.CTkButton(settings_frame_win, text="",image=decrypt_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=decrypt_win)
decrypt_tab_deselect.place(x=17,y=518)

keys_tab_deselect = customtkinter.CTkButton(settings_frame_win, text="",image=keys_tab_deselect_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False,command=keys_win)
keys_tab_deselect.place(x=17,y=612)

settings_tab = customtkinter.CTkButton(settings_frame_win, text="",image=settings_tab_img,bg_color="#1FFFA9",fg_color="#1FFFA9",hover=False)
settings_tab.place(x=17,y=707)

def save_checkbox_state(state):
    with open('.\\_internal\\src\\checkbox_state.pickle', 'wb') as file:
        pickle.dump(state, file)

def read_checkbox_state():
    try:
        with open('.\\_internal\\src\\checkbox_state.pickle', 'rb') as file:
            state = pickle.load(file)
            if state == 'on':
                checkbox.select()
                check_var.set('on')
            else:
                checkbox.deselect()
                check_var.set('off')
    except FileNotFoundError:
        return None

def destroy_window():
    checkbox_state = check_var.get()
    save_checkbox_state(checkbox_state)
    if checkbox_state == 'on':
        app.withdraw()

        def open_app():
            icon.stop()
            app.after(0,app.deiconify)

        def app_destroy():
            icon.stop()
            app.destroy()
        
        image = Image.open(".\\_internal\\assets\\ico.png")
        menu=pystray.Menu(pystray.MenuItem("Open enigma:guard",open_app),pystray.MenuItem("Exit", app_destroy))
        icon = pystray.Icon('enigma:guard', image, "enigma:guard", menu)
        icon.run()

    else:
        app.destroy()

settings_minimize_frame = customtkinter.CTkLabel(settings_frame_win,text="",image=settings_minimize)
settings_minimize_frame.place(x=420,y=121)

check_var = customtkinter.StringVar(value="off")
checkbox = customtkinter.CTkCheckBox(settings_minimize_frame, text="", variable=check_var, onvalue="on", offvalue="off",width=30,height=35,checkbox_height=35,checkbox_width=35,border_color="#1FFFA9",bg_color="#000000")
checkbox.place(x=1078,y=33)

app.protocol("WM_DELETE_WINDOW", destroy_window)

label_update = [
    total_encryptions_decryptions_label,
    total_encryptions_decryptions_label2,
    total_encryptions_decryptions_label3,
    total_encryptions_decryptions_label4,
    total_encryptions_decryptions_label5
]

update_time()
update_pygal_analytics_graph(pygal_analytics_graph)
read_checkbox_state()

for label in label_update:
    update_total_encryptions_decryptions_label(label)

update_total_decryptions_analytic_frame_label(total_decryptions_analytic_frame_label)
update_total_encryptions_analytic_frame_label(total_encryptions_analytic_frame_label)

app.mainloop()
