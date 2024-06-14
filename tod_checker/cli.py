"""CLI interface for tod_checker project."""

from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="Check if two transactions are TOD")

    args = parser.parse_args()
    print(args)
