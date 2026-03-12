from src.rescue_ai import RescueCoordinator, VictimSignal


def test_priority_stack_orders_most_critical_first():
    coordinator = RescueCoordinator()
    victims = [
        VictimSignal("A", (3, 3), 0.2, 0.9, 0.8, 0.1, 80),
        VictimSignal("B", (1, 1), 0.9, 0.2, 0.1, 0.8, 20),
        VictimSignal("C", (2, 2), 0.6, 0.6, 0.5, 0.4, 45),
    ]
    risk_grid = [
        [0.1, 0.2, 0.2, 0.1],
        [0.1, 0.9, 0.3, 0.1],
        [0.1, 0.3, 0.4, 0.1],
        [0.1, 0.1, 0.1, 0.1],
    ]
    entries = [(0, 0), (3, 0), (0, 3)]

    result = coordinator.process_incident("drone-live", victims, risk_grid, entries)

    assert result["victim_priority_stack"][0]["victim_id"] == "B"
    assert len(result["recommended_entry_points"]) >= 1
    assert "avg_rescue_cost" in result["recommended_entry_points"][0]
