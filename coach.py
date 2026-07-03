def elite_rating(stats):

    passes = stats.get("passes", 0)
    phases = stats.get("phases", {})
    events = stats.get("phase_events", [])

    score = 50  # base rating

    # ---------------- PASS CONTROL ----------------
    if passes > 120:
        score += 20
    elif passes < 60:
        score -= 15

    # ---------------- BUILD-UP CONTROL ----------------
    if phases.get("progression", 0) > phases.get("build_up", 0):
        score += 10
    else:
        score -= 5

    # ---------------- FINAL THIRD PRESSURE ----------------
    if phases.get("final_third", 0) > 150:
        score += 10

    # ---------------- STRUCTURE ERRORS ----------------
    if len(events) > 6:
        score -= 10

    return max(0, min(100, score))


def generate_coach_report(stats):

    passes = stats.get("passes", 0)
    zones = stats.get("zones", {})
    phases = stats.get("phases", {})
    events = stats.get("phase_events", [])

    attack = zones.get("attack", 0)
    midfield = zones.get("midfield", 0)
    defence = zones.get("defence", 0)

    # ---------------- PLAYSTYLE ----------------
    if passes > 120:
        playstyle = "Possession-based controller"
    elif attack > midfield:
        playstyle = "Aggressive attacking player"
    elif midfield > attack:
        playstyle = "Midfield control player"
    else:
        playstyle = "Balanced counter-attacking player"

    # ---------------- ISSUES ----------------
    issues = []

    if passes < 70:
        issues.append("You rush possession and lose control of build-up")

    if midfield < attack:
        issues.append("You skip midfield progression too often")

    if len(events) > 6:
        issues.append("You lose structure during transitions")

    if phases.get("final_third", 0) < 100:
        issues.append("You struggle to sustain attacking pressure")

    # ---------------- STRENGTHS ----------------
    strengths = []

    if passes > 100:
        strengths.append("Good passing involvement")

    if attack > 120:
        strengths.append("Strong attacking threat")

    if midfield > 120:
        strengths.append("Good midfield engagement")

    if phases.get("progression", 0) > 150:
        strengths.append("Strong build-up progression")

    # ---------------- FIX PLAN (15 WIN SYSTEM FOCUS) ----------------
    fix_plan = [
        "Slow down build-up and complete 3–5 passes before attacking",
        "Avoid sprinting immediately after winning the ball",
        "Play through midfield instead of direct long attacks",
        "Recycle possession when forward options are blocked",
        "Maintain structure before entering final third"
    ]

    # ---------------- TRAINING ----------------
    training = [
        "EA FC build-up play tutorial",
        "how to control midfield EA FC",
        "pro FIFA possession gameplay guide",
        "how to stop rushing attacks EA FC"
    ]

    # ---------------- BIGGEST MISTAKE ----------------
    biggest_mistake = issues[0] if issues else "No major mistake detected"

    return {
        "summary": {
            "playstyle": playstyle,
            "elite_rating": elite_rating(stats),
            "biggest_mistake": biggest_mistake
        },
        "analysis": {
            "issues": issues[:3],
            "strengths": strengths[:3]
        },
        "improvement": {
            "fix_plan": fix_plan,
            "training": training
        }
    }