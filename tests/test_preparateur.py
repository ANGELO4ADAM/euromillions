from preparateur_donnees import calculate_frequencies, calculate_gaps, prepare_features


def test_frequency_and_gaps_are_computed():
    draws = [
        {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2]},
        {"numbers": [2, 3, 4, 5, 6], "stars": [2, 3]},
        {"numbers": [3, 4, 5, 6, 7], "stars": [3, 4]},
    ]
    profile = {"max_number": 7, "max_star": 4}

    frequencies = calculate_frequencies(draws)
    gaps = calculate_gaps(draws, profile)
    features = prepare_features(profile, draws, window_size=3)

    assert frequencies["numbers"][3] == 3
    assert frequencies["stars"][2] == 2
    assert gaps["numbers"][1] == 2  # 1 is absent from last two draws
    assert gaps["stars"][4] == 0  # 4 appears in last draw
    assert features["windows"]["numbers"]
    assert features["windows"]["stars"]
