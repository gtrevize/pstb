from _typeshed import Incomplete
from pstb.file.pstb_speed import find_best_block_size as find_best_block_size

def overwrite_with_pattern(file, pattern, block_size) -> None: ...
def verify_pass(file_path, expected_pattern, block_size): ...
def dod522022m_shred(file_path, block_size: Incomplete | None = ..., true_random: bool = ..., standard: str = ..., adaptive: bool = ...) -> None: ...

file_to_shred: str
true_random: bool
standard: str
adaptive: bool
