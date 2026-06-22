Step 1: Prepare / Promise を実装する
Step 2: AcceptRequest / Accepted を実装する
Step 3: Acceptor単体を作る
 - Acceptorが新しい提案にはPromiseする
古い提案は拒否する
受け入れた値を記録する
テスト：
    1. 初めての Prepare には Promise を返す
    2. すでに高い proposal number に Promise していたら、古い Prepare は拒否する
    3. Promise には、過去に accepted した値が含まれる
------------------------------------------------------------------------------
Step 4: 3台Acceptorで多数派判定する
Step 5: Proposerを作る
Step 6: 古いproposalが拒否されるテストを書く
Step 7: safety testを書く
Step 8: メッセージ遅延・欠落をnetwork.pyで表現する