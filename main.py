from app import backup, delta, metadata


def main() -> None:
    """Run Android device backup using USB Debugging.
    """
    # Fetch raw metadata from device & create a datatframe
    metadata.fetch()
    # Calculate delta dataframe for minimal operations
    delta.calculate()
    # Backup session context to handle live render enter and exit
    with backup.session() as bkp:
        # Run the backup
        bkp.run(mock=False)
    # Check if delta size exceed 1.0 GB
    if delta.size() >= 1_000_000_000:
        # if yes, create archive for online backup and merge delta with main backup dir
        delta.archive()
        delta.merge()
    else:
        # else simply clean up the data dir of the repository
        delta.cleanup(delete_df=True)


if __name__ == "__main__":
    main()
    