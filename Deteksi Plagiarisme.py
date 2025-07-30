import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Aplikasi Cek Plagiarisme Mahasiswa")
        self.geometry("1000x600")
        self.mahasiswa_dict = {}
        self.result_stats = {"Ringan": 0, "Sedang": 0, "Berat": 0}

        self.frames = {}
        for F in (MainMenu, UploadPage, ListPage, ComparePage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="\U0001F4D8 Aplikasi Cek Plagiarisme Mahasiswa", font=("Helvetica", 18, "bold")).pack(pady=40)

        tk.Button(self, text="\U0001F4C2 Upload File Mahasiswa", width=30, height=2,
                  command=lambda: controller.show_frame("UploadPage")).pack(pady=10)
        tk.Button(self, text="\U0001F4CB Lihat Daftar Mahasiswa", width=30, height=2,
                  command=lambda: controller.show_frame("ListPage")).pack(pady=10)
        tk.Button(self, text="\U0001F50D Bandingkan Mahasiswa", width=30, height=2,
                  command=lambda: controller.show_frame("ComparePage")).pack(pady=10)
        tk.Button(self, text="\u274C Keluar", width=30, height=2,
                  command=self.quit).pack(pady=10)


class UploadPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="\U0001F4C2 Upload File Mahasiswa", font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Button(self, text="Pilih File .txt", command=self.load_files).pack(pady=10)
        tk.Button(self, text="\u2B05 Kembali ke Menu", command=lambda: controller.show_frame("MainMenu")).pack(pady=10)

    def load_files(self):
        files = filedialog.askopenfilenames(title="Pilih File Tugas Mahasiswa", filetypes=[("Text files", "*.txt")])
        if len(files) < 2:
            messagebox.showwarning("Peringatan", "Pilih minimal 2 file.")
            return

        self.controller.mahasiswa_dict.clear()

        for path in files:
            try:
                filename = os.path.splitext(os.path.basename(path))[0]
                if "_" not in filename:
                    continue

                nim, nama = filename.split("_", 1)
                with open(path, "r", encoding="utf-8") as f:
                    teks = f.read().strip()
                    self.controller.mahasiswa_dict[nim] = {"nama": nama, "nim": nim, "teks": teks}
            except Exception as e:
                messagebox.showerror("Error", f"Kesalahan saat membaca {path}:\n{e}")
                return

        messagebox.showinfo("Sukses", f"{len(self.controller.mahasiswa_dict)} file mahasiswa berhasil dimuat.")


class ListPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="\U0001F4CB Daftar Mahasiswa", font=("Helvetica", 16, "bold")).pack(pady=10)
        self.listbox = tk.Listbox(self, font=("Arial", 12))
        self.listbox.pack(expand=True, fill="both", padx=20, pady=10)
        tk.Button(self, text="\U0001F504 Muat Ulang", command=self.refresh_list).pack(pady=5)
        tk.Button(self, text="\u2B05 Kembali ke Menu", command=lambda: controller.show_frame("MainMenu")).pack(pady=5)

    def refresh_list(self):
        self.listbox.delete(0, "end")
        if not self.controller.mahasiswa_dict:
            self.listbox.insert("end", "Belum ada data mahasiswa yang dimuat.")
            return

        for nim, data in sorted(self.controller.mahasiswa_dict.items()):
            self.listbox.insert("end", f"{nim} - {data['nama']}")


class ComparePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="\U0001F50D Bandingkan Mahasiswa", font=("Helvetica", 16, "bold")).pack(pady=10)

        input_frame = tk.Frame(self)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="NIM/Nama Mahasiswa 1:", anchor="e", width=25).grid(row=0, column=0, pady=5)
        self.nama1_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.nama1_var, width=40).grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="NIM/Nama Mahasiswa 2:", anchor="e", width=25).grid(row=1, column=0, pady=5)
        self.nama2_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.nama2_var, width=40).grid(row=1, column=1, padx=5)

        tk.Button(input_frame, text="Bandingkan", command=self.compare_students, bg="#4CAF50", fg="white").grid(row=2, column=1, pady=5, sticky="w")
        tk.Button(input_frame, text="\U0001F500 Bandingkan Acak", command=self.compare_random_students, bg="#2196F3", fg="white").grid(row=3, column=1, pady=5, sticky="w")
        tk.Button(input_frame, text="\U0001F4CA Lihat Statistik", command=self.show_stats, bg="#FF9800", fg="white").grid(row=4, column=1, pady=5, sticky="w")

        self.tree = ttk.Treeview(self, columns=("Mahasiswa 1", "Mahasiswa 2", "Kemiripan", "Kategori", "Status"), show="headings", height=10)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", stretch=True, width=180)
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

        tk.Button(self, text="\u2B05 Kembali ke Menu", command=lambda: controller.show_frame("MainMenu")).pack(pady=5)

    def get_plagiarism_category(self, percent):
        if percent < 40:
            return "Ringan"
        elif percent <= 70:
            return "Sedang"
        return "Berat"

    def get_plagiarism_status(self, kategori):
        return "Plagiarisme" if kategori in ("Sedang","Berat") else "Bukan Plagiarisme"

    def find_mahasiswa(self, input_text):
        input_text = input_text.lower()
        for nim, data in self.controller.mahasiswa_dict.items():
            if input_text == nim.lower() or input_text in data["nama"].lower():
                return data
        return None

    def compare_students(self):
        input1 = self.nama1_var.get().strip()
        input2 = self.nama2_var.get().strip()
        self.compare_by_input(input1, input2)

    def compare_random_students(self):
        data = list(self.controller.mahasiswa_dict.values())
        if len(data) < 2:
            messagebox.showwarning("Peringatan", "Minimal harus ada 2 mahasiswa untuk membandingkan.")
            return

        mhs1, mhs2 = random.sample(data, 2)
        self.compare_by_data(mhs1, mhs2)

    def compare_by_input(self, input1, input2):
        if not input1 or not input2:
            messagebox.showwarning("Peringatan", "Masukkan kedua nama atau NIM mahasiswa.")
            return
        if input1 == input2:
            messagebox.showwarning("Peringatan", "Tidak bisa membandingkan mahasiswa yang sama.")
            return

        mhs1 = self.find_mahasiswa(input1)
        mhs2 = self.find_mahasiswa(input2)

        if not mhs1 or not mhs2:
            messagebox.showerror("Error", "Mahasiswa tidak ditemukan.")
            return

        self.compare_by_data(mhs1, mhs2)

    def compare_by_data(self, mhs1, mhs2):
        try:
            vectorizer = CountVectorizer()
            bow_matrix = vectorizer.fit_transform([mhs1["teks"], mhs2["teks"]])
            similarity = cosine_similarity(bow_matrix)[0][1]
            percent = round(similarity * 100, 2)
            kategori = self.get_plagiarism_category(percent)
            status = self.get_plagiarism_status(kategori)
            self.controller.result_stats[kategori] += 1

            self.tree.insert("", "end", values=(
                f"{mhs1['nim']} - {mhs1['nama']}",
                f"{mhs2['nim']} - {mhs2['nama']}",
                f"{percent} %",
                kategori,
                status
            ))
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membandingkan: {e}")

    def show_stats(self):
        stats = self.controller.result_stats
        msg = f"\nJumlah Kemiripan:\nRingan: {stats['Ringan']}\nSedang: {stats['Sedang']}\nBerat: {stats['Berat']}"
        messagebox.showinfo("Statistik Kemiripan", msg)


if __name__ == "__main__":
    app = App()
    app.mainloop()
