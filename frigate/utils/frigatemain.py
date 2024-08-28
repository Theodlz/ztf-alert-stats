from frigate.utils.datasets import save_dataframe
from frigate.utils.kowalski import get_candidates_from_kowalski
from frigate.utils.skyportal import get_candids_per_filter_from_skyportal


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {"false", "f", "0", "no", "n"}:
        return False
    elif value.lower() in {"true", "t", "1", "yes", "y"}:
        return True
    raise ValueError(f"{value} is not a valid boolean value")


def process_candidates(args):
    # GET CANDIDATES FROM KOWALSKI
    candidates, err = get_candidates_from_kowalski(
        args.start,
        args.end,
        args.programids,
        n_threads=args.n_threads,
        low_memory=args.low_memory,
        low_memory_format=args.output_format,
        low_memory_dir=args.output_directory,
        format=args.output_format,
    )
    if err or candidates is None:
        print(err)
        return

    # GET CANDIDATES FROM SKYPORTAL
    print("Getting candidates from SkyPortal using the following filters:")
    print(args.filterids)
    print("Getting candidates from SkyPortal using the following groupIDs:")
    print(args.groupids)
    candids_per_filter, err = get_candids_per_filter_from_skyportal(
        args.start, args.end, args.groupids, args.filterids, saved=False
    )
    if err or candids_per_filter is None:
        print(err)
        return

    # ADD PASSED FILTERS TO CANDIDATES
    candidates["passed_filters"] = [[] for _ in range(len(candidates))]
    for filterID, candids in candids_per_filter.items():
        try:
            idx = candidates[candidates["candid"].isin(candids)].index
            candidates.loc[idx, "passed_filters"] = candidates.loc[
                idx, "passed_filters"
            ].apply(lambda x: x + [filterID])
        except KeyError:
            print(f"Candid {candids} not found in candidates dataframe, skipping...")
            continue

    # SAVE CANDIDATES TO DISK
    filename = f"{args.start}_{args.end}_{'_'.join(map(str, args.programids))}"
    filepath = save_dataframe(
        df=candidates,
        filename=filename,
        output_format=args.output_format,
        output_compression=args.output_compression,
        output_compression_level=args.output_compression_level,
        output_directory=args.output_directory,
    )

    print(f"Saved candidates to {filepath}")
