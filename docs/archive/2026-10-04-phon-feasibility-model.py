# ARCHIVED 2026-10-04 - DO NOT CITE. NO NUMBER BELOW IS PUBLISHABLE.
#
# The feasibility model from the discarded prototype, retained verbatim with
# its errors, because it is the evidence for why that direction was rejected
# and because it records what was assumed rather than what was measured.
#
# Four defects, three of them arithmetic, all verifiable in the code below:
#
#   1. TOTAL_HOR_SEATS = 150. The House of Representatives has 151 seats. The
#      script's own output string prints "151" while the arithmetic uses 150,
#      so it contradicts itself inside one run.
#   2. The summary of this model circulated the day it was written said booth
#      coverage was "below 15%". The script's own output is 1.33%. The number
#      was overstated more than tenfold on the way out of the tool into prose.
#   3. CURRENT_PHON_SEATS = 2. Verified figure is 1, won at the Farrer
#      by-election on 25 May 2026.
#   4. The seat-conversion model is a black box. calculate_seat_conversion_
#      hurdle() is a linear ramp, (primary - 15) * 0.02 below 28% and
#      0.26 + (primary - 28) * 0.045 above it. The constants 15, 28, 0.02,
#      0.26 and 0.045 appear in no cited source. simulate_pathway() does the
#      same with 1 + (primary - 10) * 0.8 and 10 + (primary - 20) * 2.2.
#      A forecast built on invented coefficients returns a hard-edged number
#      like "76 seats in 6 cycles" carrying the authority of arithmetic, when
#      it is the assumptions restated.
#
# The one part worth carrying forward: CORE_TARGET_SEATS gives real 2022 AEC
# division primary votes (Flynn 12.0, Capricornia 14.6, Maranoa 11.8,
# Wright 12.1, Hunter 9.8, Paterson 7.9, Durack 9.6, Hinkler 8.7). Those are
# measurements, not forecasts, and they are the input Chart 02 and Chart 04
# need. They must be verified against AEC before use.
#
# Volunteer figures (2800 active, 4500 members) are unsourced inputs passed in
# by the caller, not findings. The 22% candidate attrition rate is likewise an
# assumption. Neither can be published: AGENTS.md non-negotiables 1 and 2.
#
# Body below is unmodified.

