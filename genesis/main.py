import argparse
import sys
from pathlib import Path

from genesis import Genesis


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="De Genesis workflow orkestrator")
    print(
        """
     _____                      _
    / ____|                    (_)
   | |  __  ___ _ __   ___  ___ _ ___
   | | |_ |/ _ \\ '_ \\ / _ \\/ __| / __|
   | |__| |  __/ | | |  __/\\__ \\ \\__ \\
    \\_____|\\___|_| |_|\\___||___/_|___/
                            MDDE Douane
    """,
        file=sys.stdout,
    )

    parser.add_argument("config_file", help="Locatie van een configuratiebestand")
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="Sla DevOps deployment over"
    )
    args = parser.parse_args()
    genesis = Genesis(file_config=Path(args.config_file))
    genesis.start_processing()
