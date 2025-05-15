import os

def save_project_structure(root_dir, output_file="project_structure.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Уровень вложенности
            level = dirpath.replace(root_dir, "").count(os.sep)
            indent = "    " * level
            # Папка
            f.write(f"{indent}[{os.path.basename(dirpath)}/]\n")
            sub_indent = "    " * (level + 1)
            for file in filenames:
                f.write(f"{sub_indent}{file}\n")

if __name__ == "__main__":
    # Задай путь к корню проекта (если запускаешь из корня — оставь ".")
    project_root = "."
    save_project_structure(project_root)
    print("Структура проекта сохранена в 'project_structure.txt'")
