import os


def generate_context(directory):
    context = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file == "context.py":
                continue
            if "tests" in root:
                continue
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    file_content = f.read()
                    relative_path = os.path.relpath(file_path, directory)
                    context.append(f"### {relative_path} ###\n")
                    context.append(file_content)
                    context.append("\n\n")

    return "".join(context)


if __name__ == "__main__":
    context = generate_context(".")

    with open("project_context.txt", "w") as output_file:
        output_file.write(context)
