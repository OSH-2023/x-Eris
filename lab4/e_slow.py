import time
import ray
import random


@ray.remote
def sum_remote(x):
    return sum(x)

# Actor class
@ray.remote
class monto(object):
    def __init__(self):
        self.c = 0
        self.n = 0
        # e = c/n
        self.e = 0.0

    def simulate(self, times):
        print("Begin to simulate for ", times, " times")
        self.n += times
        for i in range(times):
            x = random.uniform(1, 2)
            y = random.uniform(0, 1)
            if y < 1/x:
                self.c += 1
        self.e = pow(2, self.n / self.c)
        print(self.e)
        return self.c

    def get(self):
        return self.e

if __name__ == '__main__':
    # init
    context = ray.init()
    print(context.dashboard_url)
    time1 = time.time()
    increments = []
    n = 0
    c = 0
    e = 0.0


    # create actors
    for i in range(1):
        # create actor
        actor = monto.remote()

        # Submit calls to the actor. These calls run asynchronously but in  
        # submission order on the remote actor process.
        incre = actor.simulate.remote(10000000)
        n = 10000000
        increments.append(incre)

    # Retrieve final actor state.
    results = ray.get(increments)

    c = sum(results)

    # calculate e
    e = pow(2, n / c)
    # Retrieve and print the result.
    print(e)
    print("total time is: ",time.time()-time1)