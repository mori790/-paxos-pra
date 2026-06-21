from dataclasses import dataclass
from typing import Optional

from paxos.message import Prepare, Promise, AcceptRequest, Accepted
from paxos.types import NodeId, ProposalNumber, Value

@dataclass
class Acceptor:
    """
    Paxos の Acceptor。

    Acceptor は以下の3つの状態を持つ。

    promised_number:
        これ以上古い proposal number は受け付けない、という約束。

    accepted_number:
        最後に受け入れた proposal number。

    accepted_value:
        最後に受け入れた value。
    """
    
    node_id: NodeId
    promised_number: Optional[ProposalNumber] = None
    accepted_number: Optional[ProposalNumber] = None
    accepted_value: Optional[Value] = None
    
    def on_prepare(self, message: Prepare) -> Optional[Promise]:
        """
        Prepare メッセージを受け取ったときの処理。

        新しい proposal number なら Promise を返す。
        古い proposal number なら None を返して拒否する。
        """

        if message.acceptor_id != self.node_id:
            return None
        if self.promised_number is not None:
            if message.proposal_number < self.promised_number:
                return None
        
        self.promised_number = message.proposal_number
        
        return Promise(
            acceptor_id=self.node_id,
            proposer_id=message.proposer_id,
            proposal_number=message.proposal_number,
            accepted_number=self.accepted_number,
            accepted_value=self.accepted_value,
        )
    
    def on_accept_request(self, message: AcceptRequest) -> Optional[Accepted]:
        """
        AcceptRequest メッセージを受け取ったときの処理。

        proposal number が promised_number 以上なら受け入れる。
        promised_number より古ければ拒否する。
        """
        
        if message.acceptor_id != self.node_id:
            return None
        
        if self.promised_number is not None:
            if message.proposal_number < self.promised_number:
                return None
            
        self.promised_number = message.proposal_number
        self.accepted_number = message.proposal_number
        self.accepted_value = message.value
        
        return Accepted(
            acceptor_id=self.node_id,
            proposer_id=message.proposer_id,
            proposal_number=message.proposal_number,
            value=message.value,
        )