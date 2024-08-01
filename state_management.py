class StateManager:
    def __init__(self):
        self.last_input = ""

    def is_new_input(self, current_input: str) -> bool:
        """
        Check if the current input is different from the last processed input.

        :param current_input: The new input text.
        :return: True if the input is new, False otherwise.
        """
        return current_input != self.last_input

    def update_last_input(self, current_input: str):
        """
        Update the last processed input with the current input.

        :param current_input: The new input text.
        """
        self.last_input = current_input