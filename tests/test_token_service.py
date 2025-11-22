def test_get_balance(token_service):
    res = token_service.get_balance("0x0000000000000000000000000000000000000001")
    assert res["balance_formatted"] == 100
    assert res["success"] is True


def test_get_balance_batch(token_service):
    addresses = [
        "0x0000000000000000000000000000000000000001",
        "0x0000000000000000000000000000000000000002"
    ]
    results = token_service.get_balance_batch(addresses)
    assert results[0]["balance_formatted"] == 100
    assert results[1]["balance_formatted"] == 200


def test_get_token_info(token_service):
    info = token_service.get_token_info()
    assert info["symbol"] == "TBY"
    assert info["totalSupply_formatted"] == 1000


def test_get_top_holders(token_service):
    holders = token_service.get_top_holders(1)
    assert holders == [("0x0000000000000000000000000000000000000001", 100)]


def test_get_top_holders_with_transactions(token_service):
    holders = token_service.get_top_holders_with_transactions(1)
    assert holders == [("0x0000000000000000000000000000000000000001", 100, "2025-11-22")]
