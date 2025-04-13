#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a sample PDF file with Vietnamese text for testing the PDF converter
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a Unicode font for Vietnamese characters
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

def create_sample_pdf(output_path):
    """Create a sample PDF file with Vietnamese text"""
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setFont('DejaVuSans', 12)
    
    # Add Vietnamese text to PDF
    c.drawString(100, 750, "Đây là mẫu PDF tiếng Việt để kiểm tra chức năng chuyển đổi.")
    c.drawString(100, 730, "Xin chào! Chương trình chuyển đổi PDF sang TXT.")
    c.drawString(100, 710, "Các ký tự đặc biệt: ă, â, đ, ê, ô, ơ, ư, Ă, Â, Đ, Ê, Ô, Ơ, Ư")
    c.drawString(100, 690, "Các dấu: à, á, ả, ã, ạ, À, Á, Ả, Ã, Ạ")
    
    # Add more text
    c.drawString(100, 650, "Đoạn văn bản này kiểm tra khả năng trích xuất văn bản UTF-8.")
    c.drawString(100, 630, "Việt Nam là một quốc gia ở Đông Nam Á.")
    c.drawString(100, 610, "Hà Nội là thủ đô của Việt Nam.")
    
    # Save the PDF
    c.save()
    print(f"Đã tạo file PDF mẫu tại: {output_path}")

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Create the TaiVe directory if it doesn't exist
    taive_dir = os.path.join(script_dir, "TaiVe")
    if not os.path.exists(taive_dir):
        os.makedirs(taive_dir)
    
    # Create sample PDF file
    sample_pdf_path = os.path.join(taive_dir, "sample_vietnamese.pdf")
    create_sample_pdf(sample_pdf_path)