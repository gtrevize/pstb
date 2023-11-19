import os
import time


def measure_read_speed(file_path, block_size):
    """
    Measures the read speed of a file.

    Args:
        file_path (str): The path to the file to measure.
        block_size (int): The block size for reading.

    Returns:
        float: The read speed in MB/s.
    """

    start_time = time.perf_counter()
    with open(file_path, "rb") as file:
        while True:
            data = file.read(block_size)
            if not data:
                break
    elapsed_time = time.perf_counter() - start_time
    speed = os.path.getsize(file_path) / (1024 * 1024 * elapsed_time)  # MB/s

    return speed


def find_best_block_size(file_path):
    """
    Finds the best block size for reading a file to optimize speed.

    Args:
        file_path (str): The path to the file to analyze.

    Returns:
        int: The best block size for reading the file.
    """
    block_sizes = [
        512,
        1024,
        2048,
        4096,
        8192,
        16384,
        32768,
        65536,
    ]  # Reasonable block sizes
    best_block_size = 4096  # Default block size
    best_speed = 0

    for block_size in block_sizes:
        speed = measure_read_speed(file_path, block_size)
        if speed > best_speed:
            best_block_size = block_size
            best_speed = speed

    return best_block_size
