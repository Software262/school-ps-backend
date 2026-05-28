from pypdf import PdfReader


def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        with open("BRD_School_PS_v3.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Success")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    extract_text(r"C:\Users\Rraid\Documents\Juan David\Temporal\BRD_School_PS_v3.pdf")
