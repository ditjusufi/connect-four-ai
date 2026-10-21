import os

import matplotlib.pyplot as plt
import pandas as pd
from ucimlrepo import fetch_ucirepo

os.makedirs("data", exist_ok=True)

dataset = fetch_ucirepo(id=26)
X = dataset.data.features
y = dataset.data.targets
df = pd.concat([X, y], axis=1)
df.to_csv("data/connect4.csv", index=False)

print("Shape:", df.shape)
print()
print(df.head())
print()
print("Missing values:", int(df.isna().sum().sum()))
print()

target_col = y.columns[0]
counts = df[target_col].value_counts()
print(counts)
print()
print((counts / len(df)).round(3))
print()
print(X.stack().value_counts())

counts.plot(kind="bar")
plt.title("Outcome for the first player")
plt.ylabel("Positions")
plt.tight_layout()
plt.savefig("data/class_distribution.png")
print("Saved data/connect4.csv and data/class_distribution.png")