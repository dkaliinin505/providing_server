import os
import sys

print("__name__ is:", __name__)

def main():
    print("Main function is running")
    print("User:", os.geteuid())
    print("Python version:", sys.version)

if __name__ == "__main__":
    print("Script is being run directly")
    main()
