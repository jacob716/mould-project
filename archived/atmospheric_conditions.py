import sys
from src.extract import extract_atmospheric_table

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_table.py <path_to_pdf>")
        return

    pdf_path = sys.argv[1]
    try:
        table = extract_atmospheric_table(pdf_path)
        print(table)
    except Exception as e:
        print(f"❌ Failed to extract table: {e}")

if __name__ == "__main__":
    main()
