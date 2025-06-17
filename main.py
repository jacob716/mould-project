from src.extract import extract_conclusion_section
from src.classify import classify_issue

def main():
    pdf_path = "reports/Cornerstone sample DS report[1].pdf"  # Update if filename is different
    conclusion = extract_conclusion_section(pdf_path)

    if conclusion:
        print("=== Extracted Conclusion ===\n")
        print(conclusion)  # Optional: limit preview to first 1000 chars

        print("\n=== Classification ===\n")
        category = classify_issue(conclusion)
        print(f"Predicted issue category: {category}")
    else:
        print("No conclusion section found in the PDF.")

if __name__ == "__main__":
    main()
