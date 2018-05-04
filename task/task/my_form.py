#!/usr/bin/python


USER = [
    {"field": "name", "name": "姓名", "null": False, "min_len": 1, "unique": True},
    {"field":"username","name":"系统账号名", "null":False,"min_len":3,"unique":True},
    {"field":"passwd","name":"密码", "null":False,"min_len":8,"unique":False}

]