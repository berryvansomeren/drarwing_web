


def size_bytes_to_mib(n_bytes: int) -> float:
    return n_bytes / (1024 * 1024)


def get_size_mib(data: str|bytes) -> float:
    return size_bytes_to_mib(len(data))