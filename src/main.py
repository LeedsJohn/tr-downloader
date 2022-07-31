"""
John Leeds
main.py
7/25/2022

Main file for Type Racer downloader
"""
import downloader as dl
import formatter as fm

def main():
    downloader = dl.Downloader()
    formatter = fm.Formatter()
    text, typingLog = downloader.download("hi_i_am_epic", 1138)
    formatter.format(text, typingLog)


if __name__ == "__main__":
    main()