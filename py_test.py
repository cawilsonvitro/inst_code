import os

python = r"install_files\builder\python.exe"
pip = r"install_files\builder\Lib\site-packages\pip\__pip-runner__.py"

os.system(f"{python} {pip}")


os.system(f"{python} {pip} install -r requirements.txt")

delcom = os.path.abspath("install_files/delcom-0.1.1-py3-none-any.whl")
os.system(f"{python} {pip} install {delcom}")
print("pip install complete")