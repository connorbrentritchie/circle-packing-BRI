with open('D:\Work\Testing.txt','w') as results:
    for _ in range(3):
        print('hello world {}'.format(_), file=results)
