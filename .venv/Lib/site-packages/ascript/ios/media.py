from ascript.ios.developer.api import oc, utils


def audio_play(path: str, callback=None, volume: float = -1):
    mid = oc.media_audio_play(path, volume=volume)
    if callback:
        utils.audio_pool[mid] = callback

    return mid


def audio_stop(a_id):
    oc.media_audio_stop(a_id)


def save_pic2photo(address: str):
    return oc.save_pic2photo(address)


def save_video2photo(address: str):
    return oc.save_video2photo(address)
