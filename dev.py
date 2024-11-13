import subprocess
from argparse import ArgumentParser
from subprocess import SubprocessError


def run_subprocess(command: list[str]) -> None:
    print(f"Running... '{subprocess.list2cmdline(command)}'")
    result = subprocess.run(args=command, capture_output=True)
    if result.returncode == 0:
        print(result.stdout.decode("utf-8"))
    else:
        raise SubprocessError(result.stderr.decode("utf-8"))


def lint(args: list[str]) -> None:
    run_subprocess(["ruff", "check", "ninja_taisen", "tests", "analysis"] + args)
    run_subprocess(["mypy", "ninja_taisen", "tests", "analysis", "--install-types", "--non-interactive"] + args)


def format(args: list[str]) -> None:
    run_subprocess(["black", "ninja_taisen", "tests", "analysis"] + args)
    run_subprocess(["ruff", "check", "ninja_taisen", "tests", "analysis", "--fix", "--unsafe-fixes"] + args)


def test(args: list[str]) -> None:
    run_subprocess(["pytest", "tests"] + args)


def regen(args: list[str]) -> None:
    run_subprocess(["pytest", "tests/regression", "--regen"] + args)


def check(args: list[str]) -> None:
    format(args)
    lint(args)
    test(args)


def yeehaw(args: list[str]) -> None:
    check([])
    run_subprocess(["git", "add", "."])
    run_subprocess(["git", "commit", "-m"] + args)
    run_subprocess(["git", "push", "-u"])


def run() -> None:
    parser = ArgumentParser()
    parser.add_argument("mode", choices=("lint", "format", "test", "regen", "check", "yeehaw"))
    args, remainder = parser.parse_known_args()
    remainder = list(remainder)

    if args.mode == "lint":
        lint(remainder)
    elif args.mode == "format":
        format(remainder)
    elif args.mode == "test":
        test(remainder)
    elif args.mode == "regen":
        regen(remainder)
    elif args.mode == "check":
        check(remainder)
    elif args.mode == "yeehaw":
        yeehaw(remainder)
    else:
        raise ValueError(f"Unexpected mode {args.mode}")


if __name__ == "__main__":
    run()
