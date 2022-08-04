"""
John Leeds
main.py
7/25/2022

Main file for Type Racer downloader
"""
import downloader as dl

def main():
    downloader = dl.Downloader()
    print(downloader.download("flaneur", 26183))


if __name__ == "__main__":
    main()
