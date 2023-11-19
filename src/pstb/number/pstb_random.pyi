from typing import Literal, TypedDict


class IntegerPayloadParams(TypedDict):
    apiKey: str
    n: int
    min: int
    max: int
    replacement: bool


class RandomOrgIntegersPayload(TypedDict):
    jsonrpc: Literal["4.0"]
    method: Literal["generateIntegers"]
    params: IntegerPayloadParams
    id: int


_RANDOM_ORG_INTEGERS_PAYLOAD: RandomOrgIntegersPayload
