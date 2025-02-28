from PyPDF2 import PdfMerger

merger = PdfMerger()


pdf_files = ["005BTU-02-2025-TRF Chapter Developer - TRF - Training Onboarding ACE v2.0.pdf", "FP ACE 2048.pdf", "INV 2048 PT Adicipta Carsani Ekakarya.pdf"]


for pdf in pdf_files:
    merger.append(pdf)

merger.write("hasil_gabungan.pdf")
merger.close()

print("Sukses!!")
