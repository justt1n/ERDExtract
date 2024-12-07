import re
import typing


class ERDRelation:
    def __init__(
        self,
        entity1: str,
        entity2: str,
        attributes1: typing.List[str],
        attributes2: typing.List[str],
        relationship_type: str,
        primary_keys1: typing.List[str] = None,
        primary_keys2: typing.List[str] = None,
    ):
        self.entity1 = entity1
        self.entity2 = entity2
        self.attributes1 = attributes1
        self.attributes2 = attributes2
        self.relationship_type = relationship_type
        self.primary_keys1 = primary_keys1 or []
        self.primary_keys2 = primary_keys2 or []


class ERDExtractor:
    @staticmethod
    def parse_erd_input(input_str: str) -> ERDRelation:
        pattern = r"\[(.*?)\]\s*\((.*?)\)(?:\s*\((.*?)\))?\s*-\s*\[(.*?)\]\s*\((.*?)\)(?:\s*\((.*?)\))?: (.+)"

        match = re.match(pattern, input_str, re.UNICODE)
        if not match:
            raise ValueError(f"Invalid input format: {input_str}")

        entity1, attrs1, pk1, entity2, attrs2, pk2, rel_type = match.groups()

        attributes1 = [attr.strip() for attr in attrs1.split(",")]
        attributes2 = [attr.strip() for attr in attrs2.split(",")]

        primary_keys1 = [
            pk.split(":")[0].strip() for pk in (pk1 or "").split(",") if pk.strip()
        ]
        primary_keys2 = [
            pk.split(":")[0].strip() for pk in (pk2 or "").split(",") if pk.strip()
        ]

        rel_type_mapping = {"cha - con": "cha - con", "n - 1": "n - 1"}
        normalized_rel_type = rel_type_mapping.get(rel_type.strip(), rel_type.strip())

        return ERDRelation(
            entity1,
            entity2,
            attributes1,
            attributes2,
            normalized_rel_type,
            primary_keys1,
            primary_keys2,
        )

    @staticmethod
    def transform_erd_model(input_str: str) -> str:
        erd_relation = ERDExtractor.parse_erd_input(input_str)

        if erd_relation.relationship_type == "n - 1":
            foreign_key = erd_relation.attributes2[0]

            new_attrs1 = erd_relation.attributes1 + [foreign_key]

            new_attrs2 = [foreign_key]
            for attr in erd_relation.attributes2:
                if attr != foreign_key and attr not in new_attrs2:
                    new_attrs2.append(attr)

            return (
                f"[{erd_relation.entity1}]"
                f" ({', '.join(new_attrs1)})"
                f" ({foreign_key}:FK)"
                f" - [{erd_relation.entity2}]"
                f" ({', '.join(new_attrs2)})"
                f": {erd_relation.relationship_type}"
            )

        elif erd_relation.relationship_type in ["1 - 1", "cha - con"]:
            set_type = "1 - 1"
            parent_id = erd_relation.attributes1[0]
            return (
                f"[{erd_relation.entity1}]"
                f" ({', '.join(erd_relation.attributes1)})"
                f" - [{erd_relation.entity2}]"
                f" ({parent_id}, {', '.join(erd_relation.attributes2)})"
                f": {set_type}"
            )

            return input_str

        return input_str


def main():
    try:
        with open("input.txt", "r", encoding="utf-8") as input_file:
            input_lines = input_file.readlines()

        output_lines = []
        for line in input_lines:
            line = line.strip()
            if line:
                try:
                    result = ERDExtractor.transform_erd_model(line)
                    output_lines.append(result)
                except ValueError as e:
                    output_lines.append(f"Error: {str(e)}")

        with open("output.txt", "w", encoding="utf-8") as output_file:
            for line in output_lines:
                output_file.write(line + "\n")

        print("Transformation completed. Results:")
        for line in output_lines:
            print(line)

    except FileNotFoundError:
        print("Error: input.txt file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
