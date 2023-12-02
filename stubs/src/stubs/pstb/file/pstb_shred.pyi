from _typeshed import Incomplete as Incomplete

def overwrite_with_pattern(file, pattern, block_size) -> None: ...
def verify_pass(file_path, expected_pattern, block_size) -> None: ...
def dod522022m_shred(file_path, block_size: Incomplete | None = ..., true_random: bool = ..., standard: str = ..., adaptive: bool = ...) -> None: ...

file_to_shred: str
true_random: bool
standard: str
adaptive: bool
