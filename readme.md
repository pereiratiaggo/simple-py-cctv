# 🖥️ Ambiente Gráfico Minimalista para CFTV no Ubuntu Server

Este guia cria um **ambiente gráfico mínimo**, sem desktop completo, para rodar uma aplicação OpenCV diretamente no monitor conectado ao servidor — estilo DVR/NVR profissional.

✔ Sem GNOME
✔ Sem XFCE
✔ Sem interface pesada
✔ Inicialização automática
✔ Tela dedicada ao CFTV

---

## ✅ 1. Atualizar o sistema

```bash
sudo apt update
sudo apt upgrade -y
```

---

## ✅ 2. Instalar motor gráfico mínimo

Instala apenas o necessário para exibir aplicações gráficas.

```bash
sudo apt install -y \
xorg \
openbox \
xinit \
x11-xserver-utils \
mesa-utils
```

### O que cada pacote faz

| Pacote     | Função                          |
| ---------- | ------------------------------- |
| xorg       | servidor gráfico                |
| openbox    | gerenciador leve de janelas     |
| xinit      | permite iniciar o X manualmente |
| mesa-utils | aceleração gráfica básica       |

---

## ✅ 3. Dependências necessárias para OpenCV (Qt/XCB)

Evita erro:

```
Could not load Qt platform plugin "xcb"
```

Instale:

```bash
sudo apt install -y \
libxcb-xinerama0 \
libxkbcommon-x11-0 \
libxcb-cursor0 \
libxcb-icccm4 \
libxcb-image0 \
libxcb-keysyms1 \
libxcb-render-util0 \
libxcb-xfixes0 \
libgl1-mesa-glx
```

---

## ✅ 4. Criar script de inicialização do CFTV

```bash
nano ~/start-cctv.sh
```

Conteúdo:

```bash
#!/bin/bash

cd /home/USER/simple-py-cctv
source .venv/bin/activate

python main.py
```

Dar permissão:

```bash
chmod +x ~/start-cctv.sh
```

---

## ✅ 5. Criar sessão gráfica mínima

Arquivo responsável por iniciar o ambiente gráfico.

```bash
nano ~/.xinitrc
```

Conteúdo:

```bash
#!/bin/sh

# desativa economia de energia da tela
xset -dpms
xset s off
xset s noblank

# inicia window manager leve
openbox-session &

# inicia o CFTV
/home/USER/start-cctv.sh
```

---

## ✅ 6. Testar manualmente

No console físico do servidor:

```bash
startx
```

Resultado esperado:

* tela preta
* sem desktop
* aplicação abre direto

---

## ✅ 7. Inicializar automaticamente ao ligar o servidor

Criar serviço systemd:

```bash
sudo nano /etc/systemd/system/cctv.service
```

Conteúdo:

```ini
[Unit]
Description=CCTV Kiosk
After=network.target

[Service]
User=USER
Environment=DISPLAY=:0
TTYPath=/dev/tty1
ExecStart=/usr/bin/startx
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable cctv.service
```

---

## ✅ 8. Reiniciar

```bash
sudo reboot
```

---

## 🎯 Resultado Final

Ao ligar o servidor:

1. Ubuntu Server inicia
2. Xorg sobe automaticamente
3. Nenhum desktop é carregado
4. O monitor abre direto o CFTV

Comportamento equivalente a:

* DVR Linux
* NVR Intelbras
* Hikvision Standalone

---

## 🧠 Dicas Importantes

* Execute o `startx` **apenas no terminal físico**, não via SSH.
* Se necessário, verifique:

```bash
echo $DISPLAY
```

Deve retornar:

```
:0
```

---

## 🚀 Próximos Melhoramentos (Opcional)

* esconder cursor do mouse
* auto recovery se câmera travar
* watchdog de processo
* boot splash personalizado
* modo appliance (igual NVR comercial)

---

# README — Fazer o startx iniciar automaticamente após autologin

## Situação atual

* Servidor liga ✔
* Login automático funciona ✔
* Cai no bash ❌
* Ambiente gráfico não inicia ❌

---

## ✅ 1. Criar/editar o `.profile`

Abra:

```bash
nano ~/.profile
```

---

## ✅ 2. Adicione NO FINAL do arquivo

```bash
# iniciar ambiente gráfico automaticamente
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx
fi
```

Salvar:

```
CTRL + O
ENTER
CTRL + X
```

---

## ✅ 3. Garantir permissões corretas

```bash
chmod +x ~/.profile
```

---

## ✅ 4. Testar sem reiniciar

Saia do usuário:

```bash
exit
```

ou:

```bash
logout
```

Se tudo estiver certo:

👉 o sistema fará login automático novamente
👉 o `startx` abrirá sozinho

---

## ✅ 5. Teste final

Reinicie:

```bash
sudo reboot
```

---

## ✔ Resultado esperado

Boot → Autologin → startx inicia → ambiente gráfico aparece no monitor.

---

## 🔥 Se ainda não abrir

Teste manualmente:

```bash
tty
```

Precisa retornar:

```
/dev/tty1
```

Se retornar outro tty, o startx não será executado.
