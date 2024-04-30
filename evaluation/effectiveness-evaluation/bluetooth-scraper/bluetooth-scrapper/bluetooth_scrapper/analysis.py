import json
import os

layers = []
for file in os.listdir("../../data/device_details"):
    if file.endswith(".json"):
        # print(file)
        with open(f"../../data/device_details/{file}") as f:
            data = json.load(f)
            if data is None:
                print(file)
                continue
            if "QualifiedDesign" in data:
                if data["QualifiedDesign"] is not None:
                    if "Layers" in data["QualifiedDesign"]:
                        layers.extend(data["QualifiedDesign"]["Layers"])
                        continue
                        print(["QualifiedDesign"]["Layers"])
            if "ReferencedQualifiedDesigns" in data:
                if data["ReferencedQualifiedDesigns"] is not None:
                    trigger = False
                    for reference in data["ReferencedQualifiedDesigns"]:

                        if "Layers" in reference.keys():
                            # print(reference["Layers"])
                            layers.extend(reference["Layers"])
                            trigger = True
                            # print(["ReferencedQualifiedDesigns"]["Layers"])
                    if trigger:
                        continue
            print(file)
            print("error no layer found")
            # ["ReferencedQualifiedDesigns"]["Layers"]


from collections import Counter

# print(layers[0])
# Use a list comprehension to extract FullName values and count them with Counter
fullname_counts = Counter([layer["FullName"] for layer in layers])

print(fullname_counts)
