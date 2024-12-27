from app import delta, metadata


def main() -> None:
    """Run Android device backup using USB Debugging.
    """
    # Fetch raw metadata from device & create a datatframe
    metadata.fetch()
    # Calculate delta dataframe for minimal operations
    delta.calculate()

    
if __name__ == "__main__":
    main()
    