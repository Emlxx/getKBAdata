# getKBAdata
This repository automatically downloads and processes the monthly FZ8 vehicle registration data published by the [Kraftfahrt-Bundesamt (KBA)](https://www.kba.de/).
It stores the raw .xlsx files and compiles selected values into a single aggregated CSV file for easier analysis.

| File / Folder                        | Description                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| `downloads/`                         | Contains all downloaded monthly FZ8 `.xlsx` files                                          |
| `combined_data.csv`                  | Aggregated CSV file with extracted values from all FZ8 datasets                            |
| `download_file_of_last_month.py`     | Script that downloads the FZ8 file of last month and updates the combined CSV              |
| `download_multiple_files_at_once.py` | Script that downloads **all available FZ8 files since 2023** and rebuilds the combined CSV |

A GitHub Actions workflow runs automatically on the 1st day of each month at 12:00 UTC, downloading the FZ8 dataset of last month and updating combined_data.csv.
