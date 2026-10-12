from conveyor_sim.main import startup_message


def test_startup_message() -> None:
    assert startup_message() == "Conveyor simulator initialized"
