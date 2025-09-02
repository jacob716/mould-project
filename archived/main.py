from src.extract import extract_conclusion_section, extract_full_text
from src.classify import classify_issue, identify_features

def main():
    pdf_path = "reports/Full report sample.pdf"  # Update if filename is different
    full_text = extract_full_text(pdf_path)

    if full_text:
        structure = identify_features(full_text,model='llama3')
        print("\n ===Here is the json=== \n")
        print(structure)
    else:
        print("No text is found in the pdf")

# def main():
#     pdf_path = "reports/Cornerstone sample DS report.pdf"  # Update if filename is different
#     conclusion = extract_conclusion_section(pdf_path)

#     if conclusion:
#         print("=== Extracted Conclusion ===\n")
#         print(conclusion)  # Optional: limit preview to first 1000 chars

#         print("\n=== Classification ===\n")
#         category = classify_issue(conclusion)
#         print(f"Predicted issue category: {category}")
#     else:
#         print("No conclusion section found in the PDF.")



if __name__ == "__main__":
    main()
