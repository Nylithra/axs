#!/usr/bin/env sh
# TON kurulumu: `ton` komutunu her yerden calisir hale getirir.
#   ./install.sh            -> ~/.local/bin/ton
#   ./install.sh /usr/local/bin

set -e

KOK=$(cd "$(dirname "$0")" && pwd)
HEDEF=${1:-"$HOME/.local/bin"}

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.8 ya da ustu gerekli. Once python3 kur."
  exit 1
fi

SURUM=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || {
  echo "Python 3.8+ gerekli (bulunan: $SURUM)"
  exit 1
}

mkdir -p "$HEDEF"
ln -sf "$KOK/ton" "$HEDEF/ton"
chmod +x "$KOK/ton"

echo "TON kuruldu: $HEDEF/ton  (python $SURUM)"

case ":$PATH:" in
  *":$HEDEF:"*) ;;
  *) echo "Not: $HEDEF PATH'te degil. Su satiri ~/.bashrc dosyana ekle:"
     echo "  export PATH=\"\$PATH:$HEDEF\"" ;;
esac

echo "Deneme: ton -e 'print: merhaba'"
