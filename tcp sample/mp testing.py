from multiprocessing import Process, Queue

def a(b):
    a = 0
    while True:
        a += b
        print(a)
        
def b(c):
    b = 0
    while True:
        b += c
        print(b)


if __name__ == "__main__":
    p1 = Process(target=a, args=(1,))
    p2 = Process(target=b, args=(2,))

    p1.start()
    p2.start() 
    p1.join()
    p2.join()