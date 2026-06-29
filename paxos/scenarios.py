from paxos.message import Prepare, AcceptRequest
from paxos.node import Acceptor
from paxos.simulator import PaxosSimulator
from paxos.types import NodeId, ProposalNumber, Value


def print_acceptor_states(acceptors: list[Acceptor]) -> None:
    print("\nAcceptor states:")
    for acceptor in acceptors:
        print(
            f"{acceptor.node_id}: "
            f"promised={acceptor.promised_number}, "
            f"accepted=({acceptor.accepted_number}, {acceptor.accepted_value})"
        )

def scenario_basic_success() -> None:
    """
    一番シンプルな成功パターン。

    P1 が value A を提案する。
    3台中3台が Promise / Accepted を返す。
    A が chosen になる。
    """

    acceptors = [
        Acceptor(node_id=NodeId("A1")),
        Acceptor(node_id=NodeId("A2")),
        Acceptor(node_id=NodeId("A3")),
    ]
    
    simulator = PaxosSimulator(acceptors)
    
    print("P1 proposes value A with proposal number 1")
    
    result = simulator.propose(
        proposer_id=NodeId("P1"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )
    
    print("\nPromises:")
    for promise in result.promises:
        print(promise)

    print("\nAccepted:")
    for accepted in result.accepted:
        print(accepted)

    print(f"\nChosen value: {result.chosen_value}")

    print_acceptor_states(acceptors)

def scenario_old_proposal_rejected() -> None:
    """
    古い proposal number が拒否される例。

    まず P1 が proposal number 5 で Prepare する。
    その後、P2 が proposal number 3 で Prepare する。
    3 は 5 より古いので拒否される。
    """

    acceptor = Acceptor(node_id=NodeId("A1"))
    
    print("P1 sends Prepare(5) to A1")
    
    prepare_5 = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(5),
    )
    
    promise = acceptor.on_prepare(prepare_5)
    print("A1 response:", promise)

    print("\nP2 sends Prepare(3) to A1")
    print("But A1 already promised proposal number 5")
    
    prepare_3 = Prepare(
        proposer_id=NodeId("P2"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(3),
    )
    
    old_response = acceptor.on_prepare(prepare_3)
    print("A1 response:", old_response)
    print("\nBecause response is None, Prepare(3) was rejected.")
    print_acceptor_states([acceptor])
    
def scenario_value_is_inherited() -> None:
    """
    Paxosの安全性で一番大事な例。

    1. P1 が proposal number 1 で value A を提案する
    2. A が acceptors に受け入れられる
    3. その後、P2 が proposal number 2 で value B を提案する
    4. しかし Promise の中に accepted_value=A が含まれる
    5. P2 は B ではなく A を引き継ぐ
    """

    acceptors = [
        Acceptor(node_id=NodeId("A1")),
        Acceptor(node_id=NodeId("A2")),
        Acceptor(node_id=NodeId("A3")),
    ]

    simulator = PaxosSimulator(acceptors)

    print("Step 1: P1 proposes value A with proposal number 1")
    
    result_1 = simulator.propose(
        proposer_id=NodeId("P1"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )
    
    print(f"Chosen value by P1: {result_1.chosen_value}")
    print_acceptor_states(acceptors)

    print("\nStep 2: P2 tries to propose value B with proposal number 2")
    print("However, acceptors already accepted value A before.")
    
    result_2 = simulator.propose(
        proposer_id=NodeId("P2"),
        proposal_number=ProposalNumber(2),
        value=Value("B"),
    )
    
    print("\nPromises returned to P2:")
    for accepted in result_2.accepted:
        print(accepted)
        
    print(f"\nP2 wanted to propose: B")
    print(f"But chosen value by P2: {result_2.chosen_value}")

    print_acceptor_states(acceptors)