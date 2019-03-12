import os
import numpy as np
import boto3
import librosa
import sox

from application import app


def is_conversion_required(filepath):
    sample_rate_16khz = int(sox.file_info.sample_rate(filepath)) == 16000
    mono = sox.file_info.channels(filepath) == 1
    wav = sox.file_info.file_type(filepath) == 'wav'
    convert = sample_rate_16khz and mono and wav
    return not convert


def convert_to_wav(input_path, output_path):
    app.logger.info(f'Entering convert_to_wav with input: {input_path} to {output_path}')
    if not os.path.isfile(input_path):
        app.logger.error(f'Path does not exist!')
    if is_conversion_required(input_path):
        tfm = sox.Transformer()
        tfm.rate(samplerate=16000)
        tfm.norm(db_level=-3)
        tfm.channels(1)
        tfm.build(input_filepath=input_path, output_filepath=output_path)
    else:
        os.rename(input_path, output_path)


def read_wave_local(path: str) -> (int, np.ndarray):
    signal, fs = librosa.load(path=path, sr=16000, mono=True)
    return fs, signal


def seconds_to_wav_bytes(time, fs, dtype, wav_header_size: int=44):
    bytes = int(time * fs * np.dtype(dtype).itemsize) + wav_header_size
    if bytes % 2:  # odd byte, effect caused by rounding float
        bytes -= 1
    return bytes


def get_range_bytes(start, end, dtype, fs):
    start_bytes = seconds_to_wav_bytes(start, fs, dtype)
    end_bytes = seconds_to_wav_bytes(end, fs, dtype)
    if (end_bytes - start_bytes) % 2 == 0:
        end_bytes -= 1
    # Range set according to https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.35
    range_bytes = f'bytes={start_bytes}-{end_bytes}'
    return range_bytes


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
    range_bytes = get_range_bytes(start, end, dtype, fs)
    o = client.get_object(Bucket=bucket, Key=path, Range=range_bytes)
    result = o['Body'].read()
    wav = np.frombuffer(result, dtype=dtype)
    return wav

