import subprocess

def classify_issue(conclusion_text: str, model: str = "mistral") -> str:
    """
    Sends the conclusion text to a local LLM (Ollama) for classification.

    Returns the predicted category as a string.
    """


    prompt = f"""
    You are a damp and mould inspection expert. Read the conclusion below and classify the primary cause into ONE of the following categories:

    - Condensation-related mould
    - Structural damp
    - Ventilation deficiency
    - Insulation/thermal bridging
    - Surface mould (non-structural)
    - Mixed causes
    - No issue detected

    Return ONLY the category. No explanations or extra output.

    Conclusion:
    {conclusion_text}
    """.strip()

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True,
    )
    output = result.stdout.decode().strip()
    return output
