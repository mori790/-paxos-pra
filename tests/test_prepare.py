from paxos.message import Prepare, AcceptRequest, Promise
from paxos.node import Acceptor
from paxos.types import NodeId, ProposalNumber, Value

# 最初の提案は受け付ける
def test_acceptor_promises_first_prepare() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))
    
    prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
    )
    
    response = acceptor.on_prepare(prepare)
    
    assert isinstance(response, Promise)
    assert response.acceptor_id == NodeId("A1")
    assert response.proposer_id == NodeId("P1")
    assert response.proposal_number == ProposalNumber(1)
    assert response.accepted_number is None
    assert response.accepted_value is None
    
    assert acceptor.promised_number == ProposalNumber(1)
    
# 古いリーダーを拒否
def test_acceptor_rejects_old_prepare() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))
    
    first_prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(5),
    )
    
    first_response = acceptor.on_prepare(first_prepare)
    
    assert isinstance(first_response, Promise)
    assert acceptor.promised_number == ProposalNumber(5)
    
    old_response = Prepare(
        proposer_id=NodeId("P2"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(3),
    )
    
    old_response = acceptor.on_prepare(old_response)
    
    assert old_response is None
    assert acceptor.promised_number == ProposalNumber(5)
    
# 新しいproposalなら受け付ける
def test_acceptor_promises_higher_prepare() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))
    
    first_prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
    )
    
    first_response = acceptor.on_prepare(first_prepare)
    
    assert isinstance(first_response, Promise)
    assert acceptor.promised_number == ProposalNumber(1)
    
    higher_prepare = Prepare(
        proposer_id=NodeId("P2"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(2),
    )
    
    higher_response = acceptor.on_prepare(higher_prepare)
    
    assert isinstance(higher_response, Promise)
    assert higher_response.proposal_number == ProposalNumber(2)
    assert acceptor.promised_number == ProposalNumber(2)
    
# 提案せず過去のデータを引き継ぐ
def test_promise_includes_previously_accepted_value() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))
    
    accept_request = AcceptRequest(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )
    
    accepted = acceptor.on_accept_request(accept_request)
    
    assert accepted is not None
    assert acceptor.accepted_number == ProposalNumber(1)
    assert acceptor.accepted_value == Value("A")
    
    prepare = Prepare(
        proposer_id=NodeId("P2"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(2),
    )
    
    response = acceptor.on_prepare(prepare)
    
    assert isinstance(response, Promise)
    assert response.accepted_number == ProposalNumber(1)
    assert response.accepted_value == Value("A")
