text = """
{"code": "invalid_param", "message": "Run failed: Traceback (most recent call last):\n  File \"/var/sandbox/sandbox-python/tmp/d5911400_3441_4917_8ec8_285279801273.py\", line 48, in <module>\n  File \"<string>\", line 52, in <module>\n  File \"<string>\", line 35, in main\nValueError: JSON\u6570\u636e\u4e2d\u7f3a\u5c11'data'\u5b57\u6bb5\nerror: exit status 255\n", "status": 400}
"""

if "ValueError: JSON\u6570\u636e\u4e2d\u7f3a\u5c11'data'\u5b57\u6bb5" in text:
    print("hello")
else:
    print("world")
