def elite_rating(stats):

    passes = stats.get("passes", 0)
    phases = stats.get("phases", {})
    events = stats.get("phase_events", [])

    score = 50  # base rating

    # ---------------- PASS CONTROL ----------------
    if passes > 100:
        score += 15
    elif passes < 50:
        score -= 10

    # ---------------- PHASE CONTROL ----------------
    if phases.get("progression", 0) > phases.get("build_up", 0):
        score += 10
    else:
        score -= 5

    if phases.get("final_third", 0) > 120:
        score += 10

    # ---------------- ERROR PENALTY ----------------
    if events.count("fast_transition") > 5:
        score -= 10

    return max(0, min(100, score))


def generate_coach_report(stats):

    passes = stats.get("passes", 0)
    zones = stats.get("zones", {})
    positions = stats.get("positions", 0)
    balls = stats.get("balls", 0)

    phases = stats.get("phases", {})
    events = stats.get("phase_events", [])

    attack = zones.get("attack", 0)
    midfield = zones.get("midfield", 0)
    defence = zones.get("defence", 0)

    # ---------------- PLAYSTYLE ----------------
    if phases.get("progression", 0) > phases.get("build_up", 0):
        playstyle = "Direct progression-based player"
    elif phases.get("build_up", 0) > phases.get("final_third", 0):
        playstyle = "Controlled possession build-up player"
    elif attack > midfield:
        playstyle = "Aggressive attacking player"
    else:
        playstyle = "Balanced / defensive counter player"

    # ---------------- ISSUES ----------------
    issues = []

    if passes < 60:
        issues.append("You rush play and avoid structured build-up")

    if midfield < attack:
        issues.append("You skip midfield control and force attacks too early")

    if phases.get("final_third", 0) < 80:
        issues.append("You struggle to sustain pressure in attacking areas")

    if events.count("fast_transition") > 5:
        issues.append("You rely too heavily on fast transitions instead of control")

    if len(events) > 0:
        issues.append("Your game has inconsistent structural transitions")

    # ---------------- BIGGEST MISTAKE ----------------
    biggest_mistake = issues[0] if len(issues) > 0 else "No major mistake detected"

    # ---------------- STRENGTHS ----------------
    strengths = []

    if attack > 120:
        strengths.append("You generate strong attacking pressure")

    if positions > 5000:
        strengths.append("High involvement in gameplay and movement")

    if midfield > defence:
        strengths.append("Good central engagement and control")

    if phases.get("progression", 0) > 150:
        strengths.append("Strong midfield progression activity")

    # ---------------- FIX PLAN ----------------
    fix_plan = [
        "Force 2–3 controlled passes before attacking",
        "Stop sprinting immediately after winning possession",
        "Play through midfield before final third entries",
        "Recycle possession when forward options are blocked",
        "Delay final pass until structure is stable"
    ]

    # ---------------- TRAINING ----------------
    training = [
        "EA FC build-up play tutorial",
        "how to control midfield EA FC",
        "elite division gameplay analysis",
        "how to stop rushing attacks EA FC"
    ]

    return {
        "playstyle": playstyle,
        "issues": issues[:3],
        "strengths": strengths[:2],
        "fix_plan": fix_plan[:5],
        "training": training,
        "biggest_mistake": biggest_mistake,
        "elite_rating": elite_rating(stats)
    }