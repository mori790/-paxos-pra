# main.py

from paxos.message import Prepare, Promise, AcceptRequest, Accepted
from paxos.types import NodeId, ProposalNumber, Value


def main() -> None:
    prepare = Prepare(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
    )

    promise = Promise(
        acceptor_id=NodeId("A1"),
        proposer_id=NodeId("P1"),
        proposal_number=ProposalNumber(1),
    )

    accept_request = AcceptRequest(
        proposer_id=NodeId("P1"),
        acceptor_id=NodeId("A1"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )

    accepted = Accepted(
        acceptor_id=NodeId("A1"),
        proposer_id=NodeId("P1"),
        proposal_number=ProposalNumber(1),
        value=Value("A"),
    )

    print(prepare)
    print(promise)
    print(accept_request)
    print(accepted)


if __name__ == "__main__":
    main()