import pandas as pd

DATA_PATH = "data/connect4.csv"
LETTERS = ["a", "b", "c", "d", "e", "f", "g"]
NUMBERS = [1, 2, 3, 4, 5, 6]
MIRROR_LETTER = {"a": "g", "b": "f", "c": "e", "d": "d", "e": "c", "f": "b", "g": "a"}


def square_columns():
    """Return the 42 square column names in dataset order a1..g6."""
    return [letter + str(number) for letter in LETTERS for number in NUMBERS]


def check_disc_counts(df):
    """Print how many rows have exactly 4 x and 4 o."""
    squares = df[square_columns()]
    x_counts = (squares == "x").sum(axis=1)
    o_counts = (squares == "o").sum(axis=1)
    good = ((x_counts == 4) & (o_counts == 4)).sum()
    print(f"a) Rows with exactly 4 x and 4 o: {good} of {len(df)}")


def column_is_stacked(values):
    """Return True if no blank appears below a disc, with values listed bottom to top."""
    seen_blank = False
    for value in values:
        if value == "b":
            seen_blank = True
        elif seen_blank:
            return False
    return True


def count_floating_rows(df, bottom_number):
    """Count rows with a disc floating above a blank, assuming bottom_number is the bottom."""
    if bottom_number == 1:
        order = NUMBERS
    else:
        order = list(reversed(NUMBERS))
    bad_rows = 0
    for _, row in df.iterrows():
        for letter in LETTERS:
            values = [row[letter + str(number)] for number in order]
            if not column_is_stacked(values):
                bad_rows += 1
                break
    return bad_rows


def check_square_numbering(df):
    """Print whether number 1 or number 6 is the bottom of each column."""
    bad_if_one_is_bottom = count_floating_rows(df, 1)
    bad_if_six_is_bottom = count_floating_rows(df, 6)
    print(f"b) Rows with floating discs if 1 is the bottom: {bad_if_one_is_bottom}")
    print(f"   Rows with floating discs if 6 is the bottom: {bad_if_six_is_bottom}")
    if bad_if_one_is_bottom == 0:
        print("   Conclusion: number 1 is the BOTTOM of each column.")
    elif bad_if_six_is_bottom == 0:
        print("   Conclusion: number 6 is the BOTTOM of each column.")
    else:
        print("   Conclusion: neither numbering is consistent.")


def check_classes(df):
    """Print class counts and the majority-class share (baseline accuracy)."""
    counts = df["class"].value_counts()
    print("c) Class counts:")
    for name, count in counts.items():
        print(f"   {name:5} {count:6}  ({count / len(df):.1%})")
    print(f"   Majority class: {counts.idxmax()}, baseline accuracy {counts.max() / len(df):.4f}")


def check_duplicates(df):
    """Print the number of duplicate rows."""
    print(f"d) Duplicate rows (including class): {df.duplicated().sum()}")
    print(f"   Duplicate positions (squares only): {df.duplicated(subset=square_columns()).sum()}")


def mirror_square(name):
    """Return the left-right mirrored square name, for example a1 -> g1."""
    return MIRROR_LETTER[name[0]] + name[1]


def check_mirrors(df):
    """Print how many positions have their mirror image also in the dataset."""
    columns = square_columns()
    mirrored_columns = [mirror_square(name) for name in columns]
    positions = set(df[columns].astype(str).agg("".join, axis=1))
    mirrored = df[mirrored_columns].astype(str).agg("".join, axis=1)
    has_mirror = mirrored.isin(positions)
    symmetric = mirrored == df[columns].astype(str).agg("".join, axis=1)
    print(f"e) Positions whose mirror image is also in the dataset: {has_mirror.sum()}")
    print(f"   Of these, positions that are their own mirror (symmetric): {symmetric.sum()}")
    print(f"   Positions with a different mirror image in the dataset: {(has_mirror & ~symmetric).sum()}")


def main():
    """Load the dataset and run all checks."""
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns from {DATA_PATH}")
    print()
    check_disc_counts(df)
    check_square_numbering(df)
    check_classes(df)
    check_duplicates(df)
    check_mirrors(df)


if __name__ == "__main__":
    main()
