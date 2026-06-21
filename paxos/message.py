from dataclasses import dataclass
from typing import Optional

from paxos.types import NodeId, ProposalNumber, Value

@dataclass(frozen=True)
class Prepare:
    """
    Proposer -> Acceptor
    
    Proposer が Acceptor に対して、
    「proposal_numberで提案しても良いですか？」
    と問い合わせるメッセージ。
    """
    
    proposer_id: NodeId
    acceptor_id: NodeId
    proposal_number: ProposalNumber
    
@dataclass(frozen=True)
class Promise:
    """
    Acceptor -> Proposer

    Acceptor が Proposer に対して、
    「その proposal_number 以上の提案なら受け付けます」
    と約束するメッセージ。

    もし過去に受け入れた提案があれば、
    accepted_number と accepted_value に入れて返す。
    """
    
    acceptor_id: NodeId
    proposer_id: NodeId
    proposal_number: ProposalNumber
    accepted_number: Optional[ProposalNumber] = None
    accepted_number: Optional[Value] = None
    
@dataclass(frozen=True)
class AcceptRequest:
    """
    Proposer -> Acceptor

    Proposer が Acceptor に対して、
    「この proposal_number で、この value を受け入れてください」
    と依頼するメッセージ。
    """
    proposer_id: NodeId
    acceptor_id: NodeId
    proposal_number: ProposalNumber
    value: Value

@dataclass(frozen=True)
class Accepted:
    """
    Acceptor -> Proposer / Learner

    Acceptor が、
    「この proposal_number と value を受け入れました」
    と知らせるメッセージ。
    """
    
    acceptor_id: NodeId
    proposer_id: NodeId
    proposal_number: ProposalNumber
    value: Value