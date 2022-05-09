import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-ip", default=os.environ.get("STELLA_LOCAL_IP", ""))
    parser.add_argument("--local-port", default=os.environ.get("STELLA_LOCAL_PORT", "8888"))

    args = parser.parse_args()
