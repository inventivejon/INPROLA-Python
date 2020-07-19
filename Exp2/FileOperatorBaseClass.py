class FileOperatorBaseClass():
    def __init__(self):
        pass

    def read_from_text_file(self, filepath: str) -> list:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read().replace('\n', '')
        return []

    def write_to_text_file(self, filepath: str, requirement_list: list):
        with open(filepath, 'w', encoding='utf-8') as file:
            file.writelines(requirement_list)
        return []
    
    def append_to_text_file(self, filepath: str, requirement_list: list):
        with open(filepath, 'aw', encoding='utf-8') as file:
            file.writelines(requirement_list)
        return []

    def clear_text_file(sself, filepath):
        with open(filepath, 'w', encoding='utf-8') as file:
            pass