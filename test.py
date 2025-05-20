def fun(**kwargs):
    t = kwargs
    for k, val in kwargs.items():
        print("%s == %s" % (k, val))



fun(s1 = 1, s2 = 1)