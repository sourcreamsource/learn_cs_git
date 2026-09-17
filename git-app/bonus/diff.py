# 타입 힌트를 위해 List, Tuple을 불러옴
from typing import List, Tuple


# 두 텍스트 라인 리스트를 비교하여 추가(+), 삭제(-), 공통( ) 줄을 찾아내는 Diff 비교 클래스임
class SimpleDiff:
    # 최장 공통 부분 수열(LCS) 동적 계획법 알고리즘으로 두 줄 목록의 차이를 계산하는 함수임
    @staticmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def compute_diff(
        # 준비한 값으로 이 단계의 작업을 실행함.
        lines1: List[str], lines2: List[str]
    # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
    ) -> List[Tuple[str, str]]:
        # 첫 번째 파일의 줄 수임
        m = len(lines1)
        # 두 번째 파일의 줄 수임
        n = len(lines2)

        # DP 테이블을 담을 빈 목록을 준비함
        dp: List[List[int]] = []
        # 첫 번째 파일 줄 수만큼 행을 만듦
        for row_index in range(m + 1):
            # 한 행을 담을 빈 목록을 준비함
            row: List[int] = []
            # 두 번째 파일 줄 수만큼 0을 넣어 열을 만듦
            for column_index in range(n + 1):
                # 아직 공통 줄 길이를 계산하지 않았으므로 0을 넣음
                row.append(0)
            # 완성한 한 행을 DP 테이블에 추가함
            dp.append(row)

        # LCS 길이를 계산하는 DP 루프임
        for i in range(1, m + 1):
            # 목록의 항목을 하나씩 꺼내 같은 작업을 반복함.
            for j in range(1, n + 1):
                # 줄 내용이 일치하면 대각선 값에 1을 더함
                if lines1[i - 1] == lines2[j - 1]:
                    # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
                    dp[i][j] = dp[i - 1][j - 1] + 1
                # 앞의 조건에 해당하지 않는 나머지 경우를 처리함.
                else:
                    # 일치하지 않으면 위쪽과 왼쪽 값 중 큰 값을 취함
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        # 역추적을 통해 변경 사항(diff 결과)을 수집할 리스트임
        diff_result: List[Tuple[str, str]] = []
        # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
        i = m
        # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
        j = n

        # DP 테이블의 우하단에서 좌상단으로 거슬러 올라감
        while i > 0 or j > 0:
            # 양쪽 줄이 모두 남아있고 내용이 같은 경우 (공통 줄)
            if i > 0 and j > 0 and lines1[i - 1] == lines2[j - 1]:
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                diff_result.append((" ", lines1[i - 1]))
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                i -= 1
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                j -= 1
            # 두 번째 파일에만 존재하는 줄인 경우 (추가된 줄 +)
            elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                diff_result.append(("+", lines2[j - 1]))
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                j -= 1
            # 첫 번째 파일에만 존재하는 줄인 경우 (삭제된 줄 -)
            elif i > 0 and (j == 0 or dp[i][j - 1] < dp[i - 1][j]):
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                diff_result.append(("-", lines1[i - 1]))
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                i -= 1

        # 역추적했으므로 올바른 순서가 되도록 뒤집음
        diff_result.reverse()
        # 최종 diff 목록을 반환함
        return diff_result

    # 두 파일 경로를 전달받아 파일 내용을 읽고 diff 문자열을 생성하는 함수임
    @classmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def diff_files(cls, file1_path: str, file2_path: str) -> str:
        # 첫 번째 파일을 읽음
        with open(file1_path, "r", encoding="utf-8") as f1:
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            lines1 = f1.read().splitlines()

        # 두 번째 파일을 읽음
        with open(file2_path, "r", encoding="utf-8") as f2:
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            lines2 = f2.read().splitlines()

        # diff를 계산함
        diff_entries = cls.compute_diff(lines1, lines2)

        # 표시용 문자열 리스트를 생성함
        output_lines: List[str] = []
        # 목록의 항목을 하나씩 꺼내 같은 작업을 반복함.
        for symbol, line_text in diff_entries:
            # 찾은 항목을 목록 끝에 추가하여 기억함.
            output_lines.append(f"{symbol} {line_text}")

        # 줄바꿈으로 연결하여 반환함
        return "\n".join(output_lines)
