import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cli", action="store_true")
parser.add_argument("-d", "--debug", action="store_true")
args = parser.parse_args()

if args.cli:
    from CLI.app import CliApplication
    app = CliApplication(args.debug)
