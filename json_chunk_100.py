import json

chunk_size = 100

with open("./json/ALL_human.json") as f:
    data = json.load(f)

for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    with open(f"./json/ALL_human_chunk_{i//chunk_size + 1}.json", "w") as f_out:
        json.dump(chunk, f_out, indent=2)

print(f"Created {len(data)//chunk_size + 1} JSON chunks")

