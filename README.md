# nexuscreator-container
NeXusCreator converts experimental data and NeXus definition files into valid NeXus (.nxs) HDF5 files. It also supports generating NeXus-definition templates (.nxd) from input data. A lightweight plugin system powers both generation and parsing for formats like SPEC and DTA/DAT, including a batteries folder workflow.

## Docker setup
```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Run checks
To run all checks specified in `docker-compose.yaml`:
```bash
sudo docker compose up
```

### Format with `black`
```bash
sudo docker compose run format
```

### Lint with `flake8`
```bash
sudo docker compose run format
```

### Check vulnerabilities with `safety`
```bash
sudo docker compose run safety
```

### Test with `pytest`
```bash
sudo docker compose run tests
```

## Local build
```bash
sudo docker build --target=prod --tag=localhost/larch_container:local --load .
```
