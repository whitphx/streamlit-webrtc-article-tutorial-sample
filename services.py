"""Media streamings"""
import logging
from pathlib import Path

import av
import pydub
import numpy as np


HERE = Path(__file__).parent
ROOT = HERE.parent

logger = logging.getLogger(__name__)


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    
    # ここに音声を受け取って最終的にファイルにする構造が必要そう？
    return av.VideoFrame.from_ndarray(img, format="bgr24")



def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    raw_samples = frame.to_ndarray()
    sound = pydub.AudioSegment(
        data=raw_samples.tobytes(),
        sample_width=frame.format.bytes,
        frame_rate=frame.sample_rate,
        channels=len(frame.layout.channels),
    )

    # Ref: https://github.com/jiaaro/pydub/blob/master/API.markdown#audiosegmentget_array_of_samples  # noqa
    channel_sounds = sound.split_to_mono()
    channel_samples = [s.get_array_of_samples() for s in channel_sounds]
    new_samples: np.ndarray = np.array(channel_samples).T
    new_samples = new_samples.reshape(raw_samples.shape)

    new_frame = av.AudioFrame.from_ndarray(new_samples, layout=frame.layout.name)
    new_frame.sample_rate = frame.sample_rate
    return new_frame