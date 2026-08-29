# AGENT_17: Visual Merkle Proof Tree Diagram & Drawer

## Objective
Build an interactive cryptographic proof visualizer (`frontend/src/components/MerkleTreeVisualizer.tsx`) for the Decision Receipts system that renders a 3-node Merkle proof tree illustrating SHA-256 Merkle root formation and Ed25519 signature binding.

## Deliverables
1. `frontend/src/components/MerkleTreeVisualizer.tsx`:
   - Visual Root Node: SHA-256 Merkle Root with verified checkmark and copy button.
   - Animated SVG connecting branch lines with glowing pulse signals.
   - 3 Cryptographic Leaf Nodes:
     - Leaf 1: Cart State Digest (Items, authoritative prices, subtotal).
     - Leaf 2: Guardian Policy Invariant Digest (Rule 6 cost floor, margin check).
     - Leaf 3: Merchant Ed25519 Signature Digest.
   - 1-Click Replay Verification Status Badge (`MATCH: 100% Zero Drift`).
2. Integrate into `frontend/src/app/(merchant)/receipts/page.tsx` and `frontend/src/app/(merchant)/receipts/[receipt_id]/page.tsx`.

## Acceptance Criteria
- Clicking any decision receipt displays the interactive Merkle Tree diagram.
- Replaying a receipt animates the leaves and proves cryptographic zero-drift integrity.
