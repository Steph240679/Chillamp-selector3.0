from presets import presets

def compare_elements(user_choice, target_choice):
    return user_choice.strip().lower() == target_choice.strip().lower()

def compute_fidelity_score(preset, user_basse, user_ampli, user_baffle, user_effets):
    score = 0
    total = 4  # basse, ampli, baffle, effets

    if compare_elements(user_basse, preset['basse']):
        score += 1
    if compare_elements(user_ampli, preset['ampli']):
        score += 1
    if compare_elements(user_baffle, preset['baffle']):
        score += 1

    matching_effects = len(set([e.lower() for e in user_effets]) & set([e.lower() for e in preset['effets']]))
    score += matching_effects / max(len(preset['effets']), 1)  # pondéré

    return round((score / total) * 100)

def get_presets_for_combination(bassiste_nom, user_basse, user_ampli, user_baffle, user_effets):
    matching_presets = [p for p in presets if p['nom'].strip().lower() == bassiste_nom.strip().lower()]
    if not matching_presets:
        return {
            "error": f"Aucun preset trouvé pour le bassiste '{bassiste_nom}'."
        }

    preset = matching_presets[0]
    score = compute_fidelity_score(preset, user_basse, user_ampli, user_baffle, user_effets)

    # Message en fonction du score
    if score == 100:
        message = "Configuration idéale : votre matériel correspond exactement à celui du bassiste."
    elif score >= 75:
        message = "Très bonne correspondance. Quelques ajustements mineurs suffisent."
    elif score >= 50:
        message = "Correspondance partielle. Le rendu sera proche mais pas exact."
    else:
        message = "Le matériel sélectionné est éloigné de celui du bassiste. Attendez-vous à un son différent."

    # On adapte les réglages à partir de ceux du bassiste mais sans les modifier ici
    return {
        "bassiste": preset["nom"],
        "description": preset["description"],
        "mot_cle": preset["mot_cle"],
        "reglages": {
            "basse": user_basse,
            "ampli": user_ampli,
            "baffle": user_baffle,
            "effets": user_effets,
            "reglages_effets": preset["reglages_effets"]
        },
        "score_fidelite": score,
        "message": message
    }

