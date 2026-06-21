# main.py

from paxos.message import Prepare, AcceptRequest
from paxos.node import Acceptor
from paxos.types import NodeId, ProposalNumber, Value


def main() -> None:
    acceptor = Acceptor(node_id=NodeId("A1"))

    prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
    )

    promise = acceptor.on_prepare(prepare)
    print("Promise:", promise)

    accept_request = AcceptRequest(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )

    accepted = acceptor.on_accept_request(accept_request)
    print("Accepted:", accepted)

    old_prepare = Prepare(
        proposer_id=NodeId("P2"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(0),
    )

    old_promise = acceptor.on_prepare(old_prepare)
    print("Old Promise:", old_promise)

    print("Acceptor state:", acceptor)


if __name__ == "__main__":
    main()