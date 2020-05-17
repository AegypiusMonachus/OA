'''
这是一个线程池，主要用在登录娱乐城异步转账时使用
'''
from concurrent.futures.thread import ThreadPoolExecutor
EntertainmentCityThreadPool = ThreadPoolExecutor(10)
