import numpy as np
import boto3
from scipy.io import wavfile


def read_wave_local(path: str, normalise=True) -> (int, np.ndarray):
    fs, signal = wavfile.read(path)
    if normalise:
        signal = signal / signal.max()
    return fs, signal.astype('float32')


def wav_float_to_int(signal: np.ndarray) -> np.ndarray:
    max_abs_val = np.absolute(signal).max()
    signal = ((signal / (max_abs_val / (2 ** 15 - 1))).astype('int16'))
    return signal


def write_wave(path: str, signal: np.ndarray, pcm16: bool=True, rate: int = 16000) -> None:
    if pcm16:
        signal = wav_float_to_int(signal)
    wavfile.write(path, rate, signal)


def read_wave_part_from_s3(bucket: str, path: str, fs: int, start: int, end: int, dtype: np.dtype = np.int16) -> np.ndarray:
    """
    Read part of a wavefile from S3
    :param bucket: bucket name
    :param path: path in the bucket
    :param fs: frequency [Hz]
    :param start: start of audio of interest [s]
    :param end: end of audio of interest [s]
    :param dsize: data type size (e.g. int16 = 2 bytes)
    :return: wavefile of interest
    """
    client = boto3.client('s3')
    start_bytes = int(start * fs * np.dtype(dtype).itemsize)
    end_bytes = int(end * fs * np.dtype(dtype).itemsize)
    if (end_bytes - start_bytes) % 2 == 0:
        end_bytes += 1
    # Range set according to https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.35
    range_bytes = f'bytes={start_bytes}-{end_bytes}'
    # o = client.get_object(Bucket=bucket, Key=path)
    o = client.get_object(Bucket=bucket, Key=path, Range=range_bytes)
    result = o['Body'].read()
    wav = np.frombuffer(result, dtype=dtype)
    return wav