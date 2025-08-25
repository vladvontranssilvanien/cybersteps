import pickle

with open("saved_state.pkl", "rb") as f:
    print("B1 file opened for read:", f.name)
    # Deserialize bytes -> Python object (dict)
    loaded_state = pickle.load(f)
    # Sanity-check: show the whole dict
    print("B2 loaded_state:", loaded_state)
    # Access a specific field to prove it behaves like a dict
    print("B2 user:", loaded_state["user"])
