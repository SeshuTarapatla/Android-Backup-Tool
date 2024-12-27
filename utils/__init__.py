# Encodings
UTF_8 = "utf-8"
UTF_8_SIG = "utf-8-sig"


# Utilities
def load_set(file: str) -> set[str]:
    """Helper function to load required sets

    Args:
        file (str): File to be read

    Returns:
        set: Set of lines in the file
    """
    with open(file, "r", encoding=UTF_8) as fr:
        data = fr.read().splitlines()
    return set(data)
