import subprocess, os

def get_etcd_key(key):
    host = os.getenv('ETCD_HOST')
    port = os.getenv('ETCD_PORT')
    username = os.getenv('ETCD_USERNAME')
    password = os.getenv('ETCD_PASSWORD')

    print(f"Connecting to etcd at {host}:{port} with user {username} and password {password}")

    command = f'etcdctl --endpoints=http://{host}:{port} --user={username}:{password} get {key}'

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return result.stdout.decode('utf-8').split('\n')[0] if result.stdout else None
