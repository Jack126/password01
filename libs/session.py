class session:
    def __init__(self, handler):
        self.handler = handler

    @staticmethod
    def _random_str():
        '''用随机数来作为session_id'''
        return str(uuid.uuid4())

    def _get_cookie_sid(self):
        '''获取cookie中的session_id'''
        cookie_sid = self.handler.get_secure_cookie("__session", None)
        return str(cookie_sid, encoding="utf-8") if cookie_sid else None

    def __setitem__(self, key, value):
        cookie_sid = self._get_cookie_sid()
        if not cookie_sid:
            cookie_sid = self._random_str()
        self.handler.set_secure_cookie("__session", cookie_sid)
        SESSION.setdefault(cookie_sid, {}).__setitem__(key, value)

    def __getitem__(self, key):
        cookie_sid = self._get_cookie_sid()
        content = SESSION.get(cookie_sid, None)
        return content.get(key, None) if content else None

    def __delitem__(self, key):
        cookie_sid = self._get_cookie_sid()
        if not cookie_sid or not SESSION.get(cookie_sid):
            raise KeyError(key)
        del SESSION[cookie_sid][key]