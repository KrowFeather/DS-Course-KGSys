import pdfplumber

text_path = r"resources/数据结构与算法C语言版.pdf"

with pdfplumber.open(text_path) as pdf:
    total_pages = len(pdf.pages)
    print("total_pages: ", total_pages)

    # fitz读取pdf全文
    content = ""
    for i in range(0, len(pdf.pages)):
        # page=
        content += pdf.pages[i].extract_text()
        # print(page.extract_tables())
    print(content)
