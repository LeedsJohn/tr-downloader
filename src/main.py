"""
John Leeds
main.py
7/25/2022

Main file for Type Racer downloader
"""
import downloader as dl

def main():
    downloader = dl.Downloader()
    downloader.download("nothisisjohn", 14900, 15023)


if __name__ == "__main__":
    main()
