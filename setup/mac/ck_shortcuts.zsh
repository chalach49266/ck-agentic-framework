# CK shortcuts. Source this after your existing shell and Conda setup.
_ck_go() { local folder="$1"; shift; cd "$folder" || return; CK_GROKBOT_AUTO=1 claude "$@"; }
cdev() { _ck_go "{{PHD_ROOT}}/Device Fabrication" "$@"; }
cnv() { _ck_go "{{PHD_ROOT}}/NV Compact Magnetometer" "$@"; }
gb() { _ck_go "$HOME/PhD_local" "$@"; }
grokbot() { gb "$@"; }
phd() { cd "$HOME/PhD_local" || return; }
# Keep an activated Conda environment first. Existing PATH entries keep their order.
_ck_path="$HOME/.local/bin"
case ":$PATH:" in *":$_ck_path:"*) ;; *) export PATH="$_ck_path:$PATH" ;; esac
unset _ck_path
