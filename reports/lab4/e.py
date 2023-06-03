import time
import ray


@ray.remote
def sum_remote(x):
    return sum(x)

# Actor class
@ray.remote
class increment(object):
    def __init__(self):
        self.r = 0.0

    def calculate(self, start, elements):
        # print begin calculate from start to start + elements
        print("Begin calculate from %d to %d" % (start, start + elements))
        timenow = time.time()
        for i in range(start + 1, start + elements):
            self.r += (1/i ** 2)
        print(time.time() - timenow)
        print("Finish calculate from %d to %d" % (start, start + elements))
        print("Time used: %f" % (time.time() - timenow))
        return self.r

    def get(self):
        return self.r

if __name__ == '__main__':
    # init
    ray.init()
    time1 = time.time()
    increments = []

    # create actors
    for i in range(8):
        # create actor
        actor = increment.remote()

        # Submit calls to the actor. These calls run asynchronously but in  
        # submission order on the remote actor process.
        incre = actor.calculate.remote(i * 125000000, 125000000)
        increments.append(incre)

    # Retrieve final actor state.
    results = ray.get(increments)

    # Submit a task to sum the results of the actors.
    result = sum_remote.remote(results)
    # Retrieve and print the result.
    print(ray.get(result))
    print("total time is: ",time.time()-time1)