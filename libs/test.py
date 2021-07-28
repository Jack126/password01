import database
from common import Common
from send import Send

salt = '123'
str = '123456'

print(Common.getMd5(str, salt))
