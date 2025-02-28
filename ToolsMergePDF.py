import os
from PyPDF2 import PdfMerger

merger = PdfMerger()


pdf_files =sorted([file for file in os.listdir() if file.endswith(".pdf")])


for pdf in pdf_files:
    merger.append(pdf)

merger.write("hasil_gabungan.pdf")
merger.close()

print("Sukses dan Mantap!!")
