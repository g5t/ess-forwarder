from typing import Tuple

import p4p
from caproto import Message as CA_Message


class no_op_Serialiser:
    def __init__(self, source_name: str):
        pass

    def serialise(self, update: p4p.Value) -> Tuple[None, None]:
        return None, None

    def ca_serialise(self, update: CA_Message, **unused) -> Tuple[None, None]:
        return None, None

    def ca_conn_serialise(self, pv: str, state: str) -> Tuple[None, None]:
        return None, None
