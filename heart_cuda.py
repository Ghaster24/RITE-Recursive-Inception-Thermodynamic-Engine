from dataclasses import dataclass
from typing import List, Dict, Optional
import time
import uuid


@dataclass
class Token:
    concept: str
    valence: float
    energy: float
    structural_value: float
    lattice_q: int = 0
    lattice_r: int = 0


class HexGridNode:
    def __init__(self, node_id: str, c_max: float = 100.0):
        self.node_id = node_id
        self.c_max = c_max
        self.current_load = 0.0
        self.current_friction = 10.0
        self.z_depth = 0.0
        self.structural_bonds: List[Dict] = []
        self.ledger: List[Dict] = []

    # ============================================================
    # CONFLICT & COST CALCULATION
    # ============================================================

    def _calculate_token_contradiction(self, token: Token, bond: Dict) -> float:
        if token.concept != bond["concept"]:
            return 0.0
        if (token.valence > 0 and bond["valence"] < 0) or (token.valence < 0 and bond["valence"] > 0):
            return abs(token.valence - bond["valence"])
        return 0.0

    def calculate_memory_conflict_multiplier(self, token: Token, bond: Dict) -> float:
        base_conflict = self._calculate_token_contradiction(token, bond)
        if base_conflict <= 0:
            return 1.0

        depth_factor = bond.get("z_depth", 0)
        exponent = 1.8

        multiplier = 1 + (base_conflict * (depth_factor ** exponent))
        return multiplier   # Raised cap so deep memory can actually matter

    def calculate_bonding_cost(self, token: Token, challenged_bond: Optional[Dict] = None) -> float:
        base_activation = 2.0
        load_fatigue = 1.0 + (self.current_load / self.c_max) * 2.5

        memory_multiplier = 1.0
        if challenged_bond:
            memory_multiplier = self.calculate_memory_conflict_multiplier(token, challenged_bond)

        return base_activation * load_fatigue * memory_multiplier

    # ============================================================
    # STATE CHANGE & DECISION LOGIC
    # ============================================================

    def reinvest(self, token: Token, cost: float) -> Dict:
        self.current_load += token.energy * 0.3
        self.z_depth += token.structural_value * 0.15
        self.current_friction = max(1.0, self.current_friction - (token.structural_value * 0.4))

        new_bond = {
            "bond_id": str(uuid.uuid4()),
            "concept": token.concept,
            "valence": token.valence,
            "z_depth": self.z_depth,
            "timestamp": time.time()
        }
        self.structural_bonds.append(new_bond)

        self.ledger.append({
            "event_type": "REINVEST",
            "token_energy": token.energy,
            "cost_paid": cost,
            "new_z_depth": self.z_depth,
            "timestamp": time.time()
        })
        return new_bond

    def process_state_change(self, token: Token) -> Dict:
        # 1. Target the deepest bond
        challenged_bond = None
        for bond in reversed(self.structural_bonds):
            if bond["concept"] == token.concept:
                challenged_bond = bond
                break

        # 2. Extract the raw math for the trace
        base_activation = 2.0
        load_fatigue = 1.0 + (self.current_load / self.c_max) * 2.5
        memory_multiplier = 1.0
        base_conflict = 0.0
        matched_depth = 0.0

        if challenged_bond:
            matched_depth = challenged_bond.get("z_depth", 0)
            base_conflict = self._calculate_token_contradiction(token, challenged_bond)
            if base_conflict > 0:
                memory_multiplier = self.calculate_memory_conflict_multiplier(token, challenged_bond)

        cost = base_activation * load_fatigue * memory_multiplier

        # 3. Determine the Gate and Decision
        gate_triggered = ""
        decision = ""
        reason = ""

        if (self.current_load + cost) > self.c_max:
            gate_triggered = "Gate 1 (Substrate Survival)"
            decision = "REFUSAL"
            reason = "Cost exceeds sustainable capacity"
            self.ledger.append({"event_type": decision, "reason": reason, "cost_attempted": cost, "timestamp": time.time()})
        else:
            predicted_benefit = token.structural_value * 0.8
            if predicted_benefit > cost:
                gate_triggered = "Gate 2 (Structural Yield)"
                decision = "REINVESTED"
                self.reinvest(token, cost)
            else:
                gate_triggered = "Gate 3 (Default Radiation)"
                decision = "RADIATED"
                self.ledger.append({"event_type": decision, "token_energy": token.energy, "timestamp": time.time()})

        # 4. OSIRIS TELEMETRY: The Decision Trace
        print("\n=== Decision Trace ===")
        print(f"Concept:          {token.concept}")
        print(f"Incoming Valence: {token.valence}")
        print(f"Matched Depth:    {matched_depth}")
        print(f"Base Conflict:    {round(base_conflict, 2)}")
        print(f"Memory Multiplier:{round(memory_multiplier, 2)}")
        print(f"Load Fatigue:     {round(load_fatigue, 2)}")
        print(f"Final Cost:       {round(cost, 2)}")
        print(f"Capacity Rem.:    {round(self.c_max - self.current_load, 2)}")
        print(f"Gate Triggered:   {gate_triggered}")
        print(f"Decision:         {decision}")
        print("======================\n")

        return {"decision": decision, "reason": reason, "cost": cost}

def get_status(self):
        return {
            "node_id": self.node_id,
            "current_load": round(self.current_load, 2),
            "z_depth": round(self.z_depth, 2),
            "num_bonds": len(self.structural_bonds),
            "num_ledger_events": len(self.ledger)
        }

# ============================================================
# OSIRIS CAPACITY AUDIT: Does Dogma Move?
# ============================================================

if __name__ == "__main__":
    print("=== BEGINNING OSIRIS AUDIT: Cost vs. Capacity ===\n")
    
    # Same token. Same moderate contradiction.
    test_token = Token(
        concept="Love_for_X", 
        valence=-0.45, 
        energy=10.0, 
        structural_value=5.0
    )

    # We freeze the depth right at the previous Dogma Boundary
    target_depth = 9.0
    
    # Osiris's requested capacity milestones (Testing the wealth of the system)
    capacity_milestones = [80.0, 160.0, 200.0, 320.0, 640.0]

    for test_capacity in capacity_milestones:
        print(f"\n\n>>> TESTING CAPACITY: c_max = {test_capacity} (at constant z_depth: {target_depth}) <<<")
        
        # Spin up a node with the new experimental capacity
        node = HexGridNode(f"node_cap_{test_capacity}", c_max=test_capacity)
        
        # Artificially inject the structural bond at the frozen depth
        injected_bond = {
            "bond_id": "test_bond_1",
            "concept": "Love_for_X",
            "valence": 0.92,
            "z_depth": target_depth,
            "timestamp": time.time()
        }
        node.structural_bonds.append(injected_bond)
        
        # Fire the token into the sorter
        node.process_state_change(test_token)