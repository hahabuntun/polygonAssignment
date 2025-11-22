def test_balance_of(mock_polygon_client):
    res = mock_polygon_client.balance_of("0x0000000000000000000000000000000000000001")
    assert res["balance_formatted"] == 100
    assert res["success"] is True


def test_token_info(mock_polygon_client):
    res = mock_polygon_client.token_info()
    assert res["symbol"] == "TBY"
    assert res["totalSupply_formatted"] == 1000
    assert res["success"] is True


def test_top_holders(mock_polygon_client):
    holders = mock_polygon_client.get_top_holders(1)
    assert holders == [("0x0000000000000000000000000000000000000001", 100)]


def test_top_holders_with_transactions(mock_polygon_client):
    holders = mock_polygon_client.get_top_holders_with_transactions(1)
    assert holders == [("0x0000000000000000000000000000000000000001", 100, "2025-11-22")]
