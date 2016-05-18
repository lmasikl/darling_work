import asyncio

@asyncio.coroutine
def factorial(data):
    f = 1
    for i in range(2, data['n'][1] + 1):
        print("Task %s: Compute factorial(%s)..." % (data['n'][0], i))
        f *= i
        yield from asyncio.sleep(1)

    data['f'] = f
    print("Task %s: factorial(%s) = %s" % (data['n'][0], data['n'][1], f))
    print()



@asyncio.coroutine
def async(tasks):
    results = asyncio.gather(*[factorial(task) for task in tasks])
    return results

tasks = [
    {'n': ("A", 2), 'f': 0},
    {'n': ("B", 3), 'f': 0},
    {'n': ("C", 4), 'f': 0},
]

loop = asyncio.get_event_loop()
loop.run_until_complete(async(tasks))
loop.close()

print(tasks)
