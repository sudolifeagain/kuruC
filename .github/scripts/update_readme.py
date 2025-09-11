import re
import os
from pathlib import Path
import subprocess

# === 設定項目 ===
SRC_DIR = Path("src")          # コメントを収集するディレクトリ
README = Path("README.md")     # 更新対象のREADME
GITHUB_REPO = "your-username/your-repo"  # <OWNER>/<REPO> に置き換えてください
BRANCH = "main"                # 対象ブランチ名

# Gitのルートディレクトリを取得
def get_git_root():
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True
    ).stdout.strip()

GIT_ROOT = Path(get_git_root())

def extract_comments(file_path):
    """
    C言語ファイルからコメントを抽出して
    [(行番号, コメント内容)] のリストを返す
    """
    comments = []
    with open(file_path, encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line_strip = line.strip()
            # 行コメント //
            if line_strip.startswith("//"):
                comments.append((idx, line_strip[2:].strip()))
            # ブロックコメント /* */
            else:
                block_comments = re.findall(r"/\*+(.*?)\*/", line_strip)
                for bc in block_comments:
                    comments.append((idx, bc.strip()))
    return comments

def generate_github_link(file_path, line_num):
    """
    GitHub上で対象行を表示するリンクを生成
    """
    relative_path = file_path.relative_to(GIT_ROOT)
    return f"https://github.com/{GITHUB_REPO}/blob/{BRANCH}/{relative_path}#L{line_num}"

def generate_comment_section():
    """
    コメントをMarkdown形式で出力する
    """
    result = []
    for file in SRC_DIR.rglob("*.c"):  # C言語ファイルを対象
        comments = extract_comments(file)
        if comments:
            relative_path = file.relative_to(GIT_ROOT)
            result.append(f"### `{relative_path}`")
            for line_num, comment in comments:
                link = generate_github_link(file, line_num)
                result.append(f"- {comment} ([L{line_num}]({link}))")
            result.append("")  # 空行
    return "\n".join(result)

def update_readme(new_content):
    """
    README.mdの特定セクションを置換
    """
    with open(README, encoding="utf-8") as f:
        readme_content = f.read()

    updated_content = re.sub(
        r"(<!-- COMMENTS:START -->)(.*?)(<!-- COMMENTS:END -->)",
        f"<!-- COMMENTS:START -->\n{new_content}\n<!-- COMMENTS:END -->",
        readme_content,
        flags=re.DOTALL
    )

    with open(README, "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    section = generate_comment_section()
    update_readme(section)
