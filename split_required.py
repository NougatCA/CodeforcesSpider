import os.path


def main():

    required_root = "./required/"
    lang = "Python"

    lines_per_file = 10000
    with open(os.path.join(required_root, f"{lang}_required.jsonl"), mode="r", encoding="utf-8") as f:
        lines = f.readlines()
    num_files = len(lines) // lines_per_file
    if len(lines) % lines_per_file != 0:
        num_files += 1

    for i in range(num_files):
        start = i * lines_per_file
        end = start + lines_per_file
        output_path = os.path.join(required_root, f"{lang}_required_split_{i}.jsonl")

        with open(output_path, mode="w", encoding="utf-8") as write_f:
            write_f.writelines(lines[start: end])


if __name__ == "__main__":
    main()