"""
Pauline Hanson's One Nation (PHON) - Federal Government Feasibility Simulation
=============================================================================
This script models the mathematical, geographic, preferential, and logistical
barriers to Pauline Hanson's One Nation (PHON) forming government (or serving
as a senior/junior coalition partner) in the Australian House of Representatives.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math
TOTAL_HOR_SEATS = 150
MAJORITY_THRESHOLD = 76
MINORITY_GOV_VIABLE_LOWER = 70  # Feasible minority baseline with crossbench
CURRENT_PHON_SEATS = 2          # Baseline 2 seats in the House of Representatives

# Historical benchmarks in Australian Federal Election history (1901-2026)
RECORD_SWINGS = {
    "1975_coalition_landslide_2pp": 7.4,   # Fraser post-dismissal (Largest 2PP swing to opposition)
    "1943_curtin_labor_landslide": 6.8,    # Curtin wartime swing
    "1996_howard_coalition_swing": 5.1,    # End of Keating era
    "2022_teal_community_surge": 12.5,   # Hyper-localized seat swings (not national uniform)
    "1998_phon_qld_state_peak": 22.7,     # Queensland State peak (won 11/89 seats)
    "1998_phon_federal_peak": 8.43,       # Federal primary vote peak (won 0 HoR seats)
    "2022_phon_federal_actual": 4.96,     # Primary vote in 2022 federal election
}

# Polling and volunteer ground game requirements
AUSTRALIA_POLLING_BOOTHS = 7050          # Average federal polling places on election day
HOURS_PER_BOOTH = 10                     # 8:00 AM to 6:00 PM
VOLUNTEERS_PER_BOOTH_MIN = 3             # 2 shifts of 1-2 workers to hand out How-to-Vote cards
AEC_NOMINATION_DEPOSIT_PER_SEAT = 2000   # Forfeited if candidate gets < 4% primary vote


@dataclass
class TargetSeat:
    name: str
    state: str
    current_holder: str
    phon_2022_primary: float
    incumbent_primary: float
    runner_up_primary: float
    margin_to_2cp_threshold: float  # Primary gap needed to enter Two-Candidate-Preferred (2CP)

# High-performing sample target seats for PHON (predominantly regional QLD/NSW/Hunter)
CORE_TARGET_SEATS: List[TargetSeat] = [
    TargetSeat("Flynn", "QLD", "LNP", 12.0, 36.8, 33.5, 21.5),
    TargetSeat("Capricornia", "QLD", "LNP", 14.6, 39.4, 28.1, 13.5),
    TargetSeat("Maranoa", "QLD", "LNP", 11.8, 56.4, 15.3, 3.5),   # 2nd place vs Littleproud
    TargetSeat("Wright", "QLD", "LNP", 12.1, 43.1, 25.5, 13.4),
    TargetSeat("Hunter", "NSW", "ALP", 9.8, 40.6, 27.2, 17.4),
    TargetSeat("Paterson", "NSW", "ALP", 7.9, 40.6, 36.8, 28.9),
    TargetSeat("Durack", "WA", "LIB", 9.6, 37.8, 29.2, 19.6),
    TargetSeat("Hinkler", "QLD", "LNP", 8.7, 42.1, 23.3, 14.6),
]


class PreferentialVotingSimulator:
    """
    Simulates the mechanics of Single-Member Preferential Voting (Instant-Runoff)
    used in the Australian House of Representatives.
    """

    @staticmethod
    def calculate_seat_conversion_hurdle(primary_pct: float, geographic_concentration: float) -> float:
        """
        Calculates the probability of winning a single-member seat.
        Under preferential voting:
        1. Party must make top 2 in the distribution of preferences.
        2. Party must harvest preferences from eliminated candidates.
        Unlike PR (Senate), a dispersed 8% primary vote yields 0 HoR seats.
        """
        # Effective primary in target seats when concentrated
        effective_seat_primary = primary_pct * (1.0 + geographic_concentration)

        # In HoR, without reaching ~30% primary, minor parties almost never make 2CP
        # unless preferential flow is overwhelmingly disciplined.
        if effective_seat_primary < 28.0:
            prob = max(0.0, (effective_seat_primary - 15.0) * 0.02)
        else:
            prob = min(0.95, 0.26 + (effective_seat_primary - 28.0) * 0.045)
        return prob


class TrajectoryProjector:
    """
    Projects cumulative election cycles required for PHON to reach
    various seat thresholds in the House of Representatives.
    """

    def __init__(self, current_seats: int = CURRENT_PHON_SEATS, current_nat_primary: float = 4.96):
        self.current_seats = current_seats
        self.current_nat_primary = current_nat_primary

    def simulate_pathway(self, scenario_name: str, annual_swing: float, concentration_factor: float) -> Dict:
        """
        Runs cumulative 3-year federal election cycle projections.
        """
        cycles = 0
        seats = self.current_seats
        primary = self.current_nat_primary
        history = []

        # Maximum of 10 election cycles (30 years)
        while cycles < 10 and seats < MAJORITY_THRESHOLD:
            cycles += 1
            primary += annual_swing

            # Model seat wins above baseline of 2 seats
            if primary < 10.0:
                seats = CURRENT_PHON_SEATS
            elif primary < 20.0:
                seats = CURRENT_PHON_SEATS + int(1 + (primary - 10.0) * 0.8 * concentration_factor)
            elif primary < 30.0:
                seats = int(10 + (primary - 20.0) * 2.2 * concentration_factor)
            elif primary < 40.0:
                seats = int(32 + (primary - 30.0) * 3.8 * concentration_factor)
            else:
                seats = int(70 + (primary - 40.0) * 4.5 * concentration_factor)

            seats = min(TOTAL_HOR_SEATS, max(CURRENT_PHON_SEATS, seats))

            history.append({
                "cycle": cycles,
                "years": cycles * 3,
                "projected_primary": round(primary, 2),
                "estimated_seats": seats,
                "can_form_majority": seats >= MAJORITY_THRESHOLD,
                "can_influence_minority": seats >= 2
            })

            if seats >= MAJORITY_THRESHOLD:
                break

        return {
            "scenario": scenario_name,
            "annual_swing": annual_swing,
            "cycles_to_majority": cycles if seats >= MAJORITY_THRESHOLD else "Never (>30 years)",
            "final_seats": seats,
            "timeline": history
        }


class CoalitionAnalyzer:
    """
    Evaluates realistic right-of-centre coalition permutations.
    """

    @staticmethod
    def evaluate_coalition_scenarios(phon_projected_seats: int) -> List[Dict]:
        """
        Evaluates math under varying seat balances:
        - Liberal / National Coalition (LNP)
        - Clive Palmer (United Australia Party / Trumpet-style minor party)
        - Bob Katter (Katter's Australian Party - KAP)
        - Independent right / conservative crossbench
        """
        # Historical baseline seat distributions
        lnp_baseline_seats = 58  # Typical Coalition floor in opposition/mid-term
        kap_seats = 1            # Kennedy electorate held by Bob Katter
        uap_seats = 0            # UAP historically wins 0 HoR seats (Craig Kelly defeated 2022)
        other_independents = 1    # Conservative-leaning independents

        total_right_bloc = lnp_baseline_seats + phon_projected_seats + kap_seats + uap_seats + other_independents
        can_form_government = total_right_bloc >= MAJORITY_THRESHOLD

        return [
            {
                "coalition_name": "LNP + PHON Supply & Confidence",
                "partner_seats": {"LNP": lnp_baseline_seats, "PHON": phon_projected_seats, "KAP": kap_seats},
                "total_seats": total_right_bloc,
                "majority_achieved": can_form_government,
                "phon_role": "Kingmaker (Junior Supply/Crossbench)" if can_form_government else "Insufficient Numbers",
                "stability_rating": "Fragile - High ideological friction on trade/foreign ownership with Libs"
            },
            {
                "coalition_name": "Populist Right Alliance (PHON + KAP + Minor Right)",
                "partner_seats": {"PHON": phon_projected_seats, "KAP": kap_seats, "UAP/Palmer": uap_seats},
                "total_seats": phon_projected_seats + kap_seats + uap_seats,
                "majority_achieved": (phon_projected_seats + kap_seats + uap_seats) >= MAJORITY_THRESHOLD,
                "phon_role": "Dominant Partner",
                "stability_rating": "Impossible without LNP (Seats well below 76)"
            }
        ]


class LogisticsAuditor:
    """
    Audits the organizational capacity: volunteers, candidates, and finances
    required to run a credible national campaign across all 151 electorates.
    """

    @staticmethod
    def audit_resources(estimated_volunteers: int, estimated_members: int, verified_candidates: int) -> Dict:
        # Polling booth coverage analysis
        total_shifts_needed = AUSTRALIA_POLLING_BOOTHS * VOLUNTEERS_PER_BOOTH_MIN
        coverage_pct = min(100.0, (estimated_volunteers / total_shifts_needed) * 100)

        # Nomination deposit calculations
        total_deposit_cost = verified_candidates * AEC_NOMINATION_DEPOSIT_PER_SEAT

        # Candidate attrition rate (historical PHON rate of disendorsement/resignation)
        historical_attrition_rate = 0.22  # ~22% of candidates historically disendorsed/quit mid-campaign

        return {
            "booth_coverage_pct": round(coverage_pct, 2),
            "booth_volunteer_deficit": max(0, total_shifts_needed - estimated_volunteers),
            "total_shifts_needed": total_shifts_needed,
            "estimated_available_volunteers": estimated_volunteers,
            "estimated_party_membership": estimated_members,
            "candidate_slate_count": verified_candidates,
            "candidates_needed_full_slate": TOTAL_HOR_SEATS,
            "candidate_deficit": max(0, TOTAL_HOR_SEATS - verified_candidates),
            "expected_candidate_fallout": int(verified_candidates * historical_attrition_rate),
            "nomination_deposits_aud": total_deposit_cost,
            "viability_flag": "Severely Constrained" if coverage_pct < 25.0 else "Functionally Viable"
        }


def print_separator(char="=", length=80):
    print(char * length)

def run_comprehensive_analysis():
    print_separator()
    print(" PAULINE HANSON'S ONE NATION (PHON) - 'ALTERNATIVE GOVERNMENT' FEASIBILITY")
    print(" Australian Federal House of Representatives Electoral Modeling")
    print_separator()

    # 1. Baseline Electoral Architecture
    print("\n1. BASELINE CONSTITUTIONAL REALITY")
    print(f" - Total Lower House Seats: {TOTAL_HOR_SEATS}")
    print(f" - Absolute Majority Required: {MAJORITY_THRESHOLD} seats")
    print(f" - Current PHON Lower House Seats: {CURRENT_PHON_SEATS} seats")
    print(f" - 2022 Federal PHON Primary Vote: {RECORD_SWINGS['2022_phon_federal_actual']}%")
    print(f" - All-time Record Federal 2PP Swing: {RECORD_SWINGS['1975_coalition_landslide_2pp']}% (Fraser, 1975)")

    # 2. Cycle Projections
    print("\n2. ELECTION CYCLE PROJECTIONS (Cumulative Swings to reach 76 seats)")
    projector = TrajectoryProjector()

    scenarios = [
        ("Moderate Realist (+1.5% primary/cycle)", 1.5, 1.2),
        ("Historic Optimist (+4.5% primary/cycle)", 4.5, 1.4),
        ("Unprecedented Populist Tsunami (+8.0% primary/cycle)", 8.0, 1.6)
    ]

    for title, swing, conc in scenarios:
        res = projector.simulate_pathway(title, swing, conc)
        print(f"\n   Scenario: {res['scenario']}")
        print(f"   Outcome: Reaches 76 seats in: {res['cycles_to_majority']} cycles")
        print("   " + "-" * 70)
        print(f"   {'Cycle':<7} | {'Years':<7} | {'Primary %':<12} | {'HoR Seats Won':<15} | {'Kingmaker Viable'}")
        print("   " + "-" * 70)
        for step in res['timeline'][:5]:  # Show first 5 cycles (15 years)
            print(f"   {step['cycle']:<7} | {step['years']:<7} | {step['projected_primary']:<12}% | {step['estimated_seats']:<15} | {step['can_influence_minority']}")

    # 3. Coalition Math & Edge Cases
    print("\n3. COALITION & KINGMAKER MATHEMATICS (Junior vs Senior Alternative)")
    coalition_sims = CoalitionAnalyzer.evaluate_coalition_scenarios(phon_projected_seats=6)
    for c in coalition_sims:
        print(f"\n   Option: {c['coalition_name']}")
        print(f"   Seat Breakdown: {c['partner_seats']}")
        print(f"   Total Bloc Seats: {c['total_seats']} / 151 (Majority: {c['majority_achieved']})")
        print(f"   Feasibility & Dynamics: {c['stability_rating']}")

    # 4. Grassroots Logistics & Ground Game Audit
    print("\n4. LOGISTICS, CANDIDATES, AND GRASSROOTS AUDIT")
    # Realistic PHON estimates based on AEC filings and party disclosures:
    # ~3,000-5,000 party members nationally; ~2,500 active booth volunteers on election day.
    audit = LogisticsAuditor.audit_resources(
        estimated_volunteers=2800,
        estimated_members=4500,
        verified_candidates=151  # Running in all seats
    )

    print(f" - Polling Booths Nationally: {AUSTRALIA_POLLING_BOOTHS}")
    print(f" - Total Booth Volunteer Shifts Needed: {audit['total_shifts_needed']:,}")
    print(f" - Estimated Available PHON Volunteers: {audit['estimated_available_volunteers']:,}")
    print(f" - National Booth Coverage Rate: {audit['booth_coverage_pct']}%")
    print(f" - Volunteer Deficit: {audit['booth_volunteer_deficit']:,} volunteers")
    print(f" - Slate Size: {audit['candidate_slate_count']} seats contested")
    print(f" - Expected Candidate Attrition/Disendorsements: ~{audit['expected_candidate_fallout']} candidates")
    print(f" - AEC Nomination Deposits Required: ${audit['nomination_deposits_aud']:,}")
    print(f" - Ground Viability Status: {audit['viability_flag']}")

    # 5. Executive Synthesis
    print("\n5. MATHEMATICAL & STRATEGIC CONCLUSION")
    print("""
 - Outright Government (76 seats): Mathematically near-zero probability.
   Single-Member Preferential voting punishes broad, shallow support. PHON's vote
   is dispersed across regional Queensland, NSW, and WA. To convert that to 76 seats
   would require sustained primary swings larger than any observed in Australian
   federation history over 4 to 6 consecutive cycles (>15-20 years).

 - Real-world 'Impact' Ceiling: 
   The only mathematically plausible avenue for PHON to influence government is as
   a crossbench or junior coalition partner (winning 2-5 regional QLD seats like
   Flynn, Capricornia, or Wright). However, formal coalition with the Liberal-National
   party is severely constrained by urban moderate Liberal friction and differing
   stances on economic policy, foreign investment, and parliamentary discipline.
""")
    print_separator()

if __name__ == "__main__":
    run_comprehensive_analysis()