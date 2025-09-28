from fabric import Connection, task

REMOTE_HOST = "209.38.25.194"
REMOTE_USER = "root"
REMOTE_PASSWORD = "Ivurs+9909Zqz"
REMOTE_DIR = "/home/root/autoconv"

@task
def deploy(c):
    c = Connection(
        host=REMOTE_HOST,
        user=REMOTE_USER,
        connect_kwargs={"password": REMOTE_PASSWORD}
    )
    c.run(f"cd {REMOTE_DIR} && git pull")
    c.run(f"cd {REMOTE_DIR}/frontend && npm install")
    c.run(f"cd {REMOTE_DIR}/backend && python -m venv .venv")
    c.run(f"cd {REMOTE_DIR}/backend && source .venv/bin/activate")
    c.run(f"cd {REMOTE_DIR}/backend && pip install -r requirements.txt")
    c.run("sudo systemctl restart autoconv")