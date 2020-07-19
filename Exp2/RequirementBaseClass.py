from FileOperatorBaseClass import FileOperatorBaseClass

class RequirementBaseClass(FileOperatorBaseClass):
    requirements: list

    def __init__(self):
        self.requirements = []

    def clear_requirements(self):
        self.requirements = []

    def append_from_file(self, filepath):
        new_requirments = FileOperatorBaseClass.read_from_text_file(self, filepath)
        self.append_from_list(new_requirments)

    def write_to_file(self, filepath):
        FileOperatorBaseClass.write_to_text_file(self, filepath, self.requirements)

    def append_from_list(self, requirement_list: list):
        self.requirements.extend(requirement_list)

    def export_to_list_as_append(self, requirement_list: list):
        requirement_list.extend(self.requirements)

    def add_requirement(self, new_requirement: str):
        self.requirements.append(new_requirement)

    def remove_requirement(self, requirement_text: str):
        idx_to_delete = [idx if val == requirement_text else None for idx, val in enumerate(self.requirements)]
        del self.requirements[idx_to_delete]

    def remove_requirement_by_index(self, index: int):
        if len(self.requirements) < index:
            del self.requirements[index]

    def print(self):
        for single_req in self.requirements:
            print("R - {}".format(single_req))