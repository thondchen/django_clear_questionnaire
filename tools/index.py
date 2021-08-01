def getRandomNumberStr(bit):
    import random
    str = ''
    for i in range(bit):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        str += ch
    return str
