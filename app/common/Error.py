# An error indicating that a desired attribute was not found within a given dictionary.
class AttributeNotFoundError(Exception):
    def __init__(self):
        super().__init__("A required attribute was not found in the dictionary")

    def __init__(self, attribute):
        super().__init__(f"Attribute {attribute} not found in dictionary")
