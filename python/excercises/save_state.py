import pickle

# In-memory application state (any Python object is fine)
app_state = {"user": "rick", "level": 5, "inventory": [
    "grandson", "time-machine"]}

print("A1 app_state:", app_state)

# Write as binary: pickle works with bytes, not text
with open("saved_state.pkl", "wb") as f:
    print("A2 file opened for write:", f.name)
    # Serialize Python object -> bytes and write to file
    pickle.dump(app_state, f)
    print("A3 state saved.")
