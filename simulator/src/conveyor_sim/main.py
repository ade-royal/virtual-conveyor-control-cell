"""Entry point for the virtual conveyor simulator."""


def startup_message() -> str:
    return "Conveyor simulator initialized"


def main() -> int:
    print(startup_message())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
