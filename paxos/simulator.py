from dataclasses import dataclass
from typing import Optional

from paxos.message import AcceptRequest, Accepted, Prepare, Promise
from paxos.node import Acceptor
from paxos.types import NodeId, ProposalNumber, Value

@dataclass
class PaxosResult:
    """
    Paxosの1回の提案結果。

    chosen_value:
        多数派に受け入れられて決定された値。
        失敗した場合は None。

    promises:
        Prepareに対して返ってきたPromise一覧。

    accepted:
        AcceptRequestに対して返ってきたAccepted一覧。
    """

    chosen_value: Optional[Value]
    promises: list[Promise]
    accepted: list[Accepted]

class PaxosSimulator:
    """
    教育用のシンプルなPaxosシミュレータ。

    まずは1つのProposerが、複数のAcceptorに対して
    Prepare -> Promise -> AcceptRequest -> Accepted
    の流れを実行する。
    """

    def __init__(self, acceptors: list[Acceptor]) -> None:
        if len(acceptors) == 0:
            raise ValueError("At least one acceptor is required.")
        
        self.acceptors = acceptors

    @property
    def majority_size(self) -> int:
        """
        多数派に必要な数。

        例:
            3台なら2
            5台なら3
        """
        
        return len(self.acceptors) // 2 + 1
    
    def propose(
            self,
            proposer_id: NodeId,
            proposal_number: ProposalNumber,
            value: Value,
    ) -> PaxosResult:
        """
        1つの値をPaxosで提案する。

        Phase 1:
            Prepareを全Acceptorに送る。
            多数派からPromiseが返ってきたら次へ進む。

        Phase 2:
            AcceptRequestを全Acceptorに送る。
            多数派からAcceptedが返ってきたらchosen。
        """

        promises = self._send_prepare_to_all(
            proposer_id=proposer_id,
            proposal_number=proposal_number,
        )
        # Phase1
        if len(promises) < self.majority_size:
            return PaxosResult(
                chosen_value=None,
                promises=promises,
                accepted=[],
            )
        
        proposed_value = self._select_value_from_promises(
            original_value=value,
            promises=promises,
        )

        accepted = self._send_accept_request_to_all(
            proposer_id=proposer_id,
            proposal_number=proposal_number,
            value=proposed_value,
        )
        # Phase2
        if len(accepted) < self.majority_size:
            return PaxosResult(
                chosen_value=None,
                promises=promises,
                accepted=accepted,
            )
        
        return PaxosResult(
            chosen_value=proposed_value,
            promises=promises,
            accepted=accepted,
        )
    
    def _send_prepare_to_all(
            self,
            proposer_id: NodeId,
            proposal_number: ProposalNumber,
    ) -> list[Promise]:
        promises: list[Promise] = []

        for acceptor in self.acceptors:
            prepare = Prepare(
                proposer_id=proposer_id,
                acceptor_id=acceptor.node_id,
                proposal_number=proposal_number,
            )

            response = acceptor.on_prepare(prepare)

            if response is not None:
                promises.append(response)

        return promises
    
    def _send_accept_request_to_all(
            self,
            proposer_id:NodeId,
            proposal_number: ProposalNumber,
            value: Value,
    ) -> list[Accepted]:
        accepted: list[Accepted] = []

        for acceptor in self.acceptors:
            accept_request = AcceptRequest(
                proposer_id=proposer_id,
                acceptor_id=acceptor.node_id,
                proposal_number=proposal_number,
                value=value,
            )

            response = acceptor.on_accept_request(accept_request)

            if response is not None:
                accepted.append(response)
        
        return accepted
    
    def _select_value_from_promises(
            self,
            original_value: Value,
            promises: list[Promise],
    ) -> Value:
        """
        Promiseの中に過去にacceptedされた値があれば、
        その中で最も大きいaccepted_numberの値を採用する。

        何もacceptedされていなければ、元々提案した値を使う。
        """

        promises_with_accepted_value = [
            promise
            for promise in promises
            if promise.accepted_number is not None
            and promise.accepted_value is not None
        ]

        if len(promises_with_accepted_value) == 0:
            return original_value
        
        latest_promise = max(
            promises_with_accepted_value,
            key=lambda promise: promise.accepted_number, 
        )

        return latest_promise.accepted_value