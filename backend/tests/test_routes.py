def test_health_contract():
    from main import app
    routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    assert "/health" in routes
    assert "/health/live" in routes
    assert "/health/ready" in routes
    assert "/predict" in routes
    assert "/beauty/scan" in routes
