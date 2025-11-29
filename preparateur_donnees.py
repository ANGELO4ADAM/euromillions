from typing import List, Dict


def nettoyer_tirages(tirages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Nettoie les tirages avant apprentissage.

    Cette fonction est volontairement simple pour conserver une base stable
    tout en laissant la possibilité de l'étendre avec des pipelines plus riches.
    """

    cleaned = []
    for tirage in tirages:
        if "numbers" in tirage and "stars" in tirage:
            cleaned.append(tirage)
    return cleaned
