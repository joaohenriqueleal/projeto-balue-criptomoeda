import os


def format_size(bytes_size: int) -> str:
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / (1024 ** 2):.2f} MB"
    elif bytes_size < 1024 ** 4:
        return f"{bytes_size / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_size / (1024 ** 4):.2f} TB"

def disk_size_detailed(path_dir: str, indent: int = 0) -> int:
    total_bytes = 0
    for entry in os.scandir(path_dir):
        if entry.is_file():
            size = os.path.getsize(entry.path)
            total_bytes += size
            print("  " * indent + f"{entry.name} - {format_size(size)}")
        elif entry.is_dir():
            print("  " * indent + f"[{entry.name}]")
            size = disk_size_detailed(entry.path, indent + 1)
            total_bytes += size
            print("  " * (indent + 1) + f"Total {entry.name}: {format_size(size)}")
    return total_bytes


directory = "../balue"
total = disk_size_detailed(directory)
print(f"\ntotal size of '{directory}': {format_size(total)}")
