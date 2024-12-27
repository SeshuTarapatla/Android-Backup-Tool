from app import metadata


def main() -> None:
    """Run Android device backup using USB Debugging.
    """
    # Fetch raw metadata from device & create a datatframe
    metadata.fetch()

if __name__ == "__main__":
    main()
    