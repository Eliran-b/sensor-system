import hashlib
import json


class CachedInstance(type):
    """
    The CachedInstance class is similar to Singleton Design Pattern.
    The difference is that pattern allows the creation of multiple instances of the same class,
    and assures that every instance is unique by the values the caller sends the constructor.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        index = cls.get_hashable_index(args, kwargs)
        if index not in cls._instances:
            cls._instances[index] = super(CachedInstance, cls).__call__(*args, **kwargs)
        return cls._instances[index]

    def get_hashable_index(cls, args: tuple, kwargs: dict) -> str:
        image_dict = {"kwargs": repr(kwargs),
                      "args": repr(args),
                      "cls": repr(cls)}
        encoded_image_dict = json.dumps(image_dict, sort_keys=True).encode()

        dhash = hashlib.md5()
        dhash.update(encoded_image_dict)
        return dhash.hexdigest()
