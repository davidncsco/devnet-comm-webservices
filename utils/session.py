class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class SessionManager(metaclass=SingletonMeta):
    """
    This is a Singleton class that manages session data
    """
    def __init__(self):
        self._session_data = {}

    def set(self, key, value):
        self._session_data[key] = value

    def get(self, key, default=None):
        return self._session_data.get(key, default)

    def remove(self, key):
        if key in self._session_data:
            del self._session_data[key]

    def clear(self):
        self._session_data.clear()

# # Usage
# session = SessionManager()

# # Set session variables
# session.set("env", "production")
# session.set("access_token", "abcdef123456")

# # Get session variables
# print(session.get("env"))  # Output: production
# print(session.get("access_token"))  # Output: abcdef123456

# # Remove a session variable
# session.remove("access_token")
# print(session.get("access_token"))  # Output: None

# # Clear all session variables
# session.clear()
# print(session.get("env"))  # Output: None
