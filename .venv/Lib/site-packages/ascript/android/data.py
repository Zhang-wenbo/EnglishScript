from airscript.data import Kv


class KeyValue:
    @staticmethod
    def save(key: str, value):
        Kv.save(key, value)

    @staticmethod
    def get(key: str, default_value):
        return Kv.get(key, default_value)

    @staticmethod
    def remove(key: str):
        return Kv.remove(key)
