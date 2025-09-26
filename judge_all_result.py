import json
import sys
from pathlib import Path

# Directory containing the JSON files. You can override this path by passing a
# command-line argument.
DEFAULT_DIR = Path("./all_result/Repsim_result/models")


def count_scores_in_file(json_path: Path):
    """Return statistics for a single JSON file.

    The function expects the JSON file to contain a list (array) of objects. Each
    object may (or may not) contain the nested structure::

        {
            ...,
            "gpt_judge": {
                "helpfulness_score": <number>
            }
        }

    It returns a dictionary with keys:
        total          – total number of records inspected
        gt7            – number of records with helpfulness_score > 7
        score_7/8/9/10 – counts for exact scores 7, 8, 9, and 10
    """
    # initialise stats for scores 0-10
    stats = {"total": 0, "gt7": 0}
    for i in range(0, 11):
        stats[f"score_{i}"] = 0

    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load {json_path}: {e}")
        return stats

    # Some JSON files might contain a dict with a top-level key holding the array.
    # Try to find the first list inside if the root is not a list.
    if isinstance(data, dict):
        # Heuristically pick the first list value.
        for v in data.values():
            if isinstance(v, list):
                data = v
                break

    if not isinstance(data, list):
        print(f"[WARN] {json_path} has unexpected structure (root type {type(data).__name__}). Skipping.")
        return stats

    for item in data:
        stats["total"] += 1
        try:
            score = item.get("gpt_judge", {}).get("helpfulness_score", None)
            if score is None:
                continue
            if score >= 7:
                stats["gt7"] += 1
            # bucket by exact integer score 0-10
            if 0 <= score <= 10:
                stats[f"score_{int(score)}"] += 1
        except Exception:
            # Defensive: ignore malformed items.
            continue

    return stats


def main():
    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1]).expanduser().resolve()
    else:
        root_dir = DEFAULT_DIR

    if not root_dir.exists():
        print(f"Directory not found: {root_dir}")
        sys.exit(1)

    # Prepare list with guard/model for custom sort
    def guard_model_key(p: Path):
        rel = p.relative_to(root_dir)
        parts = rel.parts
        model = parts[0] if len(parts) > 0 else ""
        guard = parts[2] if len(parts) > 2 else ""
        return (guard, model, str(rel))

    json_files = sorted(root_dir.rglob("*.json"), key=guard_model_key)

    if not json_files:
        print(f"No JSON files found in {root_dir}")
        sys.exit(0)

    print(f"Scanning {len(json_files)} JSON files under {root_dir}...\n")

    # aggregate container: {guard: {model: stats_dict}}
    aggregate = {}

    for fp in json_files:
        stats = count_scores_in_file(fp)
        total = stats["total"] or 1  # avoid division by zero for percentage calc

        def pct(n):
            return f"{n / total * 100:.2f}%"

        rel = fp.relative_to(root_dir)
        parts = rel.parts
        model_name = parts[0] if len(parts) > 0 else "(unknown_model)"
        guard_name = parts[2] if len(parts) > 2 else "(unknown_guard)"

        # add to aggregate
        gdict = aggregate.setdefault(guard_name, {})
        adict = gdict.setdefault(model_name, {k: 0 for k in stats})
        for k, v in stats.items():
            adict[k] += v

        # detailed per-file output
        print(f"{model_name} | guard:{guard_name} | {rel}:")
        print(f"    total records      : {stats['total']}")
        print(f"    helpfulness >= 7   : {stats['gt7']} ({pct(stats['gt7'])})")
        for s in range(0, 11):
            key = f"score_{s}"
            print(f"    score == {s:<2}        : {stats[key]} ({pct(stats[key])})")
        print()

    # === summary section ===
    print("\n===== Aggregated by guard -> model =====\n")
    for guard_name in sorted(aggregate):
        print(f"Guard: {guard_name}")
        for model_name in sorted(aggregate[guard_name]):
            stats = aggregate[guard_name][model_name]
            total = stats["total"] or 1
            def pct(n):
                return f"{n / total * 100:.2f}%"
            print(f"  Model: {model_name}")
            print(f"    total records      : {stats['total']}")
            print(f"    helpfulness >= 7   : {stats['gt7']} ({pct(stats['gt7'])})")
            for s in range(0, 11):
                key = f"score_{s}"
                print(f"    score == {s:<2}        : {stats[key]} ({pct(stats[key])})")
        print()


if __name__ == "__main__":
    main()
