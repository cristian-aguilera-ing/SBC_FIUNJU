{ pkgs, ... }: {
  # Usamos una versión estable reciente de NixOS
  channel = "stable-23.11";

  # 1. Paquetes necesarios para tu backend (Python) y frontend (Node)
  packages = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.virtualenv
    pkgs.nodejs_20
    # Herramientas para compilar librerías de Python (como bcrypt/psycopg2)
    pkgs.gcc
    pkgs.gnumake
    pkgs.postgresql 
    # DOCKER
    pkgs.docker
    pkgs.docker-compose
  ];

  # 2. Variables de entorno
  env = {
    # Para que Python no genere archivos .pyc molestos
    PYTHONDONTWRITEBYTECODE = "1";
    PYTHONUNBUFFERED = "1";
  };

  # 3. Habilitar el servicio de Docker (¡CRUCIAL!)
  services.docker.enable = true;

  idx = {
    # Extensiones útiles para tu stack
    extensions = [
      "ms-python.python"
      "bradlc.vscode-tailwindcss"
      "mtxr.sqltools"
    ];

    workspace = {
      # Comandos al crear el entorno por primera vez
      onCreate = {
        setup-backend = "python3 -m venv backend/venv && source backend/venv/bin/activate && pip install -r backend/requirements.txt";
        setup-frontend = "npm install --prefix frontend";
      };
      # Comandos al reiniciar (Levantar Docker automáticamente)
      onStart = {
        start-docker = "docker-compose up -d";
      };
    };
  };
}