import flatbuffers
from f142_logdata import LogData
from f142_logdata.Value import Value
from f142_logdata.Int import IntStart, IntAddValue, IntEnd
from f142_logdata.Double import DoubleStart, DoubleAddValue, DoubleEnd
from caproto import ChannelType
import numpy as np
from applicationlogger import get_logger

_logger = get_logger()


def _millseconds_to_nanoseconds(time_ms):
    return int(time_ms * 1000000)


def _complete_buffer(builder, file_identifier: bytes, timestamp_unix_ms: int) -> bytes:
    # LogData.LogDataAddTimestamp(builder, _millseconds_to_nanoseconds(timestamp_unix_ms))
    log_msg = LogData.LogDataEnd(builder)
    builder.Finish(log_msg)
    # Generate the output and replace the file_identifier
    buff = builder.Output()
    buff[4:8] = file_identifier
    return bytes(buff)


def _setup_builder():
    file_identifier = b"f142"
    builder = flatbuffers.Builder(1024)
    source = builder.CreateString("Forwarder-Python")
    return builder, file_identifier, source


def serialise_f142(
    data: np.ndarray, data_size: int, data_type: ChannelType, timestamp_unix_ms: int = 0
) -> bytes:
    builder, file_identifier, source = _setup_builder()

    if data_size != 1:
        _logger.error(
            "Forwarder does not yet know how to serialise EPICS arrays as an f142 message"
        )

    if data_type == ChannelType.INT:
        _serialise_int(builder, data, source)
    elif data_type == ChannelType.DOUBLE:
        _serialise_double(builder, data, source)
    else:
        _logger.error(
            f"Forwarder does not know how to serialise EPICS type {data_type} as an f142 message"
        )

    return _complete_buffer(builder, file_identifier, timestamp_unix_ms)


def _serialise_int(builder, data, source):
    IntStart(builder)
    IntAddValue(builder, data.astype(np.int32)[0])
    value_position = IntEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Int)


def _serialise_double(builder, data, source):
    DoubleStart(builder)
    DoubleAddValue(builder, data.astype(np.float64)[0])
    value_position = DoubleEnd(builder)
    LogData.LogDataStart(builder)
    LogData.LogDataAddSourceName(builder, source)
    LogData.LogDataAddValue(builder, value_position)
    LogData.LogDataAddValueType(builder, Value.Double)