import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--cli", action="store_true")
parser.add_argument("-d", "--debug", action="store_true")

# TODO add argument for diaolg
# TODO add argument for wizard mode
# TODO add argument for GUI application

args = parser.parse_args()

if args.cli:
    from CLI.app import CliApplication
    app = CliApplication(args.debug)
    app.run()

# TODO add code to run in dialog mode

# TODO add code to run in applicaion mode
