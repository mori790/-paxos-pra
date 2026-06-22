from paxos.message import AcceptRequest, Accepted, Prepare
from paxos.node import Acceptor
from paxos.types import NodeId, ProposalNumber, Value

# 同じ proposal number なら受け入れる
def test_accepts_request_with_promised_number() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))

    prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
    )

    promise = acceptor.on_prepare(prepare)

    assert promise is not None
    assert acceptor.promised_number == ProposalNumber(1)

    accept_request = AcceptRequest(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )

    response = acceptor.on_accept_request(accept_request)

    assert isinstance(response, Accepted)
    assert response.acceptor_id == NodeId("A1")
    assert response.proposer_id == NodeId("P1")
    assert response.proposal_number == ProposalNumber(1)
    assert response.value == Value("A")

    assert acceptor.accepted_number == ProposalNumber(1)
    assert acceptor.accepted_value == Value("A")

# 古い proposal number は拒否する
def test_acceptor_rejects_accept_with_old_proposal_number() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))

    prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(5),
    )

    promise = acceptor.on_prepare(prepare)

    assert promise is not None
    assert acceptor.promised_number == ProposalNumber(5)

    old_accept_request = AcceptRequest(
        proposer_id=NodeId("P2"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(3),
        value=Value("B"),
    )

    response = acceptor.on_accept_request(old_accept_request)

    assert response is None

    assert acceptor.promised_number == ProposalNumber(5)
    assert acceptor.accepted_number is None
    assert acceptor.accepted_value is None
    
# より新しい proposal number は受け入れる
def test_acceptor_request_with_higher_proposal_number() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))

    prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
    )

    promise = acceptor.on_prepare(prepare)

    assert promise is not None
    assert acceptor.promised_number == ProposalNumber(1)

    higher_accept_request = AcceptRequest(
        proposer_id=NodeId("P2"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(2),
        value=Value("B"),
    )

    response = acceptor.on_accept_request(higher_accept_request)

    assert isinstance(response, Accepted)
    assert response.proposal_number == ProposalNumber(2)
    assert response.value == Value("B")

    assert acceptor.promised_number == ProposalNumber(2)
    assert acceptor.accepted_number == ProposalNumber(2)
    assert acceptor.accepted_value == Value("B")

# 自分宛てではないメッセージは無視する
def test_acceptor_ignores_accept_request_for_other_acceptor() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))

    accept_request = AcceptRequest(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A2"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )

    response = acceptor.on_accept_request(accept_request)

    assert response is None
    assert acceptor.promised_number is None
    assert acceptor.accepted_number is None
    assert acceptor.accepted_value is None