import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PyPDF2 import PdfMerger
import pikepdf


class MergePDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 PDF Merge & Compress Tool")
        self.root.geometry("700x620")
        self.root.resizable(False, False)

        self.file_paths = []

        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=20, pady=(20, 10))
        ttk.Label(header, text="PDF Merge & Compress", font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Label(header, text="by MergePDF Tool", font=("Segoe UI", 10), bootstyle="secondary").pack(side="left", padx=(10, 0), anchor="s", pady=(0, 4))

        # Notebook (tabs)
        notebook = ttk.Notebook(self.root, bootstyle="primary")
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._build_merge_tab(notebook)
        self._build_compress_tab(notebook)

    def _build_merge_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="  📑 Merge PDF  ")

        # Top buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(btn_frame, text="➕ Tambah File", bootstyle="success", command=self._add_files).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="🗑 Hapus", bootstyle="danger-outline", command=self._remove_file).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="🧹 Hapus Semua", bootstyle="danger-outline", command=self._clear_files).pack(side="left")

        # Listbox + scrollbar
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.listbox = tk.Listbox(
            list_frame, height=12, selectmode=tk.SINGLE,
            font=("Segoe UI", 10), relief="flat", bd=0,
            highlightthickness=1, highlightcolor="#4a90d9",
            selectbackground="#4a90d9", selectforeground="white",
            bg="#2b2b2b", fg="#e0e0e0"
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview, bootstyle="primary-round")
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Order + Merge buttons
        bottom_frame = ttk.Frame(tab)
        bottom_frame.pack(fill="x")

        order_frame = ttk.Frame(bottom_frame)
        order_frame.pack(side="left")

        ttk.Button(order_frame, text="⬆ Naik", bootstyle="info-outline", command=self._move_up, width=10).pack(side="left", padx=(0, 5))
        ttk.Button(order_frame, text="⬇ Turun", bootstyle="info-outline", command=self._move_down, width=10).pack(side="left")

        ttk.Button(bottom_frame, text="🔗 Merge PDF", bootstyle="success", command=self._merge, width=18).pack(side="right")

        # File count label
        self.count_label = ttk.Label(tab, text="0 file dipilih", font=("Segoe UI", 9), bootstyle="secondary")
        self.count_label.pack(anchor="w", pady=(5, 0))

    def _build_compress_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="  🗜 Compress PDF  ")

        center = ttk.Frame(tab)
        center.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(center, text="🗜", font=("Segoe UI", 48)).pack(pady=(0, 10))
        ttk.Label(center, text="Compress PDF tanpa mengurangi kualitas", font=("Segoe UI", 12)).pack(pady=(0, 5))
        ttk.Label(center, text="Pilih file PDF lalu otomatis dikompress", font=("Segoe UI", 9), bootstyle="secondary").pack(pady=(0, 20))
        ttk.Button(center, text="📂 Pilih & Compress PDF", bootstyle="warning", command=self._compress, width=25).pack()

        self.compress_result = ttk.Label(tab, text="", font=("Segoe UI", 10), wraplength=500, justify="center")
        self.compress_result.place(relx=0.5, rely=0.75, anchor="center")

    def _update_count(self):
        self.count_label.config(text=f"{len(self.file_paths)} file dipilih")

    def _add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            if f not in self.file_paths:
                self.file_paths.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))
        self._update_count()

    def _remove_file(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            self.listbox.delete(idx)
            self.file_paths.pop(idx)
            self._update_count()

    def _clear_files(self):
        self.listbox.delete(0, tk.END)
        self.file_paths.clear()
        self._update_count()

    def _move_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        self.file_paths[idx], self.file_paths[idx - 1] = self.file_paths[idx - 1], self.file_paths[idx]
        text = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx - 1, text)
        self.listbox.selection_set(idx - 1)

    def _move_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == len(self.file_paths) - 1:
            return
        idx = sel[0]
        self.file_paths[idx], self.file_paths[idx + 1] = self.file_paths[idx + 1], self.file_paths[idx]
        text = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, text)
        self.listbox.selection_set(idx + 1)

    def _merge(self):
        if len(self.file_paths) < 2:
            messagebox.showwarning("Peringatan", "Pilih minimal 2 file PDF.")
            return

        output_dir = os.path.dirname(self.file_paths[0])
        output_path = os.path.join(output_dir, "hasil_gabungan.pdf")

        try:
            merger = PdfMerger()
            for pdf in self.file_paths:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
            messagebox.showinfo("Sukses ✅", f"Merge berhasil!\nDisimpan di:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal merge:\n{e}")

    def _compress(self):
        file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file:
            return

        output_dir = os.path.dirname(file)
        name = os.path.splitext(os.path.basename(file))[0]
        output_path = os.path.join(output_dir, f"{name}_compressed.pdf")

        try:
            pdf = pikepdf.open(file)
            pdf.save(output_path, linearize=True, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
            pdf.close()

            original_size = os.path.getsize(file)
            compressed_size = os.path.getsize(output_path)
            ratio = (1 - compressed_size / original_size) * 100

            self.compress_result.config(
                text=f"✅ Berhasil!\n"
                     f"Asal: {original_size / 1024:.1f} KB → Baru: {compressed_size / 1024:.1f} KB (hemat {ratio:.1f}%)\n"
                     f"📁 {output_path}",
                bootstyle="success"
            )
            messagebox.showinfo("Sukses ✅", f"Compress berhasil!\nHemat {ratio:.1f}%\nDisimpan di:\n{output_path}")
        except Exception as e:
            self.compress_result.config(text=f"❌ Gagal: {e}", bootstyle="danger")
            messagebox.showerror("Error", f"Gagal compress:\n{e}")


if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    MergePDFApp(root)
    root.mainloop()
