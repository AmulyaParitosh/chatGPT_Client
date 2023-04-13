import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--cli", action="store_true")
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument("-w", "--wizard", action="store_true")

# TODO add argument for diaolg
# TODO add argument for GUI application

args = parser.parse_args()

if args.cli and not args.wizard:
    from CLI.app import CliBot
    app = CliBot(args.debug)
    app.run()

elif args.wizard and args.wizard:
    from CLI.app import CliWizard
    app = CliWizard(args.debug)
    app.run()

# TODO add code to run in dialog mode

# TODO add code to run in applicaion mode
