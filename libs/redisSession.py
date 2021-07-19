import redis
import libs.session as Session

r = redis.Redis(host = "localhost", port = 6379, db = 0)

class redisSession(Session):
    @staticmethod
    def get_session_content(cookie_sid, key):
        '''用session_id和key获取redis里的session内容'''
        session_data = r.hget("_tornado_session_" + cookie_sid, key=key)
        if session_data:
            session_content = pickle.loads(session_data)
            return session_content if session_content is not None else {}
        return {}

    def __setitem__(self, key, value):
        '''这里用pickle序列化'''
        cookie_sid = self._get_cookie_sid()
        if not cookie_sid:
            cookie_sid = self._random_str()
        self.handler.set_secure_cookie("__session", cookie_sid)
        session_content = self.get_session_content(cookie_sid, key)
        session_content.__setitem__(key, value)
        r.hset("_tornado_session_" + cookie_sid, key, pickle.dumps(session_content))
        r.expire("_tornado_session_" + cookie_sid, 60 * 60 * 24)

    def __getitem__(self, key):
        cookie_sid = self._get_cookie_sid()
        if not cookie_sid:
            return None
        content = self.get_session_content(cookie_sid, key)
        return content.get(key, None) if content else None
    
    def __delitem__(self, key):
        cookie_sid = self._get_cookie_sid()
        if not cookie_sid:
            raise KeyError(key)
        session_content = self.get_session_content(cookie_sid, key)
        session_content.__delitem__(key)
        r.hset("_tornado_session_" + cookie_sid, key, pickle.dumps(session_content))