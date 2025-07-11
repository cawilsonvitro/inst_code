import venv #type:ignore
import os
#requires internet
def venv_builder(req = "constraints.txt") -> None:
    lines: list[str]
    req_file:str = req
    with open( req_file, '+r') as f:
        lines = list(f.readlines())


    stripped_lines: list[str] = []
    stripped: str = ""
    cwd = os.getcwd()

    for line in lines:
        stripped = line.strip()
        if "delcom" in stripped:
            stripped = "delcom @ file:///" + os.path.join(cwd,"delcom-0.1.1-py3-none-any.whl")
        if stripped != "":
            stripped_lines.append(stripped)

    with open(req_file, "+w") as f:
        for line in stripped_lines:
            f.write("\n" + line)
            
    venv_path = os.path.join(cwd, '.venv') 

    venv.create(venv_path, with_pip=True, clear=True)

    script = os.path.join(venv_path, 'Scripts')

    py = os.path.join(script, 'python.exe')

    pip = os.path.join(script, 'pip.exe')

    install = f"{py} {pip} install -r constraints.txt"

    os.system(install)