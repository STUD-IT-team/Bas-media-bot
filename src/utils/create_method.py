def withCreate(cls):
    """Class decorator that adds a Create method to instantiate the class."""
    @classmethod
    def Create(cls, *args, **kwargs):
        """Creates an instance of the class by calling __init__ and returns it."""
        instance = cls(*args, **kwargs)
        return instance
    
    cls.Create = Create
    return cls